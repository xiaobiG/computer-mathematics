import unittest
from math import sqrt

from projects.linear_algebra_lab.main import (
    classify_linear_system, compress_grayscale, dominant_right_singular_vector, frobenius_error, image_cosine_similarity,
    compressed_image_search, least_squares_comparison_report, least_squares_normal_equations, low_rank_parameter_report,
    matmul, matrix_composition_certificate, norm, project, least_squares_qr, rank_k_approximation, rank_one_approximation,
    pivot_trace_certificate, solve, solve_with_pivot_trace, truncated_svd_frobenius_error,
    truncated_svd_report, truncated_svd_report_certificate,
)


class LinearAlgebraLabTests(unittest.TestCase):
    def test_matrix_product_and_order(self):
        scale = [[2, 0], [0, 1]]
        rotate = [[0, -1], [1, 0]]
        self.assertEqual(matmul(rotate, scale), [[0, -1], [2, 0]])
        self.assertNotEqual(matmul(rotate, scale), matmul(scale, rotate))
        self.assertTrue(matrix_composition_certificate(rotate, scale, [1, 1], [[0, -1], [2, 0]]))

    def test_matrix_composition_certificate_rejects_wrong_order_or_vector_shape(self):
        scale = [[2, 0], [0, 1]]
        rotate = [[0, -1], [1, 0]]
        self.assertFalse(matrix_composition_certificate(rotate, scale, [1, 1], matmul(scale, rotate)))
        self.assertFalse(matrix_composition_certificate(rotate, scale, [1], matmul(rotate, scale)))

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
        matrix, target = [[1e-16, 1.0], [1.0, 1.0]], [1.0, 2.0]
        solution, trace = solve_with_pivot_trace(matrix, target)
        self.assertTrue(trace[0]["swapped"])
        self.assertEqual(trace[0]["pivot_row"], 1)
        self.assertAlmostEqual(trace[-1]["upper"][1][0], 0.0, places=12)
        self.assertTrue(all(abs(sum(a * x for a, x in zip(row, solution)) - value) < 1e-10
                            for row, value in zip(matrix, target)))
        self.assertTrue(pivot_trace_certificate(matrix, target, solution, trace))
        tampered = [dict(event) for event in trace]
        tampered[0]["multipliers"] = [0.0]
        self.assertFalse(pivot_trace_certificate(matrix, target, solution, tampered))

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

    def test_normal_equations_match_qr_on_a_well_conditioned_fit(self):
        matrix = [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]
        normal_solution, normal_residual = least_squares_normal_equations(matrix, [1.0, 2.0, 2.0])
        qr_solution, _ = least_squares_qr(matrix, [1.0, 2.0, 2.0])
        self.assertAlmostEqual(normal_solution[0], qr_solution[0], places=12)
        self.assertAlmostEqual(normal_solution[1], qr_solution[1], places=12)
        self.assertAlmostEqual(sum(matrix[row][0] * normal_residual[row] for row in range(3)), 0.0, places=12)
        self.assertAlmostEqual(sum(matrix[row][1] * normal_residual[row] for row in range(3)), 0.0, places=12)

    def test_least_squares_report_certifies_both_paths(self):
        matrix = [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]
        report = least_squares_comparison_report(matrix, [1.0, 2.0, 2.0])
        self.assertLess(report["solution_distance"], 1e-12)
        self.assertLess(report["normal_residual_norm"], 1.0)
        self.assertLess(report["qr_residual_norm"], 1.0)
        self.assertTrue(all(abs(value) < 1e-12 for value in report["normal_normal_equation_residual"]))
        self.assertTrue(all(abs(value) < 1e-12 for value in report["qr_normal_equation_residual"]))

    def test_qr_least_squares_rejects_rank_deficiency_and_wide_matrix(self):
        with self.assertRaises(ValueError):
            least_squares_qr([[1.0, 1.0], [2.0, 2.0]], [1.0, 2.0])
        with self.assertRaises(ValueError):
            least_squares_qr([[1.0, 2.0]], [1.0])

    def test_normal_equations_reject_rank_deficiency_and_nonfinite_input(self):
        with self.assertRaises(ValueError):
            least_squares_normal_equations([[1.0, 1.0], [2.0, 2.0]], [1.0, 2.0])
        with self.assertRaises(ValueError):
            least_squares_normal_equations([[float("nan")]], [1.0])

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

    def test_exact_truncated_svd_error_is_the_discarded_spectral_energy(self):
        self.assertAlmostEqual(truncated_svd_frobenius_error([5.0, 2.0, 1.0], rank=1), sqrt(5.0))
        self.assertEqual(truncated_svd_frobenius_error([5.0, 2.0, 1.0], rank=3), 0.0)

    def test_svd_certificate_rejects_invalid_spectra_and_rank(self):
        with self.assertRaises(ValueError):
            truncated_svd_frobenius_error([2.0, 5.0], rank=1)
        with self.assertRaises(ValueError):
            truncated_svd_frobenius_error([1.0, float("nan")], rank=1)
        with self.assertRaises(ValueError):
            truncated_svd_frobenius_error([1.0], rank=2)

    def test_low_rank_parameter_report_makes_the_storage_tradeoff_explicit(self):
        report = low_rank_parameter_report(8, 8, rank=2)
        self.assertEqual(report["dense_parameters"], 64)
        self.assertEqual(report["low_rank_parameters"], 34)
        self.assertEqual(report["saved_parameters"], 30)
        self.assertTrue(report["has_parameter_savings"])
        self.assertFalse(low_rank_parameter_report(2, 2, rank=2)["has_parameter_savings"])

    def test_truncated_svd_report_connects_spectral_error_and_storage_with_a_certificate(self):
        report = truncated_svd_report([5.0, 2.0, 1.0], rank=1, rows=8, columns=8)
        self.assertEqual(report["retained_spectral_energy"], 25.0)
        self.assertEqual(report["discarded_spectral_energy"], 5.0)
        self.assertAlmostEqual(report["frobenius_error"], sqrt(5.0))
        self.assertAlmostEqual(report["retained_energy_ratio"], 25.0 / 30.0)
        self.assertTrue(truncated_svd_report_certificate([5.0, 2.0, 1.0], 1, 8, 8, report)["valid"])
        tampered = dict(report)
        tampered["discarded_spectral_energy"] = 4.0
        certificate = truncated_svd_report_certificate([5.0, 2.0, 1.0], 1, 8, 8, tampered)
        self.assertFalse(certificate["fields_match_recomputed_report"])
        self.assertFalse(certificate["valid"])

    def test_compressed_image_search_reports_errors_and_ranks_the_exact_match_first(self):
        query = [[8.0, 0.0], [0.0, 3.0]]
        report = compressed_image_search(query, [query, [[0.0, 3.0], [8.0, 0.0]]], rank=2, iterations=120)
        self.assertEqual(report["query_component_count"], 2)
        self.assertEqual(report["image_component_counts"], [2, 2])
        self.assertLess(report["query_error"], 1e-9)
        self.assertTrue(all(error < 1e-9 for error in report["image_errors"]))
        self.assertEqual(report["ranking"][0][0], 0)
        self.assertAlmostEqual(report["ranking"][0][1], 1.0)
        self.assertEqual(report["original_ranking"][0][0], 0)
        self.assertEqual(report["compressed_ranking"][0][0], 0)
        self.assertTrue(report["certificate"]["original_ranking_is_a_permutation"])
        self.assertTrue(report["certificate"]["compressed_ranking_is_a_permutation"])
        self.assertTrue(report["certificate"]["top_match_is_preserved"])
        self.assertTrue(report["certificate"]["full_ranking_is_preserved"])

    def test_compressed_image_search_rejects_empty_gallery(self):
        with self.assertRaises(ValueError):
            compressed_image_search([[1.0]], [], rank=1)

    def test_flattened_image_cosine_similarity(self):
        self.assertAlmostEqual(image_cosine_similarity([[1.0, 0.0]], [[2.0, 0.0]]), 1.0)
        self.assertEqual(image_cosine_similarity([[1.0, 0.0]], [[0.0, 1.0]]), 0.0)
        self.assertEqual(image_cosine_similarity([[0.0]], [[0.0]]), 0.0)
        with self.assertRaises(ValueError):
            image_cosine_similarity([[1.0]], [[1.0, 2.0]])


if __name__ == "__main__":
    unittest.main()
