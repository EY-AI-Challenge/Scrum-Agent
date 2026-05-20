import json
import unittest
from pathlib import Path

from scrum_agent.core.schema import DemoState
from scrum_agent.services.demo_state import build_demo_state


class DemoStateTest(unittest.TestCase):
    def setUp(self):
        self.state: DemoState = build_demo_state()

    def test_loads_core_demo_entities(self):
        self.assertEqual(
            sorted(self.state.keys()),
            [
                "allocations",
                "backlog_items",
                "insights",
                "metadata",
                "projects",
                "risks",
                "sprint_plans",
                "team_members",
            ],
        )
        self.assertEqual(len(self.state["projects"]), 3)
        self.assertEqual(len(self.state["team_members"]), 15)
        self.assertGreaterEqual(len(self.state["backlog_items"]), 21)
        self.assertEqual(len(self.state["allocations"]), len(self.state["backlog_items"]))

    def test_detects_patient_timeline_risk(self):
        critical_risks = {
            risk["risk_id"]
            for risk in self.state["risks"]
            if risk["severity"] == "critical"
        }
        self.assertIn("RISK-P3-DEADLINE", critical_risks)

    def test_allocates_key_domain_specialists(self):
        assignments = {
            (allocation["project_id"], allocation["item_id"]): allocation["member_id"]
            for allocation in self.state["allocations"]
        }
        self.assertEqual(assignments[("P1", "P1-BL-003")], "nuno-figueiredo")
        self.assertEqual(assignments[("P1", "P1-BL-005")], "tiago-fernandes")
        self.assertEqual(assignments[("P2", "P2-BL-002")], "marta-carvalho")
        self.assertEqual(assignments[("P2", "P2-BL-003")], "beatriz-gomes")
        self.assertEqual(assignments[("P3", "P3-BL-003")], "luis-teixeira")

    def test_no_unflagged_capacity_overload(self):
        overloaded = [
            allocation for allocation in self.state["allocations"]
            if allocation["over_capacity"]
        ]
        self.assertEqual(overloaded, [])

    def test_json_contract_example_is_usable_as_mock(self):
        contract_path = Path("docs/data_contract/demo_state.example.json")
        example_state = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(sorted(example_state.keys()), sorted(self.state.keys()))
        self.assertEqual(len(example_state["projects"]), 3)
        self.assertEqual(len(example_state["team_members"]), 15)
        self.assertEqual(len(example_state["backlog_items"]), len(self.state["backlog_items"]))
        self.assertEqual(len(example_state["allocations"]), len(self.state["allocations"]))


if __name__ == "__main__":
    unittest.main()
