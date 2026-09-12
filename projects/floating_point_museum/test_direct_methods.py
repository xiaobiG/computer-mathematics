import copy
import unittest

from projects.floating_point_museum.direct_methods import (
    direct_method_comparison,
    direct_method_comparison_certificate,
)


class DirectMethodTests(unittest.TestCase):
    def setUp(self):
        # The stored right side [1, 2] has an exact mathematical solution near
        # [1, 1].  Eliminating with the tiny first pivot loses that first digit.
        self.matrix = [[1e-20, 1.0], [1.0, 1.0]]
        self.right_side = [1.0, 2.0]
        self.reference_solution = [1.0, 1.0]

    def test_partial_pivoting_avoids_tiny_pivot_failure(self):
        report = direct_method_comparison(self.matrix, self.right_side, self.reference_solution)
        without = report["without_pivoting"]
        pivoted = report["partial_pivoting"]
        self.assertGreater(without["relative_forward_error"], 0.9)
        self.assertLess(pivoted["relative_forward_error"], 1e-12)
        self.assertLess(pivoted["scaled_backward_error"], 1e-12)
        self.assertTrue(report["certificate"]["partial_pivoting_used_a_swap"])
        self.assertTrue(report["certificate"]["partial_pivoting_has_small_backward_error"])
        self.assertTrue(report["certificate"]["partial_pivoting_is_no_worse_in_forward_error"])

    def test_certificate_replays_all_trace_fields(self):
        report = direct_method_comparison(self.matrix, self.right_side, self.reference_solution)
        self.assertTrue(direct_method_comparison_certificate(self.matrix, self.right_side, self.reference_solution, report))
        tampered = copy.deepcopy(report)
        tampered["partial_pivoting"]["trace"][0]["pivot"] = 9.0
        self.assertFalse(direct_method_comparison_certificate(self.matrix, self.right_side, self.reference_solution, tampered))

    def test_rejects_invalid_shape_zero_pivot_and_zero_reference_norm(self):
        with self.assertRaises(ValueError):
            direct_method_comparison([[1.0]], [1.0], [1.0, 1.0])
        with self.assertRaises(ValueError):
            direct_method_comparison([[0.0, 1.0], [0.0, 2.0]], [1.0, 2.0], [1.0, 1.0])
        with self.assertRaises(ValueError):
            direct_method_comparison([[1.0, 0.0], [0.0, 1.0]], [1.0, 1.0], [0.0, 0.0])
