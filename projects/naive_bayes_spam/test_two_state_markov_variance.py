import copy
import unittest

from projects.naive_bayes_spam.two_state_markov_variance import (
    stationary_two_state_markov_mean_variance_certificate,
    stationary_two_state_markov_mean_variance_report,
)


class TwoStateMarkovVarianceTests(unittest.TestCase):
    def test_positive_correlation_inflates_exact_mean_variance(self):
        report = stationary_two_state_markov_mean_variance_report(.1, .1, 10)
        self.assertAlmostEqual(report["declared_chain"]["stationary_probability_of_one"], .5)
        self.assertAlmostEqual(report["declared_chain"]["second_eigenvalue_rho"], .8)
        self.assertGreater(report["mean_variance"], report["iid_same_marginal_variance"])
        self.assertLess(report["effective_independent_sample_size"], 10)
        self.assertTrue(stationary_two_state_markov_mean_variance_certificate(.1, .1, 10, report))

    def test_zero_correlation_matches_iid_and_certificate_rejects_tampering(self):
        report = stationary_two_state_markov_mean_variance_report(.5, .5, 8)
        self.assertAlmostEqual(report["declared_chain"]["second_eigenvalue_rho"], 0)
        self.assertAlmostEqual(report["mean_variance"], report["iid_same_marginal_variance"])
        altered = copy.deepcopy(report)
        altered["effective_independent_sample_size"] = 7
        self.assertFalse(stationary_two_state_markov_mean_variance_certificate(.5, .5, 8, altered))
        with self.assertRaises(ValueError):
            stationary_two_state_markov_mean_variance_report(0, .5, 8)


if __name__ == "__main__":
    unittest.main()
