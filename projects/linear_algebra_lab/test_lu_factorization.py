import unittest

from projects.linear_algebra_lab.lu_factorization import lu_factorize, permuted_rows, solve_lu, solve_many_lu
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
