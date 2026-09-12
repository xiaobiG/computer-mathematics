import unittest
from math import sqrt

from projects.linear_algebra_lab.power_iteration import (
    dominant_eigenpair,
    initialization_sensitivity_certificate,
    initialization_sensitivity_report,
)


class PowerIterationTests(unittest.TestCase):
    def test_finds_dominant_eigenpair_and_reports_small_residual(self):
        eigenvalue, vector, trace = dominant_eigenpair([[2.0, 1.0], [1.0, 3.0]])
        self.assertAlmostEqual(eigenvalue, (5 + sqrt(5)) / 2, places=8)
        self.assertAlmostEqual(sum(value * value for value in vector), 1.0, places=10)
        self.assertLess(trace[-1]["residual_norm"], 1e-10)

    def test_diagonal_matrix_converges_to_largest_magnitude_direction(self):
        eigenvalue, vector, _ = dominant_eigenpair([[5.0, 0.0], [0.0, 2.0]])
        self.assertAlmostEqual(eigenvalue, 5.0, places=8)
        self.assertGreater(abs(vector[0]), 0.999999)

    def test_rejects_invalid_matrices_and_reports_nonconvergence(self):
        with self.assertRaises(ValueError):
            dominant_eigenpair([[1.0, 2.0], [0.0, 1.0]])
        with self.assertRaises(ValueError):
            dominant_eigenpair([[0.0, 0.0], [0.0, 0.0]])
        with self.assertRaises(RuntimeError):
            dominant_eigenpair([[2.0, 1.0], [1.0, 3.0]], residual_tol=1e-30, max_steps=1)

    def test_small_residual_with_a_blind_initial_vector_need_not_be_the_dominant_eigenpair(self):
        matrix = [[5.0, 0.0], [0.0, 2.0]]
        report = initialization_sensitivity_report(matrix, [1.0, 1.0], [0.0, 1.0])
        self.assertTrue(report["both_paths_have_small_residual"])
        self.assertTrue(report["primary_path_has_larger_magnitude_eigenvalue"])
        self.assertAlmostEqual(report["primary"]["eigenvalue"], 5.0)
        self.assertAlmostEqual(report["blind"]["eigenvalue"], 2.0)
        self.assertTrue(initialization_sensitivity_certificate(matrix, [1.0, 1.0], [0.0, 1.0], report))
        tampered = dict(report)
        tampered["primary_path_has_larger_magnitude_eigenvalue"] = False
        self.assertFalse(initialization_sensitivity_certificate(matrix, [1.0, 1.0], [0.0, 1.0], tampered))

    def test_rejects_zero_or_wrong_sized_initial_vector(self):
        with self.assertRaises(ValueError):
            dominant_eigenpair([[5.0, 0.0], [0.0, 2.0]], initial_vector=[0.0, 0.0])
        with self.assertRaises(ValueError):
            dominant_eigenpair([[5.0, 0.0], [0.0, 2.0]], initial_vector=[1.0])
