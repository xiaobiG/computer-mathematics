import unittest

from projects.linear_algebra_lab.main import (
    classify_linear_system, compress_grayscale, dominant_right_singular_vector, frobenius_error, image_cosine_similarity,
    matmul, norm, project, least_squares_qr, rank_k_approximation, rank_one_approximation, solve, solve_with_pivot_trace,
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

    def test_pivot_trace_records_a_row_swap_and_triangular_invariant(self):
        solution, trace = solve_with_pivot_trace([[1e-16, 1.0], [1.0, 1.0]], [1.0, 2.0])
        self.assertTrue(trace[0]["swapped"])
        self.assertEqual(trace[0]["pivot_row"], 1)
        self.assertAlmostEqual(trace[-1]["upper"][1][0], 0.0, places=12)
        self.assertTrue(all(abs(sum(a * x for a, x in zip(row, solution)) - target) < 1e-10
                            for row, target in zip([[1e-16, 1.0], [1.0, 1.0]], [1.0, 2.0])))

    def test_classifies_consistent_and_inconsistent_singular_systems(self):
        self.assertEqual(classify_linear_system([[1.0, 1.0], [2.0, 2.0]], [2.0, 4.0]), "infinitely_many")
        self.assertEqual(classify_linear_system([[1.0, 1.0], [2.0, 2.0]], [2.0, 5.0]), "none")
        self.assertEqual(classify_linear_system([[2.0, 1.0], [1.0, -1.0]], [5.0, 1.0]), "unique")

    def test_elimination_rejects_nonfinite_inputs(self):
        with self.assertRaises(ValueError):
            solve([[float("nan")]], [1.0])

    def test_projection_has_orthogonal_residual(self):
        projected = project([3, 4], [1, 0])
        residual = [3 - projected[0], 4 - projected[1]]
        self.assertEqual(projected, [3.0, 0.0])
        self.assertEqual(sum(a * b for a, b in zip(residual, [1, 0])), 0.0)
        self.assertAlmostEqual(norm(residual), 4.0)

    def test_qr_least_squares_has_column_orthogonal_residual(self):
        matrix = [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]
        solution, residual = least_squares_qr(matrix, [1.0, 2.0, 2.0])
        self.assertAlmostEqual(solution[0], 0.5)
        self.assertAlmostEqual(solution[1], 7 / 6)
        self.assertAlmostEqual(sum(matrix[row][0] * residual[row] for row in range(3)), 0.0, places=12)
        self.assertAlmostEqual(sum(matrix[row][1] * residual[row] for row in range(3)), 0.0, places=12)

    def test_qr_least_squares_rejects_rank_deficiency_and_wide_matrix(self):
        with self.assertRaises(ValueError):
            least_squares_qr([[1.0, 1.0], [2.0, 2.0]], [1.0, 2.0])
        with self.assertRaises(ValueError):
            least_squares_qr([[1.0, 2.0]], [1.0])

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
