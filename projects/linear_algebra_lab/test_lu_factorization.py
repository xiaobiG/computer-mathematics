import unittest
from dataclasses import replace

from projects.linear_algebra_lab.lu_factorization import (
    lu_factorize, lu_reuse_work_certificate, lu_reuse_work_report, permuted_rows, solve_lu, solve_many_lu,
)
from projects.linear_algebra_lab.main import matmul


class LUFactorizationTests(unittest.TestCase):
    def test_partial_pivoting_reconstructs_permuted_matrix(self):
        matrix = [[0.0, 2.0], [1.0, 3.0]]
        factorization = lu_factorize(matrix)
        self.assertEqual(factorization.permutation, [1, 0])
        self.assertEqual(matmul(factorization.lower, factorization.upper), permuted_rows(matrix, factorization.permutation))

    def test_one_factorization_solves_multiple_right_sides(self):
        factorization = lu_factorize([[0.0, 2.0], [1.0, 3.0]])
        self.assertEqual(solve_lu(factorization, [2.0, 4.0]), [1.0, 1.0])
        self.assertEqual(solve_many_lu(factorization, [[2.0, 4.0], [4.0, 8.0]]), [[1.0, 1.0], [2.0, 2.0]])

    def test_singular_and_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            lu_factorize([[1.0, 1.0], [2.0, 2.0]])
        with self.assertRaises(ValueError):
            lu_factorize([[float("nan")]])
        with self.assertRaises(ValueError):
            solve_lu(lu_factorize([[1.0]]), [float("inf")])

    def test_reuse_report_separates_one_factorization_from_repeated_elimination(self):
        matrix = [[0.0, 2.0], [1.0, 3.0]]
        right_sides = [[2.0, 4.0], [4.0, 8.0]]
        report = lu_reuse_work_report(matrix, right_sides)
        self.assertEqual(report.factorization_elimination_updates, 2)
        self.assertEqual(report.triangular_dot_terms_per_right_side, 2)
        self.assertEqual(report.reuse_work_units, 6)
        self.assertEqual(report.refactor_every_time_work_units, 8)
        self.assertEqual(report.saved_work_units, 2)
        self.assertTrue(report.solutions_match)
        self.assertTrue(report.pa_equals_lu)
        self.assertEqual(report.automatic_action, "none")
        self.assertTrue(lu_reuse_work_certificate(matrix, right_sides, report))
        self.assertFalse(lu_reuse_work_certificate(matrix, right_sides, replace(report, saved_work_units=0)))
        with self.assertRaisesRegex(ValueError, "at least two"):
            lu_reuse_work_report(matrix, [right_sides[0]])
