"""Public API consumed by the frontend team."""

from __future__ import annotations

from pathlib import Path

from scrum_agent.core.schema import DemoState
from scrum_agent.core.models import to_dict
from scrum_agent.data.loaders import DEFAULT_DATA_DIR, load_projects, load_team_members
from scrum_agent.services.allocation_engine import allocate_work
from scrum_agent.services.backlog_generator import generate_backlog
from scrum_agent.services.risk_engine import build_insights, generate_risks
from scrum_agent.services.sprint_planner import plan_sprints


def build_demo_state(data_dir: str | Path | None = None) -> DemoState:
    """Build the complete deterministic state for the Scrum Agent demo."""
    resolved_data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    projects = load_projects(resolved_data_dir)
    team_members = load_team_members(resolved_data_dir / "Team Members.txt")
    backlog_items = generate_backlog(projects)
    sprint_plans = plan_sprints(projects, backlog_items)
    allocations = allocate_work(projects, backlog_items, team_members)
    risks = generate_risks(projects, backlog_items, allocations, team_members)
    insights = build_insights(projects, allocations, risks)

    return to_dict(
        {
            "projects": projects,
            "team_members": team_members,
            "backlog_items": backlog_items,
            "sprint_plans": sprint_plans,
            "allocations": allocations,
            "risks": risks,
            "insights": insights,
            "metadata": {
                "engine": "deterministic",
                "capacity_per_member_per_sprint": 8,
                "sprint_length_weeks": 2,
                "source_data_dir": str(resolved_data_dir),
            },
        }
    )  # type: ignore[return-value]


if __name__ == "__main__":
    import json

    print(json.dumps(build_demo_state(), indent=2, ensure_ascii=False))
