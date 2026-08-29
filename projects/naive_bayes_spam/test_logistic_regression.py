import unittest

from projects.naive_bayes_spam.logistic_regression import (
    LogisticRegression,
    binary_cross_entropy,
    sigmoid,
)


SAMPLES = [
    ([-2.0, -1.0], False),
    ([-1.0, -2.0], False),
    ([1.0, 2.0], True),
    ([2.0, 1.0], True),
]


class LogisticRegressionTests(unittest.TestCase):
    def test_sigmoid_stays_finite_for_extreme_scores(self):
        # The mathematical sigmoid lies in (0, 1), but a double can underflow
        # to an endpoint.  The stable branch still avoids OverflowError.
        self.assertGreaterEqual(sigmoid(-1000), 0.0)
        self.assertLess(sigmoid(-1000), 0.5)
        self.assertGreater(sigmoid(1000), 0.5)
        self.assertLessEqual(sigmoid(1000), 1.0)

    def test_cross_entropy_rewards_the_correct_forecast(self):
        self.assertLess(binary_cross_entropy(0.9, True), binary_cross_entropy(0.1, True))
        with self.assertRaises(ValueError):
            binary_cross_entropy(1.0, True)

    def test_batch_gradient_descent_reduces_loss_and_classifies_training_examples(self):
        model = LogisticRegression().fit(SAMPLES, learning_rate=0.5, steps=1)
        first_loss = model.loss(SAMPLES)
        model.fit(SAMPLES, learning_rate=0.5, steps=500)
        self.assertLess(model.loss(SAMPLES), first_loss)
        self.assertEqual([model.predict(features) for features, _ in SAMPLES], [target for _, target in SAMPLES])

    def test_fit_rejects_inconsistent_or_empty_feature_vectors(self):
        with self.assertRaises(ValueError):
            LogisticRegression().fit([])
        with self.assertRaises(ValueError):
            LogisticRegression().fit([([], True)])
        with self.assertRaises(ValueError):
            LogisticRegression().fit([([1.0], True), ([1.0, 2.0], False)])
