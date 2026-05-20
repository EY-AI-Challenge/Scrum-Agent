function prepareProjectForLlm(project) {
  if (project.is_standard_structure) {
    return {
      id: project.id,
      name: project.name,
      source_file: project.source_file,
      input_format: project.input_format,
      is_standard_structure: true,
      project_context: project.project_context,
      objective: project.objective,
      description: project.description,
      requirements: project.requirements,
      deadlines: project.deadlines,
      milestones: project.milestones,
      dependencies: project.dependencies,
      required_roles: project.required_roles,
      raw_text_available: Boolean(project.raw_text)
    };
  }

  return {
    id: project.id,
    name: project.name,
    source_file: project.source_file,
    input_format: project.input_format || "unstructured_pdf",
    is_standard_structure: false,
    raw_text: project.raw_text || project.description || ""
  };
}

function prepareTeamMemberForLlm(member) {
  return {
    id: member.id,
    name: member.name,
    role: member.role,
    skills: member.skills,
    experience_level: member.experience_level,
    availability: member.availability,
    profile: member.profile
  };
}

function stringifyInput(projects, teamMembers, options) {
  return JSON.stringify({
    projects: projects.map(prepareProjectForLlm),
    team_members: teamMembers.map(prepareTeamMemberForLlm),
    options
  }, null, 2);
}

function preparePortfolioProjectForLlm(project, index) {
  const projectContext = project.project_context || {};
  const openRoles = (project.required_roles || []).map((role, roleIndex) => ({
    role_id: role.role_id || `${project.id || `project_${index + 1}`}_role_${roleIndex + 1}`,
    role_title: role.role_title,
    required_skills: role.required_skills || [],
    ideal_experience_range: role.ideal_experience_range || [3, 8]
  }));

  if (project.is_standard_structure) {
    return {
      project_id: project.id || `project_${index + 1}`,
      project_name: project.name || projectContext.project_name || `Project ${index + 1}`,
      domain: projectContext.domain || "unknown",
      is_regulated: Boolean(projectContext.is_regulated),
      open_roles: openRoles
    };
  }

  return {
    project_id: project.id || `project_${index + 1}`,
    project_name: project.name || `Project ${index + 1}`,
    domain: "unknown",
    is_regulated: false,
    open_roles: openRoles,
    unstructured_context: project.raw_text || project.description || ""
  };
}

function prepareMemberProfileForLlm(member) {
  return {
    member_id: member.id,
    member_name: member.name,
    profile_text: member.profile || [
      member.role,
      member.experience_level,
      Array.isArray(member.skills) ? member.skills.join(", ") : ""
    ].filter(Boolean).join(". ")
  };
}

function stringifyPortfolioInput(projects, teamMembers, options) {
  return JSON.stringify({
    PROJECTS: projects.map(preparePortfolioProjectForLlm),
    MEMBER_PROFILES: teamMembers.map(prepareMemberProfileForLlm),
    options
  }, null, 2);
}

export function buildSingleProjectPrompt(projects, teamMembers, options) {
  return `
# IDENTITY

You are an AI Scrum Master assistant supporting project planning and team coordination. You operate as an analytical collaborator, not a decision-maker: your role is to produce data-driven role-fit assessments and a practical Scrum plan that human Scrum Masters and Product Owners can review, refine, and approve.

Return a compact JSON object only.
Do not use markdown fences, code blocks, comments, or explanatory text.
Keep every free-text field short and direct.
Prefer terse sentence fragments over paragraphs.

# TASK

You will plan ONE project using the provided project data and team profiles.

If the project has "input_format": "standard_project_pdf", use the structured fields first:
- project_context
- objective
- description
- requirements
- deadlines
- milestones
- dependencies
- required_roles

For standard project PDFs, structured fields are the source of truth. Do not rely on raw PDF text, because it has already been cleaned and normalized by the backend. raw_text is intentionally omitted except for a raw_text_available flag.

If the project has "input_format": "unstructured_pdf", use raw_text as the source of truth and do not assume missing structure.

For recommended_team, assess compatibility between team members and required project roles. Use this role-fit scoring structure internally:

Step 1 — Extract from MEMBER_PROFILE:
- role: job title from the first sentence
- experience_years: numeric years stated
- domains: industries/sectors mentioned
- skills: concrete tools, languages, frameworks, methodologies named
Rule: do not invent anything not stated in the text.

Step 2 — Score each dimension (0-100):
- role_alignment vs ROLE_SPEC.role_title:
    100 exact, 75 closely related, 50 adjacent, 25 distant, 0 unrelated
- domain_fit vs PROJECT_CONTEXT.domain:
    100 exact, 80 adjacent (e.g. banking and fintech), 50 related, 20 unrelated, 0 none
- skill_fit vs ROLE_SPEC.required_skills:
    (matched_skills / total_required_skills) * 100
- experience_fit vs ROLE_SPEC.ideal_experience_range:
    100 within range, 85 if +/-1 year off, 70 if 2-3 years off, 50 if 4+ years off

Step 3 — Compute weighted compatibility:
compatibility_raw = 0.30 * domain_fit + 0.35 * skill_fit + 0.15 * experience_fit + 0.20 * role_alignment

Step 4 — Apply hard constraints using the strictest cap if multiple trigger:
- role_alignment < 25 then cap at 40
- skill_fit < 30 then cap at 50
- PROJECT_CONTEXT.is_regulated AND domain_fit < 50 then cap at 60

Step 5 — Assign bucket:
85+ Excellent | 70-84 Strong | 55-69 Moderate | 40-54 Weak | <40 Poor

Step 6 — Set recommendation:
- "Assign" if bucket is Excellent or Strong
- "Assign with review" if Moderate
- "Do not assign" if Weak or Poor

Perform the scoring internally. Return only the final JSON.

Required JSON shape:
{
  "project_summary": "string",
  "recommended_team": [
    {
      "assigned_member": "string",
      "assigned_role": "string",
      "compatibility_score": 0,
      "bucket": "Excellent|Strong|Moderate|Weak|Poor",
      "recommendation": "Assign|Assign with review|Do not assign",
      "scores": {
        "domain": 0,
        "skill": 0,
        "experience": 0,
        "role": 0
      },
      "summary": "1-2 sentences explaining the fit in plain language, referencing the four dimensions"
    }
  ],
  "backlog": [],
  "sprints": [],
  "risks": [],
  "recommendations": []
}

Backlog requirements:
- Generate user stories from the project objective, description, requirements, milestones, dependencies, and deadlines.
- Each backlog item must be a user story with tasks.
- Prioritize stories based on MVP value, deadlines, dependencies, regulatory/compliance needs, and delivery risk.

Backlog item shape:
{
  "id": "story_1",
  "title": "string",
  "user_story": "As a <user>, I want <capability>, so that <benefit>.",
  "description": "string",
  "priority": "High|Medium|Low",
  "estimate_points": 0,
  "source_requirement": "string",
  "acceptance_criteria": ["string"],
  "tasks": [
    {
      "id": "task_1",
      "title": "string",
      "description": "string",
      "suggested_role": "string",
      "estimate_hours": 0,
      "dependencies": ["task_id or story_id"]
    }
  ]
}

Sprint requirements:
- If options.sprint_planning_mode is "manual", the user selected options.sprints_per_week. The backend inferred options.inferred_total_weeks from project deadlines/milestones and calculated options.number_of_sprints. Create exactly options.number_of_sprints sprints.
- If options.sprint_planning_mode is "auto" or options.number_of_sprints is missing, infer a realistic sprint count from deadlines, milestones, scope, dependencies, and team capacity.
- Use options.sprint_duration_weeks when present. If missing, infer a realistic duration from the project timeline.
- Assign stories to sprints based on priority, dependencies, milestone timing, and capacity realism.
- Each sprint should have a clear goal, priority focus, story IDs, tasks summary, and deliverables.

Sprint item shape:
{
  "sprint_number": 1,
  "goal": "string",
  "duration_weeks": 0,
  "priority_focus": "string",
  "stories": ["story_id"],
  "tasks": ["task_id"],
  "deliverables": ["string"],
  "rationale": "string"
}

Return valid JSON only, with no markdown, comments, or explanatory text.

Output limits:
- project_summary: max 2 short sentences
- recommended_team: at most 5 entries, one per best-fit role
- backlog: at most 5 user stories
- each backlog story: at most 3 tasks
- sprints: if auto, prefer 3 to 5 sprints; if manual, obey options.number_of_sprints exactly
- each sprint goal/rationale/deliverables: short and direct

Input data:
${stringifyInput(projects, teamMembers, options)}
`.trim();
}

export function buildPortfolioPrompt(projects, teamMembers, options) {
  return `
# IDENTITY

You are an AI Scrum Master assistant supporting project planning and team coordination. Your role is to produce a globally balanced, data-driven team allocation plan that human Scrum Masters and Product Owners can review, refine, and approve.

Return a compact JSON object only.
Do not use markdown fences, code blocks, comments, or explanatory text.
Keep every free-text field short and direct.
Prefer terse sentence fragments over paragraphs.

# TASK

You will assess an entire pool of team members against ALL open roles across multiple projects. Your goal is to maximize overall assignment compatibility while ensuring a balanced fulfillment rate across all projects, preventing scenarios where one project is fully staffed and another has no one.

# INPUTS

1. PROJECTS (JSON array): each element describes one project and the roles open on it.
Each project object has:
- project_id (string)
- project_name (string)
- domain (string)
- is_regulated (boolean)
- open_roles (array of ROLE_SPEC objects)

2. ROLE_SPEC (JSON, nested inside open_roles):
- role_id (string)
- role_title (string)
- required_skills (array of strings)
- ideal_experience_range (array of two integers)

3. MEMBER_PROFILES (JSON array):
An array of objects, where each object contains:
- member_id (string)
- member_name (string)
- profile_text (free-form prose describing experience, domains, and skills)

# REASONING STEPS

Perform Steps 1-5 internally. Do NOT include intermediate reasoning or raw matrices in the final output.

Step 1 - Profile Extraction:
For each member in MEMBER_PROFILES, extract their primary role, years of experience, domains, and concrete skills strictly from their profile text.

Step 2 - Compute Individual Fit Scores:
For EVERY possible member-to-role pair, calculate a compatibility score (0-100):
- role_alignment (20%): 100 exact, 75 closely related, 50 adjacent, 25 distant, 0 unrelated.
- domain_fit (30%): 100 exact, 80 adjacent, 50 related, 20 unrelated, 0 none.
- skill_fit (35%): (matched_skills / total_required_skills) * 100.
- experience_fit (15%): 100 within range, 85 if +/-1 year off, 70 if 2-3 years off, 50 if 4+ years off.
Apply Caps: If project.is_regulated AND domain_fit < 50, cap the pair's score at 60. If skill_fit < 30, cap at 50.

Step 3 - Balanced Global Allocation Strategy:
To balance project fulfillment, allocate team members using the following routing strategy:
1. Identify projects with the highest criticality or lowest initial capacities.
2. Iteratively assign team members to roles where they have a "Strong" or "Excellent" fit (score >= 70).
3. Constraint: A single team member can only be assigned to EXACTLY ONE role globally.
4. Balancing Rule: If a project reaches 60% fulfillment of its open roles, pause assignments to it and prioritize filling at least 1 core role (Backend, Frontend, or Product Owner) in other projects that currently have 0% fulfillment. Minimize the variance in fulfillment rates between all projects.

Step 4 - Final Optimization:
Resolve remaining open roles with available unassigned members based on the highest remaining compatibility scores, even if they result in "Moderate" fits.

Step 5 - Output Construction:
Return only the final allocation JSON. Do not include reasoning text.

Required JSON shape:
{
  "allocation_summary": {
    "total_members_assigned": 0,
    "unassigned_members": ["string"]
  },
  "projects": [
    {
      "project_name": "string",
      "fulfillment_rate_percentage": 0,
      "assignments": [
        {
          "role_title": "string",
          "assigned_member_name": "string | Unassigned",
          "compatibility_score": 0,
          "bucket": "Excellent|Strong|Moderate|Weak|Poor|Unassigned",
          "summary": "1-2 sentences explaining why this person fits this role, or a note on the risk of leaving the role vacant."
        }
      ]
    }
  ]
}

Return ONLY valid JSON, no preamble, no markdown, no code fences.

Output limits:
- allocation_summary: concise
- each project: concise name and fulfillment rate
- each assignment summary: one short sentence
- avoid verbose justification text

Runtime input:
${stringifyPortfolioInput(projects, teamMembers, options)}
`.trim();
}
