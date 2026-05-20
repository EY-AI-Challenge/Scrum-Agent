import json
import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from models import UserStory, Sprint, ProjectContext, TeamMember, ChatMessage
from data_loader import load_project, load_team_members

logger = logging.getLogger(__name__)

# Load .env from backend/ or Solution/ (parent)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# In-process cache: project context is expensive to rebuild (reads PDFs + team file)
_project_cache: dict[str, ProjectContext] = {}
_team_cache: list[TeamMember] | None = None


def _get_project(project_id: str) -> ProjectContext:
    if project_id not in _project_cache:
        _project_cache[project_id] = load_project(project_id)
    return _project_cache[project_id]


def _get_team() -> list[TeamMember]:
    global _team_cache
    if _team_cache is None:
        _team_cache = load_team_members()
    return _team_cache


def _project_summary(project: ProjectContext, team: list[TeamMember]) -> str:
    team_str = "\n".join(
        f"- {m.name} ({m.role}, {m.experience_years}y exp, domain: {m.domain}, skills: {', '.join(m.skills[:5])})"
        for m in team
    )
    req_str = "\n".join(f"- {r}" for r in project.requirements)
    ms_str = "\n".join(f"- {m}" for m in project.milestones)
    return f"""PROJECT: {project.name}
OBJECTIVE: {project.objective[:300]}
DURATION: {project.duration_weeks} weeks
REQUIREMENTS:
{req_str}
MILESTONES:
{ms_str}
TEAM:
{team_str}"""


def _call(prompt: str, system: str | None = None) -> str:
    contents = []
    if system:
        contents.append(types.Content(role="user", parts=[types.Part(text=f"[System instructions]\n{system}\n\n[User message]\n{prompt}")]))
    else:
        contents.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=65536,
        ),
    )
    return response.text.strip()


def _parse_json(raw: str) -> list:
    import re
    text = raw.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0].strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract the first JSON array using bracket matching
    start = text.find("[")
    if start == -1:
        raise ValueError("No JSON array found in response")

    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])

    raise ValueError("Could not extract valid JSON array from response")


def generate_backlog(project_id: str) -> list[UserStory]:
    project = _get_project(project_id)
    team = _get_team()
    context = _project_summary(project, team)

    prompt = f"""You are a Scrum Master. Generate a product backlog for this project.

{context}

Generate exactly 12 user stories. Keep all text short and concise.

Return ONLY a JSON array, no markdown, no explanation:
[
  {{
    "id": "US-001",
    "title": "Short title",
    "description": "As a [role], I want [feature] so that [benefit]",
    "acceptance_criteria": ["Criterion 1", "Criterion 2"],
    "story_points": 5,
    "priority": "high",
    "assigned_to": "Name Surname",
    "sprint_id": null,
    "status": "todo",
    "tags": ["backend"]
  }}
]"""

    raw = _call(prompt)
    logger.info("=== GEMINI RAW RESPONSE (first 500 chars) ===")
    logger.info(raw[:500])
    logger.info("=== LAST 200 chars ===")
    logger.info(raw[-200:])
    stories_data = _parse_json(raw)
    return [UserStory(**s) for s in stories_data]


def generate_sprints(project_id: str, sprint_duration_weeks: int = 2) -> list[Sprint]:
    project = _get_project(project_id)
    from storage import load_stories
    stories = load_stories(project_id)

    if not stories:
        return []

    num_sprints = project.duration_weeks // sprint_duration_weeks
    capacity = sprint_duration_weeks * 20

    stories_summary = json.dumps([
        {"id": s.id, "title": s.title, "story_points": s.story_points, "priority": s.priority}
        for s in stories
    ], indent=2)

    prompt = f"""You are a Scrum Master planning sprints for: {project.name}

Project duration: {project.duration_weeks} weeks
Sprint duration: {sprint_duration_weeks} weeks
Number of sprints: {num_sprints}
Capacity per sprint: ~{capacity} story points

Stories to distribute:
{stories_summary}

Rules:
- Respect story priorities (high priority first)
- Don't exceed capacity per sprint
- Write a clear sprint goal for each sprint
- Distribute work logically (foundations first, then features, then polish)
- Use all stories — every story must be assigned to a sprint

Return a JSON array of sprints:
[
  {{
    "id": "sprint-1",
    "name": "Sprint 1",
    "goal": "...",
    "duration_weeks": {sprint_duration_weeks},
    "start_week": 1,
    "stories": ["US-001", "US-002"],
    "capacity_points": {capacity}
  }}
]

Return ONLY the JSON array, no markdown, no explanation."""

    raw = _call(prompt)
    sprints_data = _parse_json(raw)
    return [Sprint(**s) for s in sprints_data]


def chat(project_id: str, user_message: str, history: list[ChatMessage]) -> str:
    project = _get_project(project_id)
    team = _get_team()
    from storage import load_stories, load_sprints
    stories = load_stories(project_id)
    sprints = load_sprints(project_id)

    context = _project_summary(project, team)
    backlog_summary = f"{len(stories)} stories in backlog" if stories else "No backlog generated yet"
    sprint_summary = f"{len(sprints)} sprints planned" if sprints else "No sprints planned yet"

    system = f"""You are an expert AI Scrum Master assistant for the following project:

{context}

Current state:
- Backlog: {backlog_summary}
- Sprints: {sprint_summary}

You help with: sprint planning, story refinement, prioritization, team assignments, risk identification, and agile best practices.
Be concise, practical, and actionable. When asked to modify stories or sprints, describe the changes clearly."""

    # Build conversation history string
    history_text = ""
    for msg in history[-6:]:  # last 6 messages for context
        role = "User" if msg.role == "user" else "Assistant"
        history_text += f"{role}: {msg.content}\n\n"

    prompt = f"{history_text}User: {user_message}"

    return _call(prompt, system=system)
