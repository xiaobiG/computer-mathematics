import copy
import unittest

from projects.naive_bayes_spam.practical_effect_review import (
    INTERVAL_CONTRACT,
    practical_effect_review,
    two_sample_mean_interval,
)


class PracticalEffectReviewTests(unittest.TestCase):
    def test_upstream_interval_can_support_a_manual_above_threshold_review(self):
        interval = two_sample_mean_interval([11, 12, 13, 12, 11], [8, 9, 8, 9, 8])
        self.assertEqual(interval["contract"], INTERVAL_CONTRACT)
        self.assertGreater(interval["interval"][0], 2.0)
        review = practical_effect_review(interval, 2.0)
        self.assertEqual(review["interpretation"], "interval_entirely_at_or_above_declared_minimum_effect")
        self.assertEqual(review["automatic_action"], "none")

    def test_crossing_the_threshold_is_inconclusive_not_a_negative_result(self):
        interval = two_sample_mean_interval([10, 11, 9, 10, 10], [9, 10, 8, 9, 9])
        review = practical_effect_review(interval, 1.5)
        self.assertEqual(review["interpretation"], "interval_crosses_declared_minimum_effect")

    def test_downstream_review_rejects_a_tampered_or_invalid_upstream_artifact(self):
        interval = two_sample_mean_interval([11, 12, 13, 12, 11], [8, 9, 8, 9, 8])
        altered = copy.deepcopy(interval)
        altered["interval"] = (0.0, 0.0)
        with self.assertRaises(ValueError):
            practical_effect_review(altered, 2.0)
        with self.assertRaises(ValueError):
            two_sample_mean_interval([1], [2, 3])


if __name__ == "__main__":
    unittest.main()
