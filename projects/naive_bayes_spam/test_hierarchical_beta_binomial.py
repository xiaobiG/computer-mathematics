import copy
import unittest

from projects.naive_bayes_spam.hierarchical_beta_binomial import (
    hierarchical_beta_binomial_certificate,
    hierarchical_beta_binomial_report,
)


class HierarchicalBetaBinomialTests(unittest.TestCase):
    def setUp(self):
        self.groups = [
            {"group_id": "small", "successes": 1, "failures": 0},
            {"group_id": "large", "successes": 80, "failures": 20},
        ]

    def test_shared_prior_partially_pools_small_group_and_replays(self):
        report = hierarchical_beta_binomial_report(self.groups, 2, 2)
        small, large = report["groups"]
        self.assertEqual(small["mle"], 1.0)
        self.assertAlmostEqual(small["posterior"]["mean"], .6)
        self.assertLess(small["partial_pooling"]["data_weight"], large["partial_pooling"]["data_weight"])
        self.assertTrue(hierarchical_beta_binomial_certificate(self.groups, 2, 2, report))

    def test_certificate_and_contract_reject_changed_group_or_hyperparameters(self):
        report = hierarchical_beta_binomial_report(self.groups, 2, 2)
        altered = copy.deepcopy(report)
        altered["groups"][0]["posterior"]["mean"] = 1.0
        self.assertFalse(hierarchical_beta_binomial_certificate(self.groups, 2, 2, altered))
        with self.assertRaises(ValueError):
            hierarchical_beta_binomial_report([self.groups[0]], 2, 2)
        with self.assertRaises(ValueError):
            hierarchical_beta_binomial_report(self.groups, 0, 2)


if __name__ == "__main__":
    unittest.main()
