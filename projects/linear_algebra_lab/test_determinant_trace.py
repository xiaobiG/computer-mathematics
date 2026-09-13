import unittest
from dataclasses import replace
from fractions import Fraction

from projects.linear_algebra_lab.determinant_trace import (
    classify_square_matrix,
    determinant_trace,
    determinant_trace_certificate,
    square_matrix_classification_certificate,
)


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

    def test_classification_keeps_rank_nullity_and_universal_solve_claim_together(self):
        full_rank = classify_square_matrix([[0, 2], [3, 4]])
        self.assertEqual(full_rank.determinant, Fraction(-6))
        self.assertEqual((full_rank.rank, full_rank.nullity), (2, 0))
        self.assertTrue(full_rank.invertible)
        self.assertTrue(full_rank.unique_solution_for_every_rhs)
        self.assertTrue(square_matrix_classification_certificate([[0, 2], [3, 4]], full_rank))

        singular = classify_square_matrix([[1, 2], [2, 4]])
        self.assertEqual((singular.determinant, singular.rank, singular.nullity), (0, 1, 1))
        self.assertFalse(singular.invertible)
        self.assertFalse(singular.unique_solution_for_every_rhs)
        self.assertTrue(square_matrix_classification_certificate([[1, 2], [2, 4]], singular))
        self.assertFalse(square_matrix_classification_certificate([[1, 2], [2, 4]], full_rank))

    def test_rank_does_not_stop_at_the_first_zero_column(self):
        report = classify_square_matrix([[0, 1], [0, 0]])
        self.assertEqual(report.determinant, 0)
        self.assertEqual((report.rank, report.nullity), (1, 1))
        self.assertFalse(report.invertible)
        self.assertTrue(square_matrix_classification_certificate([[0, 1], [0, 0]], report))


if __name__ == "__main__":
    unittest.main()
