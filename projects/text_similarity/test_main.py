import unittest

from projects.text_similarity.main import cosine_similarity, rank_documents, vectorize


class TextSimilarityTests(unittest.TestCase):
    def test_identical_vectors_have_score_one(self):
        vector = vectorize("Matrix matrix")
        self.assertAlmostEqual(cosine_similarity(vector, vector), 1.0)

    def test_disjoint_vectors_have_score_zero(self):
        self.assertEqual(cosine_similarity(vectorize("matrix"), vectorize("graph")), 0.0)

    def test_empty_query_is_safe(self):
        self.assertEqual(cosine_similarity(vectorize(""), vectorize("matrix")), 0.0)

    def test_ranking_prefers_overlapping_document(self):
        ranked = rank_documents("matrix vector", ["graph path", "matrix vector matrix"])
        self.assertEqual(ranked[0][0], 1)


if __name__ == "__main__":
    unittest.main()
