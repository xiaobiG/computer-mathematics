import copy
import unittest

from projects.algorithm_lab.dynamic_array_amortized import (
    dynamic_array_doubling_certificate,
    dynamic_array_doubling_report,
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


if __name__ == "__main__":
    unittest.main()
