import copy
import unittest

from projects.floating_point_museum.multidimensional_integration import (
    EXACT_INTEGRAL,
    unit_square_integration_certificate,
    unit_square_integration_report,
)


class MultidimensionalIntegrationTests(unittest.TestCase):
    def test_midpoint_grid_has_known_two_dimensional_value_and_error(self):
        report = unit_square_integration_report(2, 8, 17)
        self.assertEqual(report["exact_integral"], EXACT_INTEGRAL)
        self.assertEqual(report["grid_midpoint"]["sample_count"], 4)
        self.assertAlmostEqual(report["grid_midpoint"]["estimate"], 0.8125)
        self.assertAlmostEqual(report["grid_midpoint"]["absolute_error"], 1 / 48)

    def test_fixed_seed_replays_monte_carlo_and_certificate(self):
        first = unit_square_integration_report(4, 40, 123)
        second = unit_square_integration_report(4, 40, 123)
        self.assertEqual(first, second)
        self.assertTrue(unit_square_integration_certificate(4, 40, 123, first))
        altered = copy.deepcopy(first)
        altered["monte_carlo"]["estimated_standard_error"] = 0.0
        self.assertFalse(unit_square_integration_certificate(4, 40, 123, altered))

    def test_known_integrand_variance_exposes_theoretical_and_sample_uncertainty(self):
        report = unit_square_integration_report(2, 8, 17)
        monte_carlo = report["monte_carlo"]
        self.assertAlmostEqual(monte_carlo["theoretical_integrand_variance"], 31 / 180)
        self.assertAlmostEqual(monte_carlo["theoretical_standard_error"], (31 / (180 * 8)) ** 0.5)
        self.assertAlmostEqual(
            monte_carlo["error_in_theoretical_standard_errors"],
            monte_carlo["signed_error"] / monte_carlo["theoretical_standard_error"],
        )
        one_draw = unit_square_integration_report(2, 1, 17)["monte_carlo"]
        self.assertIsNone(one_draw["unbiased_sample_variance"])
        self.assertIsNone(one_draw["estimated_standard_error"])
        self.assertGreater(one_draw["theoretical_standard_error"], 0.0)

    def test_grid_refinement_improves_this_smooth_benchmark(self):
        coarse = unit_square_integration_report(2, 12, 1)
        fine = unit_square_integration_report(8, 12, 1)
        self.assertLess(fine["grid_midpoint"]["absolute_error"], coarse["grid_midpoint"]["absolute_error"])

    def test_contract_rejects_bad_budgets_and_seed(self):
        with self.assertRaisesRegex(ValueError, "grid_subdivisions"):
            unit_square_integration_report(0, 10, 1)
        with self.assertRaisesRegex(ValueError, "monte_carlo_samples"):
            unit_square_integration_report(2, 0, 1)
        with self.assertRaisesRegex(ValueError, "seed"):
            unit_square_integration_report(2, 10, True)
