import unittest

from projects.linear_algebra_lab.main import (
    dominant_right_singular_vector, frobenius_error, matmul, norm, project,
    rank_one_approximation, solve,
)


class LinearAlgebraLabTests(unittest.TestCase):
    def test_matrix_product_and_order(self):
        scale = [[2, 0], [0, 1]]
        rotate = [[0, -1], [1, 0]]
        self.assertEqual(matmul(rotate, scale), [[0, -1], [2, 0]])
        self.assertNotEqual(matmul(rotate, scale), matmul(scale, rotate))

    def test_matrix_shape_error(self):
        with self.assertRaises(ValueError):
            matmul([[1, 2]], [[1, 2]])

    def test_pivoting_solves_small_leading_value(self):
        answer = solve([[1e-16, 1], [1, 1]], [1, 2])
        self.assertAlmostEqual(answer[0], 1.0)
        self.assertAlmostEqual(answer[1], 1.0)

    def test_singular_system_is_explicit(self):
        with self.assertRaises(ValueError):
            solve([[1, 1], [2, 2]], [2, 4])

    def test_projection_has_orthogonal_residual(self):
        projected = project([3, 4], [1, 0])
        residual = [3 - projected[0], 4 - projected[1]]
        self.assertEqual(projected, [3.0, 0.0])
        self.assertEqual(sum(a * b for a, b in zip(residual, [1, 0])), 0.0)
        self.assertAlmostEqual(norm(residual), 4.0)

    def test_rank_one_matrix_is_reconstructed(self):
        matrix = [[3.0, 6.0], [4.0, 8.0]]
        sigma, left, right, approximation = rank_one_approximation(matrix)
        self.assertAlmostEqual(norm(left), 1.0, places=10)
        self.assertAlmostEqual(norm(right), 1.0, places=10)
        self.assertGreater(sigma, 0.0)
        self.assertLess(frobenius_error(matrix, approximation), 1e-9)

    def test_power_iteration_rejects_zero_matrix(self):
        with self.assertRaises(ValueError):
            dominant_right_singular_vector([[0.0, 0.0], [0.0, 0.0]])


if __name__ == "__main__":
    unittest.main()
