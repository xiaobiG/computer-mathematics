import unittest
from math import inf

from projects.naive_bayes_spam.bernoulli_estimation import (
    bernoulli_log_likelihood,
    bernoulli_mle_certificate,
    bernoulli_map,
    bernoulli_mle,
)


class BernoulliEstimationTests(unittest.TestCase):
    def test_mle_is_sample_mean_and_outscores_nearby_candidates(self):
        observations = [1] * 8 + [0] * 2
        self.assertEqual(bernoulli_mle(observations), 0.8)
        self.assertGreater(bernoulli_log_likelihood(observations, 0.8), bernoulli_log_likelihood(observations, 0.6))
        certificate = bernoulli_mle_certificate(observations, 0.8)
        self.assertTrue(certificate["is_interior_stationary_case"])
        self.assertTrue(certificate["valid"])

    def test_mle_certificate_distinguishes_boundary_and_tampered_candidates(self):
        all_heads = bernoulli_mle_certificate([1, 1, 1], 1.0)
        self.assertTrue(all_heads["is_correct_boundary_case"])
        self.assertTrue(all_heads["valid"])
        self.assertFalse(bernoulli_mle_certificate([1, 1, 0], 0.8)["matches_sample_mean"])
        self.assertFalse(bernoulli_mle_certificate([1, 1, 0], 0.8)["valid"])

    def test_endpoint_likelihoods_and_map_make_boundary_assumptions_explicit(self):
        self.assertEqual(bernoulli_log_likelihood([0, 0], 0.0), 0.0)
        self.assertEqual(bernoulli_log_likelihood([0, 1], 0.0), -inf)
        self.assertEqual(bernoulli_map([1, 1, 0], 2.0, 2.0), 3 / 5)
        with self.assertRaises(ValueError):
            bernoulli_map([], 1.0, 1.0)

    def test_rejects_invalid_observations_and_probability(self):
        with self.assertRaises(ValueError):
            bernoulli_mle([])
        with self.assertRaises(ValueError):
            bernoulli_log_likelihood([2], 0.5)
        with self.assertRaises(ValueError):
            bernoulli_log_likelihood([1], 1.1)
