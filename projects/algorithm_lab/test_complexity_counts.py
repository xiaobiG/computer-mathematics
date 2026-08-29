import unittest

from projects.algorithm_lab.complexity_counts import operation_counts, two_sum_sorted_trace


class ComplexityCountTests(unittest.TestCase):
    def test_exact_counts_expose_different_growth_rates(self):
        small = operation_counts(4)
        large = operation_counts(8)
        self.assertEqual(small, {"linear_scan": 4, "all_unordered_pairs": 6, "all_subsets": 16})
        self.assertEqual(large["linear_scan"], 2 * small["linear_scan"])
        self.assertGreater(large["all_unordered_pairs"], 4 * small["all_unordered_pairs"])
        self.assertEqual(large["all_subsets"], 16 * small["all_subsets"])

    def test_two_pointer_search_is_correct_and_uses_at_most_linear_comparisons(self):
        values = [1, 3, 4, 7, 11, 18]
        pair, comparisons = two_sum_sorted_trace(values, 15)
        self.assertEqual(pair, (2, 4))
        self.assertLessEqual(comparisons, len(values) - 1)
        missing, missing_comparisons = two_sum_sorted_trace(values, 100)
        self.assertIsNone(missing)
        self.assertLessEqual(missing_comparisons, len(values) - 1)

    def test_rejects_invalid_sizes_and_unsorted_input(self):
        with self.assertRaises(ValueError):
            operation_counts(-1)
        with self.assertRaises(ValueError):
            two_sum_sorted_trace([2, 1], 3)


if __name__ == "__main__":
    unittest.main()
