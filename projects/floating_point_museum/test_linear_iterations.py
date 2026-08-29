import unittest

from projects.floating_point_museum.linear_iterations import (
    is_strictly_diagonally_dominant,
    iteration_trace_certificate,
    residual,
    solve_iteratively,
)


SYSTEM = [[4.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 3.0]]
RIGHT_SIDE = [15.0, 10.0, 10.0]


class LinearIterationTests(unittest.TestCase):
    def test_both_methods_solve_a_strictly_diagonally_dominant_system(self):
        self.assertTrue(is_strictly_diagonally_dominant(SYSTEM))
        for method in ("jacobi", "gauss-seidel"):
            estimate, trace = solve_iteratively(SYSTEM, RIGHT_SIDE, method=method)
            self.assertEqual(len(estimate), 3)
            self.assertTrue(all(abs(value - 5.0) < 1e-8 for value in estimate))
            self.assertLess(trace[-1]["residual_norm"], 1e-10)
            self.assertTrue(iteration_trace_certificate(SYSTEM, RIGHT_SIDE, method, estimate, trace)["valid"])

    def test_gauss_seidel_uses_no_more_steps_on_this_system(self):
        _, jacobi_trace = solve_iteratively(SYSTEM, RIGHT_SIDE, method="jacobi")
        _, seidel_trace = solve_iteratively(SYSTEM, RIGHT_SIDE, method="gauss-seidel")
        self.assertLessEqual(len(seidel_trace), len(jacobi_trace))

    def test_residual_uses_b_minus_a_times_x(self):
        self.assertEqual(residual([[2.0]], [3.0], [5.0]), [-1.0])

    def test_certificate_rejects_a_tampered_iteration_metric(self):
        estimate, trace = solve_iteratively(SYSTEM, RIGHT_SIDE, method="jacobi")
        tampered = [dict(event) for event in trace]
        tampered[0]["residual_norm"] = 0.0
        certificate = iteration_trace_certificate(SYSTEM, RIGHT_SIDE, "jacobi", estimate, tampered)
        self.assertFalse(certificate["metrics_match"])
        self.assertFalse(certificate["valid"])

    def test_reports_divergence_and_invalid_iteration_contracts(self):
        with self.assertRaises(RuntimeError):
            solve_iteratively([[1.0, 2.0], [2.0, 1.0]], [1.0, 1.0], max_steps=12)
        with self.assertRaises(ValueError):
            solve_iteratively([[0.0]], [1.0])
        with self.assertRaises(ValueError):
            solve_iteratively([[1.0]], [1.0], method="sor")  # type: ignore[arg-type]
