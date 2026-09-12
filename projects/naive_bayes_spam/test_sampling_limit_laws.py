import unittest

from projects.naive_bayes_spam.sampling_limit_laws import bernoulli_mean_report, sample_size_scaling_report


class SamplingLimitLawTests(unittest.TestCase):
    def test_repeated_bernoulli_means_match_the_known_scale_and_plausible_coverage(self):
        report = bernoulli_mean_report(0.35, sample_size=100, trials=4000, seed=7)
        self.assertTrue(report["certificate"]["mean_is_close_on_repeated_trials"])
        self.assertTrue(report["certificate"]["empirical_standard_error_matches_theory"])
        self.assertTrue(report["certificate"]["normal_coverage_is_plausible_for_this_bernoulli_setting"])

    def test_standard_error_shrinks_at_inverse_square_root_scale(self):
        report = sample_size_scaling_report(0.5, 25, 100, trials=4000, seed=11)
        self.assertAlmostEqual(report["expected_standard_error_ratio"], 2.0)
        self.assertTrue(report["certificate"]["larger_sample_has_smaller_empirical_standard_error"])
        self.assertTrue(report["certificate"]["observed_ratio_matches_inverse_sqrt_scaling"])

    def test_invalid_probability_and_sample_size_contracts_are_rejected(self):
        with self.assertRaises(ValueError):
            bernoulli_mean_report(0.0, 20)
        with self.assertRaises(ValueError):
            bernoulli_mean_report(0.5, 1)
        with self.assertRaises(ValueError):
            sample_size_scaling_report(0.5, 100, 25)
