import math
import cmath
from copy import deepcopy
import unittest

from projects.floating_point_museum.differentiation import (
    central_difference,
    central_difference_report,
    complex_step_comparison_certificate,
    complex_step_comparison_report,
    complex_step_difference,
    finite_difference_stencil_comparison,
    forward_difference,
)


class DifferentiationTests(unittest.TestCase):
    def test_sine_step_scan_exposes_second_order_trend_and_roundoff_rebound(self):
        report = central_difference_report(math.sin, math.cos, 1.0)
        self.assertTrue(report["certificate"]["coarse_steps_show_second_order_trend"])
        self.assertTrue(report["certificate"]["small_steps_rebound_after_best"])
        self.assertTrue(report["certificate"]["valid"])
        self.assertLess(report["best"].absolute_error, 1e-10)

    def test_central_difference_handles_a_smooth_function_and_rejects_bad_contracts(self):
        self.assertAlmostEqual(central_difference(math.exp, 0.0, 1e-5), 1.0, places=9)
        self.assertAlmostEqual(forward_difference(math.exp, 0.0, 1e-5), 1.0, places=4)
        with self.assertRaises(ValueError):
            central_difference(math.log, 1e-6, 1e-5)
        with self.assertRaises(ValueError):
            central_difference_report(math.sin, math.cos, 1.0, [1, 2])
        with self.assertRaises(ValueError):
            central_difference(lambda _: float("nan"), 0.0, 1e-3)

    def test_same_step_shows_centered_accuracy_interior_and_one_sided_boundary(self):
        interior = finite_difference_stencil_comparison(math.exp, math.exp, 0.0, 0.1)
        self.assertTrue(interior["central_available"])
        self.assertLess(interior["central"].absolute_error, interior["forward"].absolute_error)

        boundary = finite_difference_stencil_comparison(math.log, lambda value: 1.0 / value, 1e-6, 1e-5)
        self.assertFalse(boundary["central_available"])
        self.assertIsNone(boundary["central"])
        self.assertGreater(boundary["forward"].absolute_error, 0.0)

    def test_complex_step_avoids_real_subtraction_only_for_declared_complex_extension(self):
        report = complex_step_comparison_report(
            math.sin, cmath.sin, math.cos, point=1.0, step=1e-16,
        )
        self.assertTrue(report["certificate"]["valid"])
        self.assertLess(report["complex_step"].absolute_error, report["central"].absolute_error)
        self.assertTrue(complex_step_comparison_certificate(
            math.sin, cmath.sin, math.cos, 1.0, 1e-16, report,
        ))

        tampered = deepcopy(report)
        tampered["complex_step"] = tampered["central"]
        self.assertFalse(complex_step_comparison_certificate(
            math.sin, cmath.sin, math.cos, 1.0, 1e-16, tampered,
        ))

        with self.assertRaises(ValueError):
            complex_step_difference(math.sin, 1.0, 1e-16)
        with self.assertRaises(ValueError):
            complex_step_difference(lambda _: complex(float("inf"), 0.0), 1.0, 1e-16)


if __name__ == "__main__":
    unittest.main()
