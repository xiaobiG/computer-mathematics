import unittest

from projects.naive_bayes_spam.main import (
    NaiveBayesSpam,
    classification_metrics,
    confusion_matrix,
    reliability_bins,
)


TRAINING = [
    ("win cash prize now", True),
    ("claim free prize", True),
    ("meeting notes attached", False),
    ("project meeting tomorrow", False),
]


class NaiveBayesSpamTests(unittest.TestCase):
    def setUp(self):
        self.model = NaiveBayesSpam().fit(TRAINING)

    def test_predicts_obvious_spam(self):
        self.assertTrue(self.model.predict("free cash prize"))

    def test_predicts_obvious_ham(self):
        self.assertFalse(self.model.predict("project meeting notes"))

    def test_smoothing_handles_unseen_word(self):
        scores = self.model.log_scores("unseen token")
        self.assertTrue(all(score < 0 for score in scores.values()))

    def test_confusion_matrix_has_all_cells(self):
        result = confusion_matrix(self.model, [("cash prize", True), ("meeting", False)])
        self.assertEqual(sum(result.values()), 2)

    def test_probability_is_normalized_and_matches_prediction_threshold(self):
        probability = self.model.predict_proba("free cash prize")
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)
        self.assertEqual(self.model.predict("free cash prize"), probability >= 0.5)

    def test_metrics_include_probability_quality(self):
        metrics = classification_metrics(self.model, [("cash prize", True), ("meeting", False)])
        self.assertEqual(set(metrics), {"precision", "recall", "f1", "brier"})
        self.assertTrue(all(0.0 <= value <= 1.0 for value in metrics.values()))

    def test_reliability_bins_preserve_all_observations(self):
        report = reliability_bins(self.model, [("cash prize", True), ("meeting", False)], bins=4)
        self.assertEqual(sum(row["count"] for row in report), 2)
        self.assertTrue(all(row["lower"] <= row["mean_prediction"] <= row["upper"] for row in report))

    def test_reliability_bins_reject_nonpositive_bin_count(self):
        with self.assertRaises(ValueError):
            reliability_bins(self.model, [("cash prize", True)], bins=0)

    def test_training_requires_both_classes(self):
        with self.assertRaises(ValueError):
            NaiveBayesSpam().fit([("only spam", True)])
