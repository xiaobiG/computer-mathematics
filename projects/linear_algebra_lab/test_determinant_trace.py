import unittest
from dataclasses import replace
from fractions import Fraction

from projects.linear_algebra_lab.determinant_trace import determinant_trace, determinant_trace_certificate


class DeterminantTraceTests(unittest.TestCase):
    def test_row_swap_changes_sign_and_trace_replays(self):
        determinant, events = determinant_trace([[0, 2], [3, 4]])
        self.assertEqual(determinant, Fraction(-6))
        self.assertTrue(events[0].swapped)
        self.assertTrue(determinant_trace_certificate([[0, 2], [3, 4]], determinant, events))
        altered = list(events)
        altered[0] = replace(altered[0], swapped=False)
        self.assertFalse(determinant_trace_certificate([[0, 2], [3, 4]], determinant, tuple(altered)))

    def test_zero_pivot_column_proves_singularity(self):
        determinant, events = determinant_trace([[1, 2], [2, 4]])
        self.assertEqual(determinant, 0)
        self.assertIsNone(events[-1].pivot_row)

    def test_rejects_non_square_and_boolean_entries(self):
        with self.assertRaises(ValueError): determinant_trace([[1, 2, 3], [4, 5, 6]])
        with self.assertRaises(ValueError): determinant_trace([[True]])


if __name__ == "__main__":
    unittest.main()
