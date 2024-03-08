import copy
import json
from pathlib import Path
import unittest
from main import plan


class PlannerTests(unittest.TestCase):
    def setUp(self): self.data = json.loads(Path(__file__).with_name("example.json").read_text())

    def test_optimal_feasible_solution(self):
        out = plan(self.data)["itinerary"]
        self.assertEqual(out["score"], 20)
        self.assertEqual(out["total_cents"], 43500)
        self.assertEqual(out["activities"], ["museum", "coastal-walk"])
        self.assertEqual(sum(out["costs"].values()), out["total_cents"])

    def test_infeasible_budget(self):
        self.data["budget_cents"] = 1
        self.assertFalse(plan(self.data)["feasible"])
