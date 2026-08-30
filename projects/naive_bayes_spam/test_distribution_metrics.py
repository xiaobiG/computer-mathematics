import unittest
from math import inf

from projects.naive_bayes_spam.distribution_metrics import (
    cross_entropy,
    entropy,
    information_report,
    information_report_certificate,
    kl_divergence,
)


class DistributionMetricTests(unittest.TestCase):
    def test_cross_entropy_decomposes_into_entropy_and_kl_divergence(self):
        actual = {"spam": 0.2, "ham": 0.8}
        predicted = {"spam": 0.3, "ham": 0.7}
        report = information_report(actual, predicted)
        self.assertGreater(kl_divergence(actual, predicted), 0.0)
        self.assertAlmostEqual(report["cross_entropy"], report["entropy"] + report["kl_divergence"])
        self.assertAlmostEqual(report["decomposition_residual"], 0.0)
        self.assertTrue(information_report_certificate(actual, predicted, report)["valid"])

    def test_information_certificate_rejects_a_tampered_finite_report(self):
        actual = {"spam": 0.2, "ham": 0.8}
        predicted = {"spam": 0.3, "ham": 0.7}
        report = information_report(actual, predicted)
        tampered = dict(report)
        tampered["kl_divergence"] += 0.1
        self.assertFalse(information_report_certificate(actual, predicted, tampered)["valid"])

    def test_matching_distribution_has_zero_kl_and_cross_entropy_equal_to_entropy(self):
        distribution = {"yes": 0.5, "no": 0.5}
        self.assertAlmostEqual(kl_divergence(distribution, distribution), 0.0)
        self.assertAlmostEqual(cross_entropy(distribution, distribution), entropy(distribution))

    def test_zero_predicted_probability_has_infinite_penalty_and_contracts_are_checked(self):
        actual, predicted = {"yes": 1.0, "no": 0.0}, {"yes": 0.0, "no": 1.0}
        self.assertEqual(cross_entropy(actual, predicted), inf)
        self.assertEqual(kl_divergence(actual, predicted), inf)
        self.assertTrue(information_report_certificate(actual, predicted, information_report(actual, predicted))["valid"])
        with self.assertRaises(ValueError):
            entropy({"yes": 0.6, "no": 0.6})
        with self.assertRaises(ValueError):
            cross_entropy({"yes": 1.0}, {"no": 1.0})


if __name__ == "__main__":
    unittest.main()
