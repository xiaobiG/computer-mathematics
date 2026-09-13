import copy
import unittest

from projects.floating_point_museum.stability import (
    quadratic_scaling_report,
    quadratic_scaling_report_certificate,
    quadratic_stability_report,
    quadratic_stability_report_certificate,
    scale_quadratic_coefficients,
    scaled_stable_quadratic_roots,
    stable_quadratic_roots,
)


class StabilityTests(unittest.TestCase):
    def test_stable_formula_recovers_the_small_root_lost_to_cancellation(self):
        report = quadratic_stability_report(1.0, 1e8, 1.0)
        self.assertTrue(report["certificate"]["stable_formula_is_no_worse_for_small_root"])
        self.assertTrue(report["certificate"]["stable_small_root_has_high_accuracy"])
        self.assertTrue(report["certificate"]["direct_formula_exposes_cancellation"])
        self.assertGreater(report["direct_small_root_relative_error"], 1e-3)
        self.assertLess(report["stable_small_root_relative_error"], 1e-12)
        self.assertTrue(quadratic_stability_report_certificate(1.0, 1e8, 1.0, report))

    def test_stability_certificate_rejects_a_changed_error_or_conclusion(self):
        report = quadratic_stability_report(1.0, 1e8, 1.0)
        tampered = copy.deepcopy(report)
        tampered["stable_small_root_relative_error"] = 1.0
        self.assertFalse(quadratic_stability_report_certificate(1.0, 1e8, 1.0, tampered))
        tampered = copy.deepcopy(report)
        tampered["certificate"]["direct_formula_exposes_cancellation"] = False
        self.assertFalse(quadratic_stability_report_certificate(1.0, 1e8, 1.0, tampered))

    def test_double_root_and_invalid_quadratics_have_explicit_contracts(self):
        self.assertEqual(stable_quadratic_roots(1.0, -2.0, 1.0), (1.0, 1.0))
        with self.assertRaises(ValueError):
            quadratic_stability_report(0.0, 1.0, 1.0)
        with self.assertRaises(ValueError):
            quadratic_stability_report(1.0, 0.0, 1.0)

    def test_discriminant_overflow_is_rejected_before_it_can_masquerade_as_a_root(self):
        with self.assertRaisesRegex(ValueError, "discriminant must be finite"):
            quadratic_stability_report(1.0, 1e308, 1.0)
        with self.assertRaisesRegex(ValueError, "discriminant must be finite"):
            stable_quadratic_roots(1.0, -1e308, 1.0)

    def test_auditable_scaling_recovers_a_finite_path_without_dropping_terms(self):
        report = quadratic_scaling_report(1.0, 1e308, 1.0)
        self.assertFalse(report["certificate"]["unscaled_binary64_discriminant_is_finite"])
        self.assertTrue(report["certificate"]["scaling_preserved_nonzero_coefficients"])
        self.assertTrue(report["certificate"]["scaled_coefficients_are_bounded_by_one"])
        self.assertFalse(report["certificate"]["automatic_production_solver_claim"])
        self.assertEqual(report["scaled_coefficients"], (1e-308, 1.0, 1e-308))
        self.assertLess(report["scaled_small_root_relative_error"], 1e-12)
        self.assertTrue(quadratic_scaling_report_certificate(1.0, 1e308, 1.0, report))
        self.assertEqual(scaled_stable_quadratic_roots(1.0, 1e308, 1.0)[0], report["scaled_stable_roots"])

    def test_scaling_rejects_a_nonzero_term_that_would_underflow_away(self):
        with self.assertRaisesRegex(ValueError, "underflowed a nonzero term"):
            scale_quadratic_coefficients(1.0, 1e308, 5e-324)
