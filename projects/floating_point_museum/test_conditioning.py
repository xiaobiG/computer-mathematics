import unittest

from projects.floating_point_museum.conditioning import (
    condition_number_infinity_2x2,
    inverse_2x2,
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
        self.assertAlmostEqual(report["baseline_solution"][0], 1.0, places=8)
        self.assertAlmostEqual(report["baseline_solution"][1], 1.0, places=8)
        self.assertAlmostEqual(report["perturbed_solution"][0], 0.0, places=8)
        self.assertAlmostEqual(report["perturbed_solution"][1], 2.0, places=8)

    def test_residual_can_be_small_while_solution_has_changed(self):
        matrix = [[1.0, 1.0], [1.0, 1.000001]]
        self.assertLess(max(abs(value) for value in residual(matrix, [0.0, 2.0], [2.0, 2.000002])), 1e-12)

    def test_singular_and_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            inverse_2x2([[1.0, 1.0], [1.0, 1.0]])
        with self.assertRaises(ValueError):
            condition_number_infinity_2x2([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        with self.assertRaises(ValueError):
            perturbation_report([[1.0, 0.0], [0.0, 1.0]], [0.0, 0.0], [1.0, 0.0])
