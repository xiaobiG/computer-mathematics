import unittest

from projects.algorithm_lab.recurrence_trace import (
    binary_search_worst_case_steps,
    merge_sort_levels,
    merge_sort_tree_certificate,
    merge_sort_tree_report,
    merge_sort_with_comparisons,
)


class RecurrenceTraceTests(unittest.TestCase):
    def test_binary_search_halves_until_one_candidate_remains(self):
        self.assertEqual(binary_search_worst_case_steps(1), 0)
        self.assertEqual(binary_search_worst_case_steps(16), 4)
        self.assertEqual(binary_search_worst_case_steps(17), 5)
        with self.assertRaises(ValueError):
            binary_search_worst_case_steps(0)

    def test_merge_tree_has_linear_work_at_every_internal_level(self):
        levels = merge_sort_levels(8)
        self.assertEqual([level.subproblems for level in levels], [1, 2, 4])
        self.assertEqual([level.items_per_subproblem for level in levels], [8, 4, 2])
        self.assertTrue(all(level.total_merge_items == 8 for level in levels))
        self.assertEqual(sum(level.total_merge_items for level in levels), 24)
        with self.assertRaises(ValueError):
            merge_sort_levels(6)

    def test_merge_tree_report_replays_all_level_and_total_work_claims(self):
        report = merge_sort_tree_report(8)
        self.assertEqual(report["internal_depth"], 3)
        self.assertEqual(report["total_merge_items"], 24)
        self.assertEqual(report["expected_total_merge_items"], 24)
        self.assertTrue(all(report["certificate"].values()))
        self.assertTrue(merge_sort_tree_certificate(8, report))
        self.assertTrue(merge_sort_tree_certificate(1, merge_sort_tree_report(1)))

        changed = dict(report)
        changed["total_merge_items"] = 23
        self.assertFalse(merge_sort_tree_certificate(8, changed))

        changed = dict(report)
        changed["levels"] = [dict(level) for level in report["levels"]]
        changed["levels"][1]["items_per_subproblem"] = 3
        self.assertFalse(merge_sort_tree_certificate(8, changed))

    def test_merge_sort_is_correct_and_comparisons_obey_n_log_n_bound(self):
        values = [5, 1, 4, 2, 3, 0, 7, 6]
        ordered, comparisons = merge_sort_with_comparisons(values)
        self.assertEqual(ordered, sorted(values))
        self.assertLessEqual(comparisons, len(values) * 3)
        self.assertEqual(values, [5, 1, 4, 2, 3, 0, 7, 6])


if __name__ == "__main__":
    unittest.main()
