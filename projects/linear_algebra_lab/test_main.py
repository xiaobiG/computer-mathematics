import unittest

from projects.linear_algebra_lab.main import (
    compress_grayscale, dominant_right_singular_vector, frobenius_error, image_cosine_similarity, matmul, norm, project,
    rank_k_approximation, rank_one_approximation, solve,
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

    def test_rank_k_exactly_reconstructs_small_rank_two_matrix(self):
        matrix = [[3.0, 0.0], [0.0, 2.0]]
        components, approximation = rank_k_approximation(matrix, rank=2, iterations=120)
        self.assertEqual(len(components), 2)
        self.assertLess(frobenius_error(matrix, approximation), 1e-9)

    def test_higher_rank_does_not_increase_compression_error(self):
        pixels = [[8.0, 0.0], [0.0, 3.0]]
        _, _, rank_one_error = compress_grayscale(pixels, rank=1, iterations=120)
        _, _, rank_two_error = compress_grayscale(pixels, rank=2, iterations=120)
        self.assertLessEqual(rank_two_error, rank_one_error + 1e-9)

    def test_rank_k_rejects_nonpositive_rank(self):
        with self.assertRaises(ValueError):
            rank_k_approximation([[1.0]], rank=0)

    def test_flattened_image_cosine_similarity(self):
        self.assertAlmostEqual(image_cosine_similarity([[1.0, 0.0]], [[2.0, 0.0]]), 1.0)
        self.assertEqual(image_cosine_similarity([[1.0, 0.0]], [[0.0, 1.0]]), 0.0)
        self.assertEqual(image_cosine_similarity([[0.0]], [[0.0]]), 0.0)
        with self.assertRaises(ValueError):
            image_cosine_similarity([[1.0]], [[1.0, 2.0]])


if __name__ == "__main__":
    unittest.main()
