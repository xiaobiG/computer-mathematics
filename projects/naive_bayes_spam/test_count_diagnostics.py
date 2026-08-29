import math
import unittest

from projects.naive_bayes_spam.count_diagnostics import count_diagnostics


class CountDiagnosticsTests(unittest.TestCase):
    def test_report_includes_mean_variance_and_poisson_zero_expectation(self):
        report = count_diagnostics([0, 1, 2])
        self.assertEqual(report.mean, 1.0)
        self.assertEqual(report.sample_variance, 1.0)
        self.assertEqual(report.variance_to_mean, 1.0)
        self.assertEqual(report.zero_fraction, 1 / 3)
        self.assertAlmostEqual(report.poisson_zero_fraction_at_mean, math.exp(-1))

    def test_mixed_rates_show_overdispersion_without_claiming_a_full_model_test(self):
        report = count_diagnostics([0, 0, 0, 10, 10, 10])
        self.assertGreater(report.variance_to_mean, 1.0)
        self.assertGreater(report.zero_fraction, report.poisson_zero_fraction_at_mean)

    def test_rejects_small_negative_fractional_and_boolean_counts(self):
        for counts in ([1], [0, -1], [0, 1.5], [True, 0]):
            with self.assertRaises(ValueError):
                count_diagnostics(counts)  # type: ignore[arg-type]
