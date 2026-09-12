import unittest

from projects.linear_algebra_lab.similarity_metrics import compare_similarity_metrics


class SimilarityMetricComparisonTests(unittest.TestCase):
    def test_direction_and_absolute_distance_can_rank_the_same_candidates_differently(self):
        report = compare_similarity_metrics(
            [1.0, 0.0],
            [
                {"label": "near", "vector": [1.0, .1]},
                {"label": "scaled", "vector": [100.0, 0.0]},
            ],
        )
        self.assertEqual(report["cosine_ranking"], ["scaled", "near"])
        self.assertEqual(report["euclidean_ranking"], ["near", "scaled"])
        self.assertFalse(report["same_top_choice"])

    def test_rejects_undefined_or_ambiguous_metric_inputs(self):
        with self.assertRaises(ValueError):
            compare_similarity_metrics([0.0, 0.0], [{"label": "a", "vector": [1.0, 0.0]}, {"label": "b", "vector": [0.0, 1.0]}])
        with self.assertRaises(ValueError):
            compare_similarity_metrics([1.0], [{"label": "a", "vector": [1.0]}, {"label": "a", "vector": [2.0]}])
        with self.assertRaises(ValueError):
            compare_similarity_metrics([1.0, 0.0], [{"label": "a", "vector": [1.0]}, {"label": "b", "vector": [0.0, 1.0]}])


if __name__ == "__main__":
    unittest.main()
