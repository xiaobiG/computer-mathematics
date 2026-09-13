import unittest
from dataclasses import replace

from projects.naive_bayes_spam.permutation_test import (
    exact_permutation_test_certificate, exact_two_sided_permutation_test,
    permutation_test_certificate, two_sided_permutation_test,
)


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
        self.assertEqual(first.seed, 8)
        self.assertTrue(permutation_test_certificate([0.0] * 6, [1.0] * 6, first))
        self.assertFalse(permutation_test_certificate(
            [0.0] * 6, [1.0] * 6, replace(first, extreme_permutations=0)
        ))
        self.assertFalse(permutation_test_certificate(
            [0.0] * 6, [1.0] * 6, replace(first, seed=9)
        ))

    def test_rejects_empty_nonfinite_or_nonpositive_round_inputs(self):
        with self.assertRaises(ValueError):
            two_sided_permutation_test([], [1.0])
        with self.assertRaises(ValueError):
            two_sided_permutation_test([1.0], [float("nan")])
        with self.assertRaises(ValueError):
            two_sided_permutation_test([1.0], [2.0], rounds=0)
        with self.assertRaises(ValueError):
            two_sided_permutation_test([1.0], [2.0], seed=True)

    def test_exact_enumeration_exposes_small_sample_resolution_and_rejects_tampering(self):
        report = exact_two_sided_permutation_test([0.0] * 3, [1.0] * 3)
        self.assertEqual(report.observed_difference, 1.0)
        self.assertEqual(report.total_assignments, 20)
        self.assertEqual(report.extreme_assignments, 2)
        self.assertEqual(report.p_value, 0.1)
        self.assertTrue(exact_permutation_test_certificate([0.0] * 3, [1.0] * 3, report))
        self.assertFalse(exact_permutation_test_certificate(
            [0.0] * 3, [1.0] * 3, replace(report, extreme_assignments=1),
        ))
        with self.assertRaises(ValueError):
            exact_two_sided_permutation_test([0.0] * 3, [1.0] * 3, max_assignments=19)
