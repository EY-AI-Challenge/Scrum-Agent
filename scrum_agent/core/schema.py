"""Typed data contract for the Motor Team public API.

This module is the integration contract consumed by the App Team. If the shape
returned by build_demo_state changes, update these TypedDicts and the JSON
example generated from the same API.
"""

from __future__ import annotations

from typing import Literal, TypedDict


ProjectId = Literal["P1", "P2", "P3"]
Domain = Literal["fintech", "retail", "healthcare"]
Priority = Literal["critical", "high", "medium", "low"]
ItemType = Literal["user_story", "task"]
ItemStatus = Literal["todo", "in_progress", "done"]
RiskSeverity = Literal["critical", "high", "medium", "low"]
RiskCategory = Literal["planning", "compliance", "data", "security", "capacity", "dependency"]
SourceStatus = Literal["pdf_loaded", "fallback"]
LLMProviderName = Literal["null", "ollama", "openai"]
LLMMode = Literal["offline", "ollama", "openai", "auto"]
ApprovalStatus = Literal["pending", "approved", "rejected"]
ApprovalActionType = Literal["change_priority", "reassign_member", "move_sprint", "add_risk", "ask_product_owner"]


class ProjectState(TypedDict):
    project_id: ProjectId
    name: str
    domain: Domain
    mvp_week: int
    final_week: int
    objective: str
    summary: str
    requirements: list[str]
    deadlines: dict[str, str]
    milestones: list[str]
    dependencies: list[str]
    source_file: str
    source_status: SourceStatus
    raw_text_excerpt: str


class TeamMemberState(TypedDict):
    member_id: str
    name: str
    role: str
    summary: str
    skills: list[str]
    domains: list[str]
    experience_years: int
    seniority: int
    capacity_per_sprint: int


class BacklogItemState(TypedDict):
    item_id: str
    project_id: ProjectId
    epic: str
    title: str
    description: str
    item_type: ItemType
    required_skills: list[str]
    priority_score: int
    priority: Priority
    story_points: int
    dependencies: list[str]
    acceptance_criteria: list[str]
    sprint_hint: int
    phase: str
    status: ItemStatus
    sprint_number: int
    sprint_id: str


class SprintPlanState(TypedDict):
    sprint_id: str
    project_id: ProjectId
    sprint_number: int
    start_week: int
    end_week: int
    focus: str
    goal: str
    item_ids: list[str]
    planned_points: int
    capacity_points: int


class AllocationState(TypedDict):
    allocation_id: str
    item_id: str
    project_id: ProjectId
    sprint_id: str
    member_id: str
    member_name: str
    role: str
    assigned_points: int
    match_score: float
    matched_skills: list[str]
    matched_domains: list[str]
    rationale: str
    over_capacity: bool


class RiskState(TypedDict):
    risk_id: str
    project_id: ProjectId | None
    severity: RiskSeverity
    category: RiskCategory
    title: str
    description: str
    mitigation: str
    owner_suggestion: str


class InsightState(TypedDict):
    title: str
    description: str
    impact: str


class MetadataState(TypedDict):
    engine: Literal["deterministic"]
    capacity_per_member_per_sprint: int
    sprint_length_weeks: int
    source_data_dir: str


class DemoState(TypedDict):
    projects: list[ProjectState]
    team_members: list[TeamMemberState]
    backlog_items: list[BacklogItemState]
    sprint_plans: list[SprintPlanState]
    allocations: list[AllocationState]
    risks: list[RiskState]
    insights: list[InsightState]
    metadata: MetadataState


class LLMMetadataState(TypedDict):
    provider: LLMProviderName
    model: str
    mode: LLMMode
    fallback_used: bool
    latency_ms: int
    error: str | None


class AgentRecommendationState(TypedDict):
    recommendation_id: str
    title: str
    project_id: ProjectId | None
    affected_item_ids: list[str]
    affected_member_ids: list[str]
    rationale: str
    expected_impact: str
    confidence: float


class ApprovalActionState(TypedDict):
    action_id: str
    action_type: ApprovalActionType
    project_id: ProjectId | None
    affected_item_ids: list[str]
    affected_member_ids: list[str]
    before: dict[str, str | int | float | bool | None]
    after: dict[str, str | int | float | bool | None]
    rationale: str
    status: ApprovalStatus


class AgentAnalysisState(TypedDict):
    executive_summary: str
    project_assessments: dict[ProjectId, str]
    priority_analysis: list[str]
    allocation_analysis: list[str]
    risk_analysis: list[str]
    product_owner_questions: list[str]


class AgentState(DemoState):
    agent_analysis: AgentAnalysisState
    recommendations: list[AgentRecommendationState]
    approval_queue: list[ApprovalActionState]
    llm_metadata: LLMMetadataState
