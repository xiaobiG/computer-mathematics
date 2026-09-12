import math
import unittest
from dataclasses import replace

from projects.floating_point_museum.integration import (
    adaptive_simpson,
    adaptive_simpson_certificate,
    composite_simpson,
    composite_trapezoid,
    refinement_report,
)


class IntegrationTests(unittest.TestCase):
    def test_smooth_sine_exhibits_expected_refinement_orders(self):
        report = refinement_report(math.sin, 0.0, math.pi, 2.0, 8)
        self.assertAlmostEqual(report.trapezoid_error_ratio, 4.0, delta=0.1)
        self.assertAlmostEqual(report.simpson_error_ratio, 16.0, delta=0.5)

    def test_simpson_integrates_cubics_exactly_on_a_valid_grid(self):
        self.assertAlmostEqual(composite_simpson(lambda x: x ** 3, 0.0, 1.0, 2), 0.25)
        self.assertLess(abs(composite_trapezoid(lambda x: x ** 3, 0.0, 1.0, 2) - 0.25), 0.1)

    def test_adaptive_simpson_reports_a_met_budget_for_a_smooth_integrand(self):
        report = adaptive_simpson(math.sin, 0.0, math.pi, absolute_tolerance=1e-10, max_evaluations=500)
        self.assertTrue(report.converged)
        self.assertTrue(report.certificate["valid"])
        self.assertLess(abs(report.estimate - 2.0), 1e-10)
        self.assertGreater(report.accepted_intervals, 1)
        self.assertGreater(report.evaluations, 3)
        self.assertLessEqual(report.evaluations, report.max_evaluations)
        self.assertTrue(adaptive_simpson_certificate(math.sin, 0.0, math.pi, report))

    def test_adaptive_simpson_reports_depth_exhaustion_instead_of_claiming_success(self):
        report = adaptive_simpson(math.sin, 0.0, math.pi, absolute_tolerance=1e-14, max_depth=0)
        self.assertFalse(report.converged)
        self.assertFalse(report.certificate["valid"])
        self.assertFalse(report.certificate["stopped_without_depth_limit"])

    def test_adaptive_simpson_stops_at_function_call_budget_with_trace(self):
        report = adaptive_simpson(math.sin, 0.0, math.pi, absolute_tolerance=1e-12, max_evaluations=3)
        self.assertFalse(report.converged)
        self.assertTrue(report.evaluation_budget_exhausted)
        self.assertEqual(report.evaluations, 3)
        self.assertEqual(report.leaves[0].status, "evaluation_budget_exhausted")
        self.assertIsNone(report.estimated_error)
        self.assertFalse(report.certificate["valid"])
        self.assertTrue(adaptive_simpson_certificate(math.sin, 0.0, math.pi, report))
        self.assertFalse(adaptive_simpson_certificate(math.sin, 0.0, math.pi, replace(report, evaluations=4)))

    def test_rejects_invalid_grids_and_nonfinite_integrand_values(self):
        with self.assertRaises(ValueError):
            composite_simpson(math.sin, 0.0, 1.0, 3)
        with self.assertRaises(ValueError):
            composite_trapezoid(lambda _: float("nan"), 0.0, 1.0, 4)
        with self.assertRaises(ValueError):
            refinement_report(math.sin, 0.0, math.pi, 2.0, 3)
        with self.assertRaises(ValueError):
            adaptive_simpson(math.sin, 0.0, 1.0, absolute_tolerance=0.0)
        with self.assertRaises(ValueError):
            adaptive_simpson(math.sin, 0.0, 1.0, max_evaluations=2)
