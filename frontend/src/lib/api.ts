import type { HealthStatus, Priority, ProjectPlan, TaskStatus, TeamMember, UserStory } from "../types";

const BACKEND_BASE = "http://localhost:3001";

export interface RawPlanResult {
  success: boolean;
  mode: "single_project" | "portfolio";
  data: any;
  meta?: {
    model?: string;
    number_of_projects?: number;
    number_of_team_members?: number;
    planning_options?: {
      sprint_planning_mode?: "auto" | "manual";
      sprints_per_week?: number;
      inferred_total_weeks?: number;
      number_of_sprints?: number;
      sprint_duration_weeks?: number;
    };
  };
  parsed_input?: {
    projects?: any[];
    team_members?: any[];
  };
}

export interface SampleProject {
  key: string;
  filename: string;
  size_bytes: number;
  pdf_url: string;
  text_url: string;
}

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${BACKEND_BASE}/health`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();

  return {
    status: data.status || "ok",
    llm_mode: data.use_mock_ai === false ? "claude" : "mock",
    model: data.model || "OpenRouter",
  };
}

export async function parseTeamUpload(file: File): Promise<TeamMember[]> {
  const text = await file.text();

  return text
    .replace(/\r/g, "")
    .split(/\n\s*\n+/)
    .map((block) => block.split("\n").map((line) => line.trim()).filter(Boolean))
    .filter((lines) => lines.length >= 2)
    .map((lines, index) => {
      const profile = lines.slice(1).join(" ");
      const role = inferRole(profile);

      return {
        id: `member_${index + 1}`,
        name: lines[0],
        role,
        skills: inferSkills(profile, role),
        capacity_hours_per_sprint: 40,
        seniority: inferSeniority(profile),
      };
    });
}

export async function extractPdf(file: File): Promise<{ text: string; filename: string; chars: number }> {
  return {
    text: "",
    filename: file.name,
    chars: 0,
  };
}

export async function listSamples(): Promise<SampleProject[]> {
  return [];
}

export async function fetchSampleText(key: string): Promise<{ key: string; filename: string; text: string; chars: number }> {
  return {
    key,
    filename: key,
    text: "",
    chars: 0,
  };
}

export async function fetchTeamRaw(): Promise<{ text: string; exists: boolean; filename: string }> {
  return {
    text: "",
    exists: false,
    filename: "team_members.txt",
  };
}

export async function generatePlanFromFiles(payload: {
  projectFiles: File[];
  teamFile: File;
  options: {
    sprint_planning_mode: "auto" | "manual";
    sprints_per_week?: number;
  };
}): Promise<RawPlanResult> {
  const formData = new FormData();

  payload.projectFiles.forEach((file) => {
    formData.append("project_pdfs", file);
  });
  formData.append("team_file", payload.teamFile);
  formData.append("options", JSON.stringify(payload.options));

  const res = await fetch(`${BACKEND_BASE}/api/plan/upload`, {
    method: "POST",
    body: formData,
  });

  const result = await res.json();
  if (!res.ok) {
    throw new Error(result?.error?.details || result?.error?.message || "Planning upload failed");
  }

  return result;
}

export async function downloadPlanReport(planResult: RawPlanResult): Promise<void> {
  const res = await fetch(`${BACKEND_BASE}/api/report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(planResult),
  });

  if (!res.ok) {
    const result = await res.json().catch(() => null);
    throw new Error(result?.error?.details || result?.error?.message || "Report generation failed");
  }

  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition") || "";
  const fileName = disposition.match(/filename="(.+)"/)?.[1] || "ai-scrum-agent-report.pdf";
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function toProjectPlan(raw: RawPlanResult): ProjectPlan {
  const parsedTeam = raw.parsed_input?.team_members || [];
  const team = parsedTeam.map(toUiTeamMember);
  const sprintDurationWeeks = raw.meta?.planning_options?.sprint_duration_weeks || 2;

  if (raw.mode === "portfolio") {
    return toPortfolioPlan(raw, team, sprintDurationWeeks);
  }

  const data = raw.data || {};
  const project = raw.parsed_input?.projects?.[0];
  const userStories: UserStory[] = (data.backlog || []).map((story: any, index: number) => (
    toUiStory(story, index, team)
  ));
  const storyMap = new Map<string, UserStory>(userStories.map((story) => [story.id, story]));
  const sprints = (data.sprints || []).map((sprint: any, index: number) => (
    toUiSprint(sprint, index, sprintDurationWeeks, storyMap)
  ));

  return {
    project_name: project?.name || data.project_name || "AI Scrum Plan",
    summary: data.project_summary || "Generated Scrum plan.",
    risks: (data.risks || []).map(formatRisk),
    user_stories: userStories,
    sprints,
    team,
    used_mock: false,
  };
}

function toPortfolioPlan(raw: RawPlanResult, team: TeamMember[], sprintDurationWeeks: number): ProjectPlan {
  const data = raw.data || {};
  const projects = data.projects || [];
  const stories: UserStory[] = projects.map((project: any, index: number) => {
    const storyId = `portfolio_${index + 1}`;
    const assignments = project.assignments || [];
    const assignedCount = assignments.filter((assignment: any) => assignment.assigned_member_name !== "Unassigned").length;

    return {
      id: storyId,
      title: project.project_name || `Project ${index + 1}`,
      as_a: "Portfolio lead",
      i_want: "to review balanced staffing for this project",
      so_that: "the portfolio remains fairly staffed across all project roles",
      acceptance_criteria: [
        `${project.fulfillment_rate_percentage || 0}% fulfillment reviewed`,
        `${assignedCount} assigned role(s) confirmed`,
      ],
      story_points: Math.max(1, Math.ceil((assignments.length || 1) / 2)),
      priority: project.fulfillment_rate_percentage < 60 ? "high" : "medium",
      tasks: assignments.map((assignment: any, assignmentIndex: number) => ({
        id: `${storyId}_task_${assignmentIndex + 1}`,
        title: `${assignment.role_title}: ${assignment.assigned_member_name || "Unassigned"}`,
        description: assignment.summary || "Review this role assignment.",
        estimate_hours: 4,
        assignee_id: findTeamMemberByName(assignment.assigned_member_name, team),
        status: assignment.assigned_member_name === "Unassigned" ? "blocked" : "todo",
      })),
    };
  });

  const maxSprint = Math.max(1, projects.length);
  const storyMap = new Map<string, UserStory>(stories.map((story) => [story.id, story]));
  const sprints = Array.from({ length: maxSprint }, (_, index) => {
    const sprintNumber = index + 1;
    const storyIds = stories[index] ? [stories[index].id] : [];

    return toUiSprint({
      sprint_number: sprintNumber,
      goal: `Review balanced allocation for ${projects[index]?.project_name || `project ${sprintNumber}`}`,
      stories: storyIds,
    }, index, sprintDurationWeeks, storyMap);
  });
  const unassigned = data.allocation_summary?.unassigned_members || [];

  return {
    project_name: "Portfolio Scrum Plan",
    summary: `Assigned ${data.allocation_summary?.total_members_assigned || 0} member(s) across ${projects.length} project(s).`,
    risks: unassigned.length > 0 ? [`Unassigned members: ${unassigned.join(", ")}`] : [],
    user_stories: stories,
    sprints,
    team,
    used_mock: false,
  };
}

function findTeamMemberByName(name: string | undefined, team: TeamMember[]): string | null {
  if (!name || name === "Unassigned") return null;
  return team.find((member) => member.name === name)?.id || null;
}

function toUiTeamMember(member: any): TeamMember {
  return {
    id: member.id,
    name: member.name,
    role: member.role,
    skills: member.skills || [],
    capacity_hours_per_sprint: Math.round((member.availability ?? 1) * 40),
    seniority: member.experience_level || null,
  };
}

function toUiStory(story: any, index: number, team: TeamMember[]): UserStory {
  const id = story.id || `story_${index + 1}`;
  const narrative = parseUserStory(story.user_story || story.description || story.title || "");

  return {
    id,
    title: story.title || `Story ${index + 1}`,
    as_a: narrative.as_a,
    i_want: narrative.i_want,
    so_that: narrative.so_that,
    acceptance_criteria: story.acceptance_criteria || [],
    story_points: Number(story.estimate_points || 3),
    priority: priorityFromText(story.priority),
    tasks: (story.tasks || []).map((task: any, taskIndex: number) => ({
      id: task.id || `${id}_task_${taskIndex + 1}`,
      title: task.title || `Task ${taskIndex + 1}`,
      description: task.description || "",
      estimate_hours: Number(task.estimate_hours || 4),
      assignee_id: findAssigneeId(task.suggested_role, team),
      status: "todo" as TaskStatus,
    })),
  };
}

function toUiSprint(sprint: any, index: number, sprintDurationWeeks: number, storyMap: Map<string, UserStory>) {
  const sprintNumber = Number(sprint.sprint_number || index + 1);
  const start = new Date();
  start.setDate(start.getDate() + index * sprintDurationWeeks * 7);
  const end = new Date(start);
  end.setDate(start.getDate() + sprintDurationWeeks * 7 - 1);
  const explicitStoryIds = sprint.stories || sprint.story_ids || [];
  const storyIds = explicitStoryIds.filter((id: string) => storyMap.has(id));

  return {
    id: `sprint_${sprintNumber}`,
    name: `Sprint ${sprintNumber}`,
    goal: sprint.goal || sprint.priority_focus || `Sprint ${sprintNumber}`,
    start_date: start.toISOString().slice(0, 10),
    end_date: end.toISOString().slice(0, 10),
    story_ids: storyIds,
  };
}

function parseUserStory(text: string) {
  const match = text.match(/As a[n]?\s+(.+?),\s*I want\s+(.+?),\s*so that\s+(.+)\.?$/i);

  if (!match) {
    return {
      as_a: "user",
      i_want: text || "to complete this capability",
      so_that: "the project can deliver value",
    };
  }

  return {
    as_a: match[1],
    i_want: match[2],
    so_that: match[3],
  };
}

function findAssigneeId(role: string | undefined, team: TeamMember[]): string | null {
  if (!role) return null;
  const normalizedRole = role.toLowerCase();
  return team.find((member) => (
    member.role.toLowerCase().includes(normalizedRole) ||
    normalizedRole.includes(member.role.toLowerCase())
  ))?.id || null;
}

function priorityFromText(priority: string | undefined): Priority {
  const normalized = String(priority || "").toLowerCase();
  if (normalized.includes("critical")) return "critical";
  if (normalized.includes("high")) return "high";
  if (normalized.includes("low")) return "low";
  return "medium";
}

function formatRisk(risk: any): string {
  if (typeof risk === "string") return risk;
  return [risk.title || risk.member || "Risk", risk.severity, risk.mitigation || risk.issue || risk.recommendation]
    .filter(Boolean)
    .join(" - ");
}

function inferRole(profile: string): string {
  const firstSentence = profile.split(".")[0] || "";
  return firstSentence.match(/^(.+?)(?:\s+with\s+|\s+specializing\s+|,\s+with\s+)/i)?.[1]?.trim() || "Team Member";
}

function inferSeniority(profile: string): string | null {
  if (/\b(lead|principal)\b/i.test(profile)) return "Lead";
  if (/\bsenior\b/i.test(profile) || /\b[7-9]\s+years\b|\b1[0-9]\s+years\b/i.test(profile)) return "Senior";
  if (/\bjunior\b/i.test(profile) || /\b[0-2]\s+years\b/i.test(profile)) return "Junior";
  return "Mid";
}

function inferSkills(profile: string, fallback: string): string[] {
  const skills = [
    "Agile", "Scrum", "BPMN", "User Stories", "Healthcare", "Banking", "Retail",
    "Java", "Spring Boot", "React", "TypeScript", "Vue.js", "Python",
    "Machine Learning", "MLOps", "Spark", "SQL", "NoSQL", "Figma",
    "AWS", "Azure", "CI/CD", "Docker", "Kubernetes", "GDPR", "Security",
    "Compliance", "Forecasting", "Data Analysis", "Scheduling",
  ].filter((skill) => new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(profile));

  return skills.length > 0 ? skills : [fallback];
}
