"""Domain models for the Scrum Agent motor."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any


@dataclass
class Project:
    project_id: str
    name: str
    domain: str
    mvp_week: int
    final_week: int
    objective: str
    summary: str
    requirements: list[str]
    deadlines: dict[str, str]
    milestones: list[str]
    dependencies: list[str]
    source_file: str
    source_status: str = "fallback"
    raw_text_excerpt: str = ""


@dataclass
class TeamMember:
    member_id: str
    name: str
    role: str
    summary: str
    skills: list[str]
    domains: list[str]
    experience_years: int
    seniority: int
    capacity_per_sprint: int = 8


@dataclass
class BacklogItem:
    item_id: str
    project_id: str
    epic: str
    title: str
    description: str
    item_type: str
    required_skills: list[str]
    priority_score: int
    priority: str
    story_points: int
    dependencies: list[str]
    acceptance_criteria: list[str]
    sprint_hint: int
    phase: str
    status: str = "todo"
    sprint_number: int = 0
    sprint_id: str = ""


@dataclass
class SprintPlan:
    sprint_id: str
    project_id: str
    sprint_number: int
    start_week: int
    end_week: int
    focus: str
    goal: str
    item_ids: list[str]
    planned_points: int
    capacity_points: int


@dataclass
class Allocation:
    allocation_id: str
    item_id: str
    project_id: str
    sprint_id: str
    member_id: str
    member_name: str
    role: str
    assigned_points: int
    match_score: float
    matched_skills: list[str]
    matched_domains: list[str]
    rationale: str
    over_capacity: bool = False


@dataclass
class Risk:
    risk_id: str
    project_id: str | None
    severity: str
    category: str
    title: str
    description: str
    mitigation: str
    owner_suggestion: str


def to_dict(value: Any) -> Any:
    """Recursively serialize dataclasses into plain Python containers."""
    if is_dataclass(value):
        return {field.name: to_dict(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, tuple):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_dict(item) for key, item in value.items()}
    return value

