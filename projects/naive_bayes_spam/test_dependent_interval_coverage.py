import copy
import unittest

from projects.naive_bayes_spam.dependent_interval_coverage import (
    ar1_bartlett_hac_interval_coverage_certificate,
    ar1_bartlett_hac_interval_coverage_report,
    ar1_mean_interval_coverage_certificate,
    ar1_mean_interval_coverage_report,
)


class DependentIntervalCoverageTests(unittest.TestCase):
    def test_positive_autocorrelation_exposes_naive_interval_undercoverage(self):
        report = ar1_mean_interval_coverage_report(.8, 1.0, 40, 2000, 17)
        self.assertGreater(
            report["exact_finite_window_mean_variance"],
            report["naive_iid_same_marginal_mean_variance"],
        )
        self.assertLess(report["effective_independent_sample_size"], 40)
        self.assertLess(report["naive_iid_interval_coverage"], .80)
        self.assertGreater(report["exact_finite_window_interval_coverage"], .90)
        self.assertGreater(report["coverage_gap_exact_minus_naive"], .15)
        self.assertTrue(ar1_mean_interval_coverage_certificate(.8, 1.0, 40, 2000, 17, 1.96, report))

    def test_iid_limit_matches_finite_window_formula_and_certificate_rejects_tampering(self):
        report = ar1_mean_interval_coverage_report(0.0, 2.0, 20, 400, 3)
        self.assertAlmostEqual(
            report["exact_finite_window_mean_variance"],
            report["naive_iid_same_marginal_mean_variance"],
        )
        self.assertAlmostEqual(report["effective_independent_sample_size"], 20)
        altered = copy.deepcopy(report)
        altered["naive_iid_interval_coverage"] = 1.0
        self.assertFalse(ar1_mean_interval_coverage_certificate(0.0, 2.0, 20, 400, 3, 1.96, altered))

    def test_invalid_stationarity_and_contract_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            ar1_mean_interval_coverage_report(1.0, 1.0, 20)
        with self.assertRaises(ValueError):
            ar1_mean_interval_coverage_report(.2, 0.0, 20)
        with self.assertRaises(ValueError):
            ar1_mean_interval_coverage_report(.2, 1.0, 1)

    def test_declared_bartlett_hac_recovers_some_coverage_without_oracle_parameters(self):
        report = ar1_bartlett_hac_interval_coverage_report(.8, 1.0, 80, 8, 2000, 29)
        self.assertLess(report["naive_sample_variance_interval_coverage"], .80)
        self.assertGreater(report["bartlett_hac_interval_coverage"], .70)
        self.assertGreater(report["coverage_gain_hac_minus_naive"], .20)
        self.assertEqual(report["nonpositive_bartlett_estimate_count"], 0)
        self.assertTrue(
            ar1_bartlett_hac_interval_coverage_certificate(.8, 1.0, 80, 8, 2000, 29, 1.96, report),
        )

    def test_bartlett_certificate_rejects_tampering_and_invalid_bandwidth(self):
        report = ar1_bartlett_hac_interval_coverage_report(0.0, 1.0, 20, 0, 400, 5)
        self.assertLess(
            abs(report["naive_sample_variance_interval_coverage"] - report["bartlett_hac_interval_coverage"]),
            .02,
        )
        altered = copy.deepcopy(report)
        altered["bartlett_bandwidth"] = 1
        self.assertFalse(ar1_bartlett_hac_interval_coverage_certificate(0.0, 1.0, 20, 0, 400, 5, 1.96, altered))
        with self.assertRaises(ValueError):
            ar1_bartlett_hac_interval_coverage_report(.2, 1.0, 20, 20)


if __name__ == "__main__":
    unittest.main()
