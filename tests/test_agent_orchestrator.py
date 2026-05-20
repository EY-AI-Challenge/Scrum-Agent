import json
import unittest

from scrum_agent.llm.providers import LLMResponse
from scrum_agent.services.agent_orchestrator import build_agent_state


class FakeProvider:
    provider_name = "ollama"
    model = "fake-model"

    def __init__(self, content: str):
        self.content = content

    def generate(self, system_prompt: str, user_payload: dict) -> LLMResponse:
        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            content=self.content,
            fallback_used=False,
            latency_ms=12,
        )


class AgentOrchestratorTest(unittest.TestCase):
    def test_offline_mode_uses_null_provider_fallback(self):
        state = build_agent_state(mode="offline")
        self.assertEqual(state["llm_metadata"]["provider"], "null")
        self.assertTrue(state["llm_metadata"]["fallback_used"])
        self.assertEqual(state["approval_queue"][0]["status"], "pending")
        self.assertEqual(len(state["projects"]), 3)
        self.assertEqual(len(state["team_members"]), 15)

    def test_valid_provider_payload_enters_recommendations_and_approval_queue(self):
        provider = FakeProvider(json.dumps(_valid_llm_payload()))
        state = build_agent_state(mode="ollama", provider=provider)

        self.assertEqual(state["llm_metadata"]["provider"], "ollama")
        self.assertFalse(state["llm_metadata"]["fallback_used"])
        self.assertEqual(state["recommendations"][0]["recommendation_id"], "REC-001")
        self.assertEqual(state["recommendations"][0]["affected_item_ids"], ["P3-BL-001"])
        self.assertEqual(state["approval_queue"][0]["action_id"], "ACT-001")
        self.assertEqual(state["approval_queue"][0]["status"], "pending")
        self.assertEqual(state["approval_queue"][0]["after"]["priority"], "critical")

    def test_invalid_json_falls_back_without_crashing(self):
        provider = FakeProvider("not json")
        state = build_agent_state(mode="ollama", provider=provider)

        self.assertTrue(state["llm_metadata"]["fallback_used"])
        self.assertEqual(state["llm_metadata"]["provider"], "ollama")
        self.assertGreaterEqual(len(state["recommendations"]), 1)

    def test_unknown_item_id_is_rejected_and_falls_back(self):
        payload = _valid_llm_payload()
        payload["recommendations"][0]["affected_item_ids"] = ["UNKNOWN"]
        provider = FakeProvider(json.dumps(payload))

        state = build_agent_state(mode="ollama", provider=provider)

        self.assertTrue(state["llm_metadata"]["fallback_used"])
        self.assertEqual(state["recommendations"][0]["recommendation_id"], "REC-001")
        self.assertEqual(state["recommendations"][0]["project_id"], "P3")

    def test_unknown_project_id_is_rejected_and_falls_back(self):
        payload = _valid_llm_payload()
        payload["recommendations"][0]["project_id"] = "P99"
        provider = FakeProvider(json.dumps(payload))

        state = build_agent_state(mode="ollama", provider=provider)

        self.assertTrue(state["llm_metadata"]["fallback_used"])
        self.assertEqual(state["recommendations"][0]["project_id"], "P3")

    def test_invalid_priority_is_rejected_and_falls_back(self):
        payload = _valid_llm_payload()
        payload["approval_queue"][0]["after"]["priority"] = "P1"
        provider = FakeProvider(json.dumps(payload))

        state = build_agent_state(mode="ollama", provider=provider)

        self.assertTrue(state["llm_metadata"]["fallback_used"])
        self.assertNotEqual(state["approval_queue"][0]["action_type"], "change_priority")

    def test_reassignment_that_breaks_capacity_is_rejected(self):
        payload = _valid_llm_payload()
        payload["approval_queue"][0] = {
            "action_type": "reassign_member",
            "project_id": "P3",
            "affected_item_ids": ["P3-BL-003"],
            "affected_member_ids": ["joao-ferreira"],
            "before": {"member_id": "luis-teixeira"},
            "after": {"member_id": "joao-ferreira"},
            "rationale": "Try to move symptom classification to backend owner.",
        }
        provider = FakeProvider(json.dumps(payload))

        state = build_agent_state(mode="ollama", provider=provider)

        self.assertTrue(state["llm_metadata"]["fallback_used"])

    def test_agent_state_does_not_mutate_deterministic_plan(self):
        state = build_agent_state(mode="offline")

        self.assertEqual(len(state["allocations"]), len(state["backlog_items"]))
        self.assertEqual([allocation for allocation in state["allocations"] if allocation["over_capacity"]], [])
        self.assertIn("agent_analysis", state)
        self.assertIn("llm_metadata", state)


def _valid_llm_payload():
    return {
        "agent_analysis": {
            "executive_summary": "P3 is the urgent planning concern; P1 and P2 need regulated/data foundations.",
            "project_assessments": {
                "P1": "Keep audit and risk decisions visible.",
                "P2": "Protect data quality before forecasting.",
                "P3": "Resolve timeline conflict before committing.",
            },
            "priority_analysis": ["Keep P3 discovery critical."],
            "allocation_analysis": ["Current specialist allocation is credible."],
            "risk_analysis": ["P3 timeline remains the main risk."],
            "product_owner_questions": ["Which P3 pilot date is real?"],
        },
        "recommendations": [
            {
                "title": "Escalate P3 timeline decision",
                "project_id": "P3",
                "affected_item_ids": ["P3-BL-001"],
                "affected_member_ids": ["sofia-almeida"],
                "rationale": "Conflicting dates make sprint planning unstable.",
                "expected_impact": "Cleaner MVP scope and less rework.",
                "confidence": 0.92,
            }
        ],
        "approval_queue": [
            {
                "action_type": "change_priority",
                "project_id": "P3",
                "affected_item_ids": ["P3-BL-001"],
                "affected_member_ids": ["sofia-almeida"],
                "before": {"priority": "high"},
                "after": {"priority": "critical"},
                "rationale": "The timeline inconsistency should be handled before delivery tasks.",
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
