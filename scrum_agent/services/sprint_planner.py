"""Plan backlog items into two-week sprints."""

from __future__ import annotations

import math
from collections import defaultdict

from scrum_agent.core.models import BacklogItem, Project, SprintPlan


SPRINT_FOCUS = {
    1: "Discovery, rules, compliance, and dependency validation",
    2: "Backend, data foundation, and model prototypes",
    3: "Dashboards, integration contracts, and control workflows",
    4: "Operational constraints, overrides, and MVP hardening",
}


def plan_sprints(projects: list[Project], backlog_items: list[BacklogItem]) -> list[SprintPlan]:
    projects_by_id = {project.project_id: project for project in projects}
    items_by_sprint: dict[tuple[str, int], list[BacklogItem]] = defaultdict(list)

    for item in backlog_items:
        project = projects_by_id[item.project_id]
        max_mvp_sprint = max(1, math.ceil(project.mvp_week / 2))
        item.sprint_number = min(max(item.sprint_hint, 1), max_mvp_sprint)
        item.sprint_id = f"{item.project_id}-S{item.sprint_number}"
        items_by_sprint[(item.project_id, item.sprint_number)].append(item)

    sprint_plans: list[SprintPlan] = []
    for (project_id, sprint_number), items in sorted(items_by_sprint.items()):
        planned_points = sum(item.story_points for item in items)
        focus = SPRINT_FOCUS.get(sprint_number, "Delivery hardening and rollout preparation")
        sprint_plans.append(
            SprintPlan(
                sprint_id=f"{project_id}-S{sprint_number}",
                project_id=project_id,
                sprint_number=sprint_number,
                start_week=(sprint_number - 1) * 2 + 1,
                end_week=sprint_number * 2,
                focus=focus,
                goal=_build_goal(items, focus),
                item_ids=[item.item_id for item in items],
                planned_points=planned_points,
                capacity_points=max(24, planned_points),
            )
        )
    return sprint_plans


def _build_goal(items: list[BacklogItem], focus: str) -> str:
    epics = sorted({item.epic for item in items})
    epic_text = ", ".join(epics[:3])
    return f"{focus}: progress {epic_text}."

