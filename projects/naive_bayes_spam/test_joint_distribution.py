import unittest

from projects.naive_bayes_spam.joint_distribution import (
    conditional_second_given_first,
    independence_residual,
    marginal_first,
    marginal_second,
)


class JointDistributionTests(unittest.TestCase):
    def setUp(self):
        self.weather_and_umbrella = {
            ("rain", "umbrella"): 0.18,
            ("rain", "none"): 0.02,
            ("sun", "umbrella"): 0.12,
            ("sun", "none"): 0.68,
        }

    def test_marginals_and_conditionals_preserve_probability_mass(self):
        first = marginal_first(self.weather_and_umbrella)
        second = marginal_second(self.weather_and_umbrella)
        self.assertAlmostEqual(first["rain"], 0.2)
        self.assertAlmostEqual(first["sun"], 0.8)
        self.assertAlmostEqual(second["umbrella"], 0.3)
        self.assertAlmostEqual(second["none"], 0.7)
        conditional = conditional_second_given_first(self.weather_and_umbrella, "rain")
        self.assertAlmostEqual(conditional["umbrella"], 0.9)
        self.assertAlmostEqual(conditional["none"], 0.1)
        self.assertAlmostEqual(sum(conditional.values()), 1.0)

    def test_independence_residual_distinguishes_product_and_dependent_tables(self):
        independent = {
            ("a", 0): 0.12, ("a", 1): 0.18,
            ("b", 0): 0.28, ("b", 1): 0.42,
        }
        self.assertAlmostEqual(independence_residual(independent), 0.0)
        self.assertGreater(independence_residual(self.weather_and_umbrella), 0.0)

    def test_rejects_invalid_normalization_and_zero_probability_conditioning(self):
        with self.assertRaises(ValueError):
            marginal_first({("a", "b"): 0.9})
        with self.assertRaises(ValueError):
            conditional_second_given_first({("a", "b"): 1.0}, "missing")
        with self.assertRaises(ValueError):
            marginal_second({("a", "b"): float("nan")})


if __name__ == "__main__":
    unittest.main()
