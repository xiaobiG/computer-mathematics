import unittest

from projects.naive_bayes_spam.moments import (
    finite_expectation,
    finite_variance,
    total_variance_report,
    welford_population,
)


class MomentTests(unittest.TestCase):
    def test_finite_distribution_mean_and_variance_match_the_definition(self):
        distribution = {1.0: 1 / 3, 3.0: 1 / 3, 5.0: 1 / 3}
        self.assertAlmostEqual(finite_expectation(distribution), 3.0)
        self.assertAlmostEqual(finite_variance(distribution), 8 / 3)

    def test_welford_matches_two_pass_population_formula(self):
        mean, variance = welford_population([1.0, 3.0, 5.0])
        self.assertAlmostEqual(mean, 3.0)
        self.assertAlmostEqual(variance, 8 / 3)

    def test_total_variance_separates_within_and_between_group_uncertainty(self):
        report = total_variance_report(
            {"low": 0.25, "high": 0.75},
            {"low": {0.0: 0.5, 2.0: 0.5}, "high": {8.0: 0.5, 10.0: 0.5}},
        )
        self.assertAlmostEqual(report["overall_mean"], 7.0)
        self.assertAlmostEqual(report["within_variance"], 1.0)
        self.assertAlmostEqual(report["between_variance"], 12.0)
        self.assertAlmostEqual(report["total_variance"], 13.0)

    def test_rejects_invalid_probability_mass_and_nonfinite_streams(self):
        with self.assertRaises(ValueError):
            finite_expectation({1.0: 0.2, 2.0: 0.2})
        with self.assertRaises(ValueError):
            welford_population([])
        with self.assertRaises(ValueError):
            total_variance_report({"one": 1.0}, {"two": {0.0: 1.0}})


if __name__ == "__main__":
    unittest.main()
