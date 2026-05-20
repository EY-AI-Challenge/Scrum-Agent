import { buildPortfolioPrompt, buildSingleProjectPrompt } from "./promptBuilder.js";
import { callOpenRouter, getConfiguredModel } from "./openrouterClient.js";
import { parseModelJsonResponse } from "../utils/jsonParser.js";
import { getMockPortfolioResponse, getMockSingleProjectResponse } from "../mock/mockResponses.js";
import { logEvent } from "../utils/logger.js";

function extractTotalWeeksFromText(text = "") {
  const weekMatches = [...text.matchAll(/\bWeek\s+(\d+)\b/gi)].map((match) => Number(match[1]));
  const durationMatches = [...text.matchAll(/\b(\d+)\s+weeks?\b/gi)].map((match) => Number(match[1]));
  const values = [...weekMatches, ...durationMatches].filter((value) => Number.isFinite(value));
  return values.length > 0 ? Math.max(...values) : null;
}

function inferProjectTotalWeeks(projects) {
  const values = projects
    .map((project) => {
      const structuredText = [
        ...(project.deadlines || []),
        ...(project.milestones || []),
        project.objective,
        project.description
      ].filter(Boolean).join("\n");

      return extractTotalWeeksFromText(structuredText) || extractTotalWeeksFromText(project.raw_text || "");
    })
    .filter((value) => Number.isFinite(value));

  return values.length > 0 ? Math.max(...values) : null;
}

function normalizePlanningOptions(projects, options = {}) {
  if (options.sprint_planning_mode === "manual") {
    const sprintsPerWeek = Math.max(1, Number(options.sprints_per_week || 1));
    const totalWeeks = inferProjectTotalWeeks(projects) || 6;

    return {
      ...options,
      sprints_per_week: sprintsPerWeek,
      inferred_total_weeks: totalWeeks,
      number_of_sprints: Math.max(1, Math.ceil(totalWeeks * sprintsPerWeek)),
      sprint_duration_weeks: 1 / sprintsPerWeek
    };
  }

  return {
    ...options,
    sprint_planning_mode: "auto"
  };
}

export async function generateScrumPlan(payload) {
  const projects = payload.projects || [];
  const teamMembers = payload.team_members || [];
  const options = normalizePlanningOptions(projects, payload.options || {});
  const mode = projects.length === 1 ? "single_project" : "portfolio";
  const model = getConfiguredModel();

  logEvent("Orchestrator", "generateScrumPlan start", {
    mode,
    projects: projects.length,
    team_members: teamMembers.length,
    options,
    model,
    use_mock_ai: process.env.USE_MOCK_AI === "true"
  });

  let data;

  if (process.env.USE_MOCK_AI === "true") {
    logEvent("Orchestrator", "using mock AI response", { mode });
    data = mode === "single_project"
      ? getMockSingleProjectResponse(projects[0], teamMembers, options)
      : getMockPortfolioResponse(projects, teamMembers, options);
  } else {
    const prompt = mode === "single_project"
      ? buildSingleProjectPrompt(projects, teamMembers, options)
      : buildPortfolioPrompt(projects, teamMembers, options);

    logEvent("Orchestrator", "prompt built", {
      mode,
      prompt_length: prompt.length
    });

    const rawModelText = await callOpenRouter(prompt);
    data = parseModelJsonResponse(rawModelText);

    logEvent("Orchestrator", "model response parsed", {
      parse_error: Boolean(data?.parse_error),
      keys: Object.keys(data || {})
    });
  }

  return {
    success: true,
    mode,
    data,
    meta: {
      model,
      number_of_projects: projects.length,
      number_of_team_members: teamMembers.length,
      planning_options: options
    }
  };
}
