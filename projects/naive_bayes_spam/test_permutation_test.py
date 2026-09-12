import unittest

from projects.naive_bayes_spam.permutation_test import two_sided_permutation_test


class PermutationTestTests(unittest.TestCase):
    def test_identical_groups_have_unit_two_sided_p_value(self):
        result = two_sided_permutation_test([0.0, 1.0, 0.0], [0.0, 1.0, 0.0], rounds=200, seed=4)
        self.assertEqual(result.observed_difference, 0.0)
        self.assertEqual(result.p_value, 1.0)

    def test_large_separation_is_reproducible_and_rare_under_label_permutation(self):
        first = two_sided_permutation_test([0.0] * 6, [1.0] * 6, rounds=2_000, seed=8)
        second = two_sided_permutation_test([0.0] * 6, [1.0] * 6, rounds=2_000, seed=8)
        self.assertEqual(first, second)
        self.assertEqual(first.observed_difference, 1.0)
        self.assertLess(first.p_value, 0.05)
        self.assertGreaterEqual(first.p_value, 1 / 2_001)

    def test_rejects_empty_nonfinite_or_nonpositive_round_inputs(self):
        with self.assertRaises(ValueError):
            two_sided_permutation_test([], [1.0])
        with self.assertRaises(ValueError):
            two_sided_permutation_test([1.0], [float("nan")])
        with self.assertRaises(ValueError):
            two_sided_permutation_test([1.0], [2.0], rounds=0)
