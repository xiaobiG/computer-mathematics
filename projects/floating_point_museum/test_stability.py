import unittest

from projects.floating_point_museum.stability import (
    quadratic_stability_report,
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

    def test_double_root_and_invalid_quadratics_have_explicit_contracts(self):
        self.assertEqual(stable_quadratic_roots(1.0, -2.0, 1.0), (1.0, 1.0))
        with self.assertRaises(ValueError):
            quadratic_stability_report(0.0, 1.0, 1.0)
        with self.assertRaises(ValueError):
            quadratic_stability_report(1.0, 0.0, 1.0)
