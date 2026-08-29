import math
import unittest

from projects.floating_point_museum.integration import composite_simpson, composite_trapezoid, refinement_report


class IntegrationTests(unittest.TestCase):
    def test_smooth_sine_exhibits_expected_refinement_orders(self):
        report = refinement_report(math.sin, 0.0, math.pi, 2.0, 8)
        self.assertAlmostEqual(report.trapezoid_error_ratio, 4.0, delta=0.1)
        self.assertAlmostEqual(report.simpson_error_ratio, 16.0, delta=0.5)

    def test_simpson_integrates_cubics_exactly_on_a_valid_grid(self):
        self.assertAlmostEqual(composite_simpson(lambda x: x ** 3, 0.0, 1.0, 2), 0.25)
        self.assertLess(abs(composite_trapezoid(lambda x: x ** 3, 0.0, 1.0, 2) - 0.25), 0.1)

    def test_rejects_invalid_grids_and_nonfinite_integrand_values(self):
        with self.assertRaises(ValueError):
            composite_simpson(math.sin, 0.0, 1.0, 3)
        with self.assertRaises(ValueError):
            composite_trapezoid(lambda _: float("nan"), 0.0, 1.0, 4)
        with self.assertRaises(ValueError):
            refinement_report(math.sin, 0.0, math.pi, 2.0, 3)
