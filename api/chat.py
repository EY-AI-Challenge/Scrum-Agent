"""Chat handler backed by the configurable Scrum Agent LLM provider."""

from __future__ import annotations

from typing import Any

from scrum_agent.llm.providers import provider_from_env


_SYSTEM_PROMPT = """\
You are an AI Scrum Master agent for a multi-project portfolio.

Use the supplied current portfolio state, agent analysis, recommendations, and approval queue.
Answer in the same language as the user. Be concise, practical, and data-backed.

Rules:
- Reference concrete project IDs, backlog item IDs, member names, sprint IDs, risks, and scores when useful.
- The deterministic plan is the source of truth.
- Recommendations and approval_queue entries are proposals only; do not claim they were applied.
- If the user asks for a change, explain the proposed action and whether it belongs in the approval queue.
"""


def handle_chat(message: str, history: list[dict], agent_state: dict[str, Any]) -> str:
    provider = provider_from_env(_chat_mode(agent_state))
    payload = {
        "current_state": _state_for_chat(agent_state),
        "conversation": _sanitized_history(history),
        "user_message": message,
    }
    response = provider.generate(_SYSTEM_PROMPT, payload, response_format="text")
    if response.fallback_used or not response.content.strip():
        return _fallback_response(message, agent_state)
    return response.content.strip()


def _chat_mode(agent_state: dict[str, Any]) -> str:
    metadata = agent_state.get("llm_metadata", {})
    mode = metadata.get("mode") if isinstance(metadata, dict) else None
    return mode if isinstance(mode, str) else "auto"


def _sanitized_history(history: list[dict]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history[-8:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()[:1200]})
    return messages


def _state_for_chat(agent_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "projects": agent_state.get("projects", []),
        "team_members": agent_state.get("team_members", []),
        "backlog_items": agent_state.get("backlog_items", []),
        "sprint_plans": agent_state.get("sprint_plans", []),
        "allocations": agent_state.get("allocations", []),
        "risks": agent_state.get("risks", []),
        "insights": agent_state.get("insights", []),
        "agent_analysis": agent_state.get("agent_analysis", {}),
        "recommendations": agent_state.get("recommendations", []),
        "approval_queue": agent_state.get("approval_queue", []),
        "llm_metadata": agent_state.get("llm_metadata", {}),
    }


def _fallback_response(message: str, agent_state: dict[str, Any]) -> str:
    msg = message.lower()

    if any(w in msg for w in ["aprovação", "approval", "recommend", "recomend", "agente", "agent"]):
        analysis = agent_state.get("agent_analysis", {})
        recommendations = agent_state.get("recommendations", [])
        actions = agent_state.get("approval_queue", [])
        lines = [
            f"**Resumo do agente:** {analysis.get('executive_summary', 'Sem análise disponível.')}",
            "",
            "**Recomendações principais:**",
        ]
        for rec in recommendations[:3]:
            lines.append(
                f"- {rec['recommendation_id']} ({rec['project_id'] or 'portfolio'}): "
                f"{rec['title']} — {rec['expected_impact']}"
            )
        if actions:
            lines.extend(["", "**Ações pendentes de aprovação:**"])
            for action in actions[:5]:
                lines.append(
                    f"- {action['action_id']} {action['action_type']} "
                    f"em {action['project_id'] or 'portfolio'}: {action['rationale']}"
                )
        return "\n".join(lines)

    if any(w in msg for w in ["risco", "risk"]):
        risks = agent_state.get("risks", [])
        critical = [r for r in risks if r["severity"] == "critical"]
        if critical:
            r = critical[0]
            return (
                f"**Risco crítico identificado:** {r['title']}\n\n"
                f"{r['description']}\n\n"
                f"**Mitigação sugerida:** {r['mitigation']}\n"
                f"**Owner sugerido:** {r['owner_suggestion']}"
            )

    if any(w in msg for w in ["sprint", "capacidade", "capacity"]):
        plans = agent_state.get("sprint_plans", [])
        lines = ["**Resumo de capacidade por sprint:**\n"]
        for sp in plans[:6]:
            pct = round(sp["planned_points"] / sp["capacity_points"] * 100) if sp["capacity_points"] else 0
            lines.append(
                f"- {sp['sprint_id']} (P{sp['project_id']}): "
                f"{sp['planned_points']}/{sp['capacity_points']} pts ({pct}%)"
            )
        return "\n".join(lines)

    if any(w in msg for w in ["insight", "estratég"]):
        insights = agent_state.get("insights", [])
        lines = []
        for ins in insights:
            lines.append(f"**{ins['title']}**\n{ins['description']}\n*Impacto: {ins['impact']}*")
        return "\n\n".join(lines)

    projects = agent_state.get("projects", [])
    names = ", ".join(p["name"] for p in projects)
    metadata = agent_state.get("llm_metadata", {})
    provider = metadata.get("provider", "null") if isinstance(metadata, dict) else "null"
    return (
        f"Olá! Sou o Scrum Master Agent. Estou a gerir os projetos: {names}.\n\n"
        "Posso ajudar-te com:\n"
        "- Estado dos sprints e capacidade da equipa\n"
        "- Riscos identificados e mitigações\n"
        "- Alocações e justificações\n"
        "- Recomendações do agente e ações pendentes de aprovação\n\n"
        f"**Modo atual:** {provider}. Quando o Ollama estiver pronto, configura "
        "`SCRUM_AGENT_LLM_PROVIDER=ollama` para respostas generativas locais."
    )
