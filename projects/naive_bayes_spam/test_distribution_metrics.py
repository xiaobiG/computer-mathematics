import unittest
from math import inf

from projects.naive_bayes_spam.distribution_metrics import (
    categorical_cross_entropy_from_logits,
    cross_entropy,
    entropy,
    information_report,
    information_report_certificate,
    kl_divergence,
    logit_cross_entropy_certificate,
    logit_cross_entropy_report,
    log_softmax,
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

    def test_log_sum_exp_cross_entropy_stays_finite_for_extreme_logits(self):
        logits = [1000.0, -1000.0]
        report = logit_cross_entropy_report(logits, 1)
        self.assertAlmostEqual(categorical_cross_entropy_from_logits(logits, 1), 2000.0)
        self.assertAlmostEqual(sum(__import__("math").exp(value) for value in log_softmax(logits)), 1.0)
        self.assertAlmostEqual(report["log_probability_normalizer"], 0.0)
        self.assertTrue(logit_cross_entropy_certificate(logits, 1, report)["valid"])

    def test_logit_loss_certificate_rejects_a_tampered_loss_or_invalid_target(self):
        logits = [2.0, 1.0, -1.0]
        report = logit_cross_entropy_report(logits, 0)
        tampered = dict(report)
        tampered["loss"] = float(tampered["loss"]) + 1.0
        self.assertFalse(logit_cross_entropy_certificate(logits, 0, tampered)["valid"])
        with self.assertRaises(ValueError):
            categorical_cross_entropy_from_logits(logits, 3)


if __name__ == "__main__":
    unittest.main()
