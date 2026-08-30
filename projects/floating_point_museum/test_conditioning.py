import unittest

from projects.floating_point_museum.conditioning import (
    condition_number_infinity_2x2,
    inverse_2x2,
    matrix_perturbation_report,
    normwise_backward_error,
    perturbation_report,
    residual,
)


class ConditioningTests(unittest.TestCase):
    def test_identity_has_unit_infinity_condition_number(self):
        self.assertEqual(condition_number_infinity_2x2([[1.0, 0.0], [0.0, 1.0]]), 1.0)

    def test_near_parallel_lines_amplify_a_tiny_rhs_change(self):
        epsilon = 1e-6
        report = perturbation_report(
            [[1.0, 1.0], [1.0, 1.0 + epsilon]],
            [2.0, 2.0 + epsilon],
            [2.0, 2.0 + 2.0 * epsilon],
        )
        self.assertGreater(report["condition_number"], 1e6)
        self.assertLess(report["relative_rhs_change"], 1e-6)
        self.assertGreater(report["relative_solution_change"], 0.9)
        self.assertLess(report["perturbed_residual_norm"], 1e-10)
        self.assertGreater(report["relative_amplification"], 1e6)
        self.assertLessEqual(report["relative_solution_change"], report["condition_number_bound"])
        self.assertTrue(report["certificate"]["observed_change_is_bounded_by_condition_number"])
        self.assertTrue(report["certificate"]["perturbed_solution_has_small_scaled_residual"])
        self.assertAlmostEqual(report["baseline_solution"][0], 1.0, places=8)
        self.assertAlmostEqual(report["baseline_solution"][1], 1.0, places=8)
        self.assertAlmostEqual(report["perturbed_solution"][0], 0.0, places=8)
        self.assertAlmostEqual(report["perturbed_solution"][1], 2.0, places=8)

    def test_residual_can_be_small_while_solution_has_changed(self):
        matrix = [[1.0, 1.0], [1.0, 1.000001]]
        self.assertLess(max(abs(value) for value in residual(matrix, [0.0, 2.0], [2.0, 2.000002])), 1e-12)
        self.assertLess(normwise_backward_error(matrix, [0.0, 2.0], [2.0, 2.000002]), 1e-12)

    def test_matrix_perturbation_uses_the_denominator_margin_bound(self):
        report = matrix_perturbation_report(
            [[1.0, 0.0], [0.0, 1.0]],
            [[1.001, 0.0], [0.0, 1.0]],
            [1.0, 2.0],
        )
        self.assertAlmostEqual(report["relative_matrix_change"], 0.001)
        # ||x||_inf is 2 for [1, 2], while only the first coordinate moves.
        self.assertAlmostEqual(report["relative_solution_change"], 1.0 / (2.0 * 1001.0))
        self.assertLess(report["relative_solution_change"], report["matrix_perturbation_bound"])
        self.assertTrue(report["certificate"]["bound_has_positive_margin"])
        self.assertTrue(report["certificate"]["observed_change_is_bounded_by_matrix_perturbation"])
        self.assertTrue(report["certificate"]["perturbed_system_residual_is_small"])

    def test_matrix_perturbation_marks_a_bound_without_margin_as_inapplicable(self):
        report = matrix_perturbation_report(
            [[1.0, 0.0], [0.0, 1.0]],
            [[2.0, 0.0], [0.0, 1.0]],
            [1.0, 2.0],
        )
        self.assertFalse(report["certificate"]["bound_has_positive_margin"])
        self.assertFalse(report["certificate"]["observed_change_is_bounded_by_matrix_perturbation"])

    def test_singular_and_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            inverse_2x2([[1.0, 1.0], [1.0, 1.0]])
        with self.assertRaises(ValueError):
            condition_number_infinity_2x2([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        with self.assertRaises(ValueError):
            perturbation_report([[1.0, 0.0], [0.0, 1.0]], [0.0, 0.0], [1.0, 0.0])
