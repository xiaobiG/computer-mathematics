import unittest

from projects.naive_bayes_spam.beta_bernoulli import map_estimate, posterior_parameters, posterior_predictive_success


class BetaBernoulliTests(unittest.TestCase):
    def test_posterior_adds_successes_and_failures(self):
        self.assertEqual(posterior_parameters([1, 1, 0], 2, 3), (4, 4))

    def test_uniform_prior_smooths_extreme_small_sample(self):
        self.assertEqual(posterior_predictive_success([1], 1, 1), 2 / 3)
        self.assertEqual(posterior_predictive_success([], 1, 1), 1 / 2)

    def test_map_estimate_uses_updated_posterior(self):
        self.assertEqual(map_estimate([1, 1, 0], 2, 2), 3 / 5)

    def test_rejects_invalid_priors_observations_and_boundary_map(self):
        with self.assertRaises(ValueError):
            posterior_parameters([1], 0, 1)
        with self.assertRaises(ValueError):
            posterior_parameters([2])
        with self.assertRaises(ValueError):
            map_estimate([], 1, 1)


if __name__ == "__main__":
    unittest.main()
