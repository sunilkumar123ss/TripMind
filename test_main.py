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

    def test_required_category_is_enforced(self):
        self.data["required_categories"] = ["spaceflight"]
        self.assertIsNone(plan(self.data)["itinerary"])

    def test_no_two_activities_on_same_day(self):
        self.data["budget_cents"] = 100000
        selected = plan(self.data)["itinerary"]["activities"]
        days = [a["day"] for a in self.data["activities"] if a["id"] in selected]
        self.assertEqual(len(days), len(set(days)))

    def test_non_destination_options_are_excluded(self):
        self.data["flights"][0]["destination"] = "Elsewhere"
        self.assertEqual(plan(self.data)["itinerary"]["flight"], "flight-flex")

    def test_order_does_not_change_tie_break(self):
        other = copy.deepcopy(self.data)
        for key in ("flights","hotels","activities"): other[key].reverse()
        self.assertEqual(plan(self.data)["itinerary"], plan(other)["itinerary"])

    def test_invalid_money_and_duplicate_id_rejected(self):
        self.data["budget_cents"] = True
        with self.assertRaises(ValueError): plan(self.data)
        self.data["budget_cents"] = 50000
        self.data["flights"].append(copy.deepcopy(self.data["flights"][0]))
        with self.assertRaises(ValueError): plan(self.data)
