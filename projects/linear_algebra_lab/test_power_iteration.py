import unittest
from math import sqrt

from projects.linear_algebra_lab.power_iteration import dominant_eigenpair


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
