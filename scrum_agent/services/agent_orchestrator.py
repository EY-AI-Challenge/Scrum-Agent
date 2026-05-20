"""Hybrid Scrum Agent orchestration.

The deterministic motor remains the source of truth. The LLM layer can analyze,
explain, and propose changes, but every proposed action is validated and kept in
an approval queue for the user/frontend to accept or reject.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scrum_agent.core.schema import (
    AgentAnalysisState,
    AgentRecommendationState,
    AgentState,
    ApprovalActionState,
    DemoState,
    LLMMetadataState,
)
from scrum_agent.llm.providers import LLMProvider, LLMResponse, NullProvider, provider_from_env
from scrum_agent.services.demo_state import build_demo_state


VALID_PRIORITIES = {"critical", "high", "medium", "low"}
VALID_ACTION_TYPES = {"change_priority", "reassign_member", "move_sprint", "add_risk", "ask_product_owner"}
VALID_MODES = {"auto", "offline", "ollama", "openai"}


SYSTEM_PROMPT = """You are the Scrum Master reasoning layer for a deterministic Scrum Agent.
You analyze three concurrent projects and propose improvements, but you must not mutate the plan.
Return only valid JSON. Do not use Markdown.

Keep the output compact. Output shape:
{
  "agent_analysis": {
    "executive_summary": "string",
    "project_assessments": {"P1": "string", "P2": "string", "P3": "string"},
    "priority_analysis": ["string"],
    "allocation_analysis": ["string"],
    "risk_analysis": ["string"],
    "product_owner_questions": ["string"]
  },
  "recommendations": [
    {
      "title": "string",
      "project_id": "P1|P2|P3|null",
      "affected_item_ids": ["existing backlog item ids only"],
      "affected_member_ids": ["existing team member ids only"],
      "rationale": "string",
      "expected_impact": "string",
      "confidence": 0.0
    }
  ],
  "approval_queue": [
    {
      "action_type": "change_priority|reassign_member|move_sprint|add_risk|ask_product_owner",
      "project_id": "P1|P2|P3|null",
      "affected_item_ids": ["existing backlog item ids only"],
      "affected_member_ids": ["existing team member ids only"],
      "before": {"field": "current value"},
      "after": {"field": "proposed value"},
      "rationale": "string"
    }
  ]
}

Rules:
- Never invent project IDs, item IDs, or member IDs.
- Priority values must be critical, high, medium, or low.
- Keep proposals concise and actionable.
- Return at most 3 recommendations and at most 2 approval actions.
- The user is the final approver.
"""


def build_agent_state(
    data_dir: str | Path | None = None,
    mode: str = "auto",
    provider: LLMProvider | None = None,
) -> AgentState:
    """Build deterministic state plus optional LLM analysis and pending actions."""
    selected_mode = mode if mode in VALID_MODES else "auto"
    demo_state = build_demo_state(data_dir)

    if selected_mode == "offline":
        llm_response = NullProvider().generate(SYSTEM_PROMPT, {})
        agent_payload = _fallback_agent_payload(demo_state)
    else:
        resolved_provider = provider or provider_from_env(selected_mode)
        payload = _build_llm_payload(demo_state)
        llm_response = resolved_provider.generate(SYSTEM_PROMPT, payload)
        agent_payload = _parse_and_validate_llm_payload(demo_state, llm_response)
        if agent_payload is None:
            llm_response.fallback_used = True
            llm_response.error = llm_response.error or "Invalid LLM JSON payload; deterministic fallback used."
            agent_payload = _fallback_agent_payload(demo_state)

    return {
        **demo_state,
        "agent_analysis": agent_payload["agent_analysis"],
        "recommendations": agent_payload["recommendations"],
        "approval_queue": agent_payload["approval_queue"],
        "llm_metadata": _metadata_from_response(llm_response, selected_mode),
    }


def _build_llm_payload(demo_state: DemoState) -> dict[str, Any]:
    key_items = sorted(
        demo_state["backlog_items"],
        key=lambda item: (-item["priority_score"], item["project_id"], item["item_id"]),
    )[:12]
    key_item_ids = {item["item_id"] for item in key_items}
    key_allocations = [
        allocation
        for allocation in demo_state["allocations"]
        if allocation["item_id"] in key_item_ids
    ]
    key_risks = [
        risk
        for risk in demo_state["risks"]
        if risk["severity"] in {"critical", "high"}
    ][:8]
    return {
        "objective": (
            "Analyze the Scrum Agent plan for priority management, team allocation efficiency, "
            "delivery risks, and improvement opportunities across three concurrent projects."
        ),
        "constraints": {
            "decision_authority": "LLM proposes; deterministic motor validates; user approves.",
            "capacity_per_member_per_sprint": demo_state["metadata"]["capacity_per_member_per_sprint"],
            "allowed_priorities": sorted(VALID_PRIORITIES),
        },
        "projects": [
            {
                "project_id": project["project_id"],
                "name": project["name"],
                "domain": project["domain"],
                "mvp_week": project["mvp_week"],
                "final_week": project["final_week"],
                "dependency_count": len(project["dependencies"]),
                "requirement_count": len(project["requirements"]),
            }
            for project in demo_state["projects"]
        ],
        "team_members": [
            {
                "member_id": member["member_id"],
                "role": member["role"],
                "skills": member["skills"][:4],
                "domains": member["domains"][:2],
                "capacity_per_sprint": member["capacity_per_sprint"],
            }
            for member in demo_state["team_members"]
        ],
        "key_backlog_items": [
            {
                "item_id": item["item_id"],
                "project_id": item["project_id"],
                "priority": item["priority"],
                "priority_score": item["priority_score"],
                "story_points": item["story_points"],
                "required_skills": item["required_skills"][:4],
                "dependency_count": len(item["dependencies"]),
                "sprint_number": item["sprint_number"],
            }
            for item in key_items
        ],
        "key_allocations": [
            {
                "item_id": allocation["item_id"],
                "project_id": allocation["project_id"],
                "sprint_id": allocation["sprint_id"],
                "member_id": allocation["member_id"],
                "assigned_points": allocation["assigned_points"],
                "match_score": allocation["match_score"],
                "over_capacity": allocation["over_capacity"],
            }
            for allocation in key_allocations
        ],
        "critical_high_risks": [
            {
                "risk_id": risk["risk_id"],
                "project_id": risk["project_id"],
                "severity": risk["severity"],
                "category": risk["category"],
                "title": risk["title"],
            }
            for risk in key_risks
        ],
    }


def _parse_and_validate_llm_payload(demo_state: DemoState, response: LLMResponse) -> dict[str, Any] | None:
    if response.fallback_used or not response.content.strip():
        return None
    try:
        raw_payload = json.loads(_strip_json_fences(response.content))
    except json.JSONDecodeError:
        return None
    return _validate_agent_payload(demo_state, raw_payload)


def _validate_agent_payload(demo_state: DemoState, raw_payload: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(raw_payload, dict):
        return None

    known_projects = {project["project_id"] for project in demo_state["projects"]}
    known_items = {item["item_id"] for item in demo_state["backlog_items"]}
    known_members = {member["member_id"] for member in demo_state["team_members"]}

    analysis = _validate_analysis(raw_payload.get("agent_analysis"), known_projects)
    if analysis is None:
        return None

    recommendations = _validate_recommendations(
        raw_payload.get("recommendations", []),
        known_projects,
        known_items,
        known_members,
    )
    if recommendations is None:
        return None

    approval_queue = _validate_approval_queue(
        raw_payload.get("approval_queue", []),
        demo_state,
        known_projects,
        known_items,
        known_members,
    )
    if approval_queue is None:
        return None

    return {
        "agent_analysis": analysis,
        "recommendations": recommendations,
        "approval_queue": approval_queue,
    }


def _validate_analysis(raw_analysis: Any, known_projects: set[str]) -> AgentAnalysisState | None:
    if not isinstance(raw_analysis, dict):
        return None
    project_assessments = raw_analysis.get("project_assessments", {})
    if not isinstance(project_assessments, dict):
        return None

    return {
        "executive_summary": _text(raw_analysis.get("executive_summary"), "No executive summary provided."),
        "project_assessments": {
            project_id: _text(project_assessments.get(project_id), "No assessment provided.")
            for project_id in sorted(known_projects)
        },
        "priority_analysis": _text_list(raw_analysis.get("priority_analysis")),
        "allocation_analysis": _text_list(raw_analysis.get("allocation_analysis")),
        "risk_analysis": _text_list(raw_analysis.get("risk_analysis")),
        "product_owner_questions": _text_list(raw_analysis.get("product_owner_questions")),
    }


def _validate_recommendations(
    raw_recommendations: Any,
    known_projects: set[str],
    known_items: set[str],
    known_members: set[str],
) -> list[AgentRecommendationState] | None:
    if not isinstance(raw_recommendations, list):
        return None

    recommendations: list[AgentRecommendationState] = []
    for index, raw_recommendation in enumerate(raw_recommendations[:6], start=1):
        if not isinstance(raw_recommendation, dict):
            return None
        project_id = raw_recommendation.get("project_id")
        if project_id is not None and project_id not in known_projects:
            return None
        if project_id is None:
            project_id = None
        item_ids = _validated_ids(raw_recommendation.get("affected_item_ids"), known_items)
        member_ids = _validated_ids(raw_recommendation.get("affected_member_ids"), known_members)
        if item_ids is None or member_ids is None:
            return None
        recommendations.append(
            {
                "recommendation_id": f"REC-{index:03d}",
                "title": _text(raw_recommendation.get("title"), "Review Scrum Agent recommendation"),
                "project_id": project_id,
                "affected_item_ids": item_ids,
                "affected_member_ids": member_ids,
                "rationale": _text(raw_recommendation.get("rationale"), "No rationale provided."),
                "expected_impact": _text(raw_recommendation.get("expected_impact"), "Impact not quantified."),
                "confidence": _confidence(raw_recommendation.get("confidence")),
            }
        )
    return recommendations


def _validate_approval_queue(
    raw_actions: Any,
    demo_state: DemoState,
    known_projects: set[str],
    known_items: set[str],
    known_members: set[str],
) -> list[ApprovalActionState] | None:
    if not isinstance(raw_actions, list):
        return None

    actions: list[ApprovalActionState] = []
    for index, raw_action in enumerate(raw_actions[:8], start=1):
        if not isinstance(raw_action, dict):
            return None
        action_type = raw_action.get("action_type")
        if action_type not in VALID_ACTION_TYPES:
            return None
        project_id = raw_action.get("project_id")
        if project_id is not None and project_id not in known_projects:
            return None
        if project_id is None:
            project_id = None
        item_ids = _validated_ids(raw_action.get("affected_item_ids"), known_items)
        member_ids = _validated_ids(raw_action.get("affected_member_ids"), known_members)
        if item_ids is None or member_ids is None:
            return None

        before = _primitive_dict(raw_action.get("before"))
        after = _primitive_dict(raw_action.get("after"))
        if before is None or after is None:
            return None
        if not _valid_priority_transition(before, after):
            return None
        if action_type == "reassign_member" and not _reassignment_preserves_capacity(demo_state, item_ids, after):
            return None

        actions.append(
            {
                "action_id": f"ACT-{index:03d}",
                "action_type": action_type,
                "project_id": project_id,
                "affected_item_ids": item_ids,
                "affected_member_ids": member_ids,
                "before": before,
                "after": after,
                "rationale": _text(raw_action.get("rationale"), "No rationale provided."),
                "status": "pending",
            }
        )
    return actions


def _fallback_agent_payload(demo_state: DemoState) -> dict[str, Any]:
    project_assessments = {
        "P1": "Loan Approval needs early compliance, auditability, risk rules, and secure backend foundations.",
        "P2": "Inventory is data-dependent; ingestion quality and baseline forecasting should lead before dashboard work.",
        "P3": "Patient Triage is the most urgent and has an explicit timeline inconsistency requiring Product Owner alignment.",
    }
    return {
        "agent_analysis": {
            "executive_summary": (
                "The deterministic motor recommends protecting Sprint 1 for alignment, rules, data dependencies, "
                "and compliance before accelerating delivery across the three projects."
            ),
            "project_assessments": project_assessments,
            "priority_analysis": [
                "P3 should stay highly visible because its MVP and pilot dates conflict with later milestones.",
                "P1 compliance, security, and audit items should remain high priority because they govern regulated decisions.",
                "P2 data ingestion and validation should be prioritized before forecasting or dashboard polish.",
            ],
            "allocation_analysis": [
                "Specialists are assigned to domain-heavy work: Tiago for loan risk, Marta and Beatriz for inventory data, Luis for symptom classification.",
                "Capacity is currently protected: no allocation is marked over capacity.",
            ],
            "risk_analysis": [
                "Escalate RISK-P3-DEADLINE before committing to sprint dates.",
                "Keep P1 and P3 compliance/security checks in the MVP, not as late hardening.",
            ],
            "product_owner_questions": [
                "For P3, is the real pilot target Week 3 or Weeks 14-15?",
                "For P2, what historical sales data quality is available for the forecasting baseline?",
                "For P1, which audit fields are mandatory for approval overrides?",
            ],
        },
        "recommendations": [
            {
                "recommendation_id": "REC-001",
                "title": "Resolve Patient Triage timeline before scope lock",
                "project_id": "P3",
                "affected_item_ids": ["P3-BL-001", "P3-BL-002"],
                "affected_member_ids": ["sofia-almeida", "ana-costa", "dr-paulo-mendes"],
                "rationale": "The project has conflicting MVP, pilot, and final delivery dates.",
                "expected_impact": "Reduces sprint churn and avoids committing to an impossible pilot plan.",
                "confidence": 0.95,
            },
            {
                "recommendation_id": "REC-002",
                "title": "Keep Inventory data quality ahead of forecasting",
                "project_id": "P2",
                "affected_item_ids": ["P2-BL-002", "P2-BL-003"],
                "affected_member_ids": ["marta-carvalho", "beatriz-gomes"],
                "rationale": "Forecasting quality depends directly on historical sales and inventory data readiness.",
                "expected_impact": "Improves forecast credibility and reduces wasted model work.",
                "confidence": 0.9,
            },
            {
                "recommendation_id": "REC-003",
                "title": "Treat loan auditability as an MVP constraint",
                "project_id": "P1",
                "affected_item_ids": ["P1-BL-001", "P1-BL-007"],
                "affected_member_ids": ["teresa-rocha", "nuno-figueiredo"],
                "rationale": "Loan approval automation is regulated and needs traceable decision records.",
                "expected_impact": "Improves executive confidence and technical defensibility.",
                "confidence": 0.88,
            },
        ],
        "approval_queue": [
            {
                "action_id": "ACT-001",
                "action_type": "ask_product_owner",
                "project_id": "P3",
                "affected_item_ids": ["P3-BL-001"],
                "affected_member_ids": ["sofia-almeida"],
                "before": {"timeline_status": "conflicting"},
                "after": {"decision_needed": "confirm MVP and pilot dates"},
                "rationale": "The agent should not re-plan P3 until the date conflict is resolved.",
                "status": "pending",
            }
        ],
    }


def _metadata_from_response(response: LLMResponse, mode: str) -> LLMMetadataState:
    return {
        "provider": response.provider if response.provider in {"null", "ollama", "openai"} else "null",
        "model": response.model,
        "mode": mode if mode in VALID_MODES else "auto",
        "fallback_used": response.fallback_used,
        "latency_ms": response.latency_ms,
        "error": response.error,
    }


def _strip_json_fences(content: str) -> str:
    stripped = content.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    return match.group(1).strip() if match else stripped


def _text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()][:8]


def _validated_ids(value: Any, known_ids: set[str]) -> list[str] | None:
    if value is None:
        return []
    if not isinstance(value, list):
        return None
    ids = []
    for item in value:
        if not isinstance(item, str) or item not in known_ids:
            return None
        ids.append(item)
    return ids


def _primitive_dict(value: Any) -> dict[str, str | int | float | bool | None] | None:
    if value is None:
        return {}
    if not isinstance(value, dict):
        return None
    primitives: dict[str, str | int | float | bool | None] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, (str, int, float, bool, type(None))):
            return None
        primitives[key] = item
    return primitives


def _valid_priority_transition(
    before: dict[str, str | int | float | bool | None],
    after: dict[str, str | int | float | bool | None],
) -> bool:
    for payload in (before, after):
        priority = payload.get("priority")
        if priority is not None and priority not in VALID_PRIORITIES:
            return False
    return True


def _reassignment_preserves_capacity(
    demo_state: DemoState,
    item_ids: list[str],
    after: dict[str, str | int | float | bool | None],
) -> bool:
    target_member_id = after.get("member_id") or after.get("assigned_member_id")
    if not isinstance(target_member_id, str):
        return False

    item_by_id = {item["item_id"]: item for item in demo_state["backlog_items"]}
    capacity_by_member = {member["member_id"]: member["capacity_per_sprint"] for member in demo_state["team_members"]}
    if target_member_id not in capacity_by_member:
        return False

    usage_by_sprint: dict[str, int] = {}
    for allocation in demo_state["allocations"]:
        if allocation["member_id"] == target_member_id and allocation["item_id"] not in item_ids:
            sprint_label = _global_sprint_label(allocation["sprint_id"])
            usage_by_sprint[sprint_label] = usage_by_sprint.get(sprint_label, 0) + allocation["assigned_points"]

    for item_id in item_ids:
        item = item_by_id[item_id]
        sprint_label = f"S{item['sprint_number']}"
        usage_by_sprint[sprint_label] = usage_by_sprint.get(sprint_label, 0) + item["story_points"]
        if usage_by_sprint[sprint_label] > capacity_by_member[target_member_id]:
            return False
    return True


def _global_sprint_label(project_sprint_id: str) -> str:
    if "-S" in project_sprint_id:
        return f"S{project_sprint_id.rsplit('-S', 1)[1]}"
    return project_sprint_id


def _confidence(value: Any) -> float:
    if isinstance(value, (int, float)):
        return min(1.0, max(0.0, float(value)))
    return 0.5


if __name__ == "__main__":
    print(json.dumps(build_agent_state(), indent=2, ensure_ascii=False))
