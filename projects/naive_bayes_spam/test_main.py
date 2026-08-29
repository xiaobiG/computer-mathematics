import unittest

from projects.naive_bayes_spam.main import NaiveBayesSpam, confusion_matrix


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

    def test_training_requires_both_classes(self):
        with self.assertRaises(ValueError):
            NaiveBayesSpam().fit([("only spam", True)])
