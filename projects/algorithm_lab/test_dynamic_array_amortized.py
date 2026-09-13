import copy
import unittest

from projects.algorithm_lab.dynamic_array_amortized import (
    dynamic_array_doubling_certificate,
    dynamic_array_doubling_report,
    dynamic_array_hysteresis_certificate,
    dynamic_array_hysteresis_report,
)


class DynamicArrayAmortizedTests(unittest.TestCase):
    def test_trace_charges_copies_and_proves_every_prefix_bound(self):
        report = dynamic_array_doubling_report([10, 20, 30, 40, 50])
        self.assertEqual([row["copied_cells"] for row in report["append_trace"]], [0, 1, 2, 0, 4])
        self.assertEqual(report["cost_summary"]["actual_total_cost"], 12)
        self.assertTrue(report["cost_summary"]["actual_total_within_amortized_charge"])
        self.assertLessEqual(report["cost_summary"]["maximum_single_amortized_cost"], 3)
        self.assertTrue(dynamic_array_doubling_certificate([10, 20, 30, 40, 50], report))

    def test_certificate_rejects_changed_copy_or_potential_trace(self):
        report = dynamic_array_doubling_report([1, 2, 3])
        altered = copy.deepcopy(report)
        altered["append_trace"][2]["copied_cells"] = 0
        self.assertFalse(dynamic_array_doubling_certificate([1, 2, 3], altered))
        with self.assertRaises(ValueError):
            dynamic_array_doubling_report([float("inf")])

    def test_hysteresis_shrinks_at_quarter_without_losing_amortized_bound(self):
        operations = [
            {"op": "push", "value": 1}, {"op": "push", "value": 2},
            {"op": "push", "value": 3}, {"op": "push", "value": 4},
            {"op": "pop"}, {"op": "pop"}, {"op": "pop"},
            {"op": "push", "value": 5}, {"op": "push", "value": 6},
        ]
        report = dynamic_array_hysteresis_report(operations)
        self.assertEqual([row["copied_cells"] for row in report["operation_trace"]], [0, 1, 2, 0, 0, 0, 1, 0, 2])
        self.assertEqual(report["operation_trace"][6]["capacity_after"], 2)
        self.assertTrue(report["cost_summary"]["actual_total_within_amortized_charge"])
        self.assertLessEqual(report["cost_summary"]["maximum_single_amortized_cost"], 3)
        self.assertTrue(dynamic_array_hysteresis_certificate(operations, report))

    def test_hysteresis_rejects_empty_pop_and_changed_resize_trace(self):
        with self.assertRaises(ValueError):
            dynamic_array_hysteresis_report([{"op": "pop"}])
        operations = [{"op": "push", "value": 1}, {"op": "push", "value": 2}]
        report = dynamic_array_hysteresis_report(operations)
        altered = copy.deepcopy(report)
        altered["operation_trace"][1]["capacity_after"] = 1
        self.assertFalse(dynamic_array_hysteresis_certificate(operations, altered))


if __name__ == "__main__":
    unittest.main()
