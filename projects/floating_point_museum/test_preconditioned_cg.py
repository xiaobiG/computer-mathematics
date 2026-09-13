import unittest

from projects.floating_point_museum.preconditioned_cg import (
    CgEvent,
    pcg_trace_certificate,
    preconditioned_conjugate_gradient,
    spd_cholesky_certificate,
    spd_cholesky_report,
)


MATRIX = [[4.0, 1.0], [1.0, 3.0]]
RIGHT_SIDE = [1.0, 2.0]


class PreconditionedCgTests(unittest.TestCase):
    def test_solves_a_small_spd_system_and_replays_each_iteration(self):
        solution, trace = preconditioned_conjugate_gradient(MATRIX, RIGHT_SIDE)
        self.assertAlmostEqual(solution[0], 1 / 11, places=10)
        self.assertAlmostEqual(solution[1], 7 / 11, places=10)
        self.assertLessEqual(len(trace), 2)
        self.assertTrue(pcg_trace_certificate(MATRIX, RIGHT_SIDE, solution, trace)["valid"])

    def test_certificate_rejects_a_tampered_search_step(self):
        solution, trace = preconditioned_conjugate_gradient(MATRIX, RIGHT_SIDE)
        tampered = list(trace)
        event = tampered[0]
        tampered[0] = CgEvent(event.iteration, event.alpha + 0.1, event.beta, event.solution, event.residual_norm, event.preconditioned_residual_dot)
        certificate = pcg_trace_certificate(MATRIX, RIGHT_SIDE, solution, tampered)
        self.assertFalse(certificate["trace_matches_recomputation"])
        self.assertFalse(certificate["valid"])

    def test_jacobi_can_remove_diagonal_scale_spread_on_the_same_system(self):
        matrix = [[1.0, 0.0, 0.0], [0.0, 100.0, 0.0], [0.0, 0.0, 10_000.0]]
        right_side = [1.0, 1.0, 1.0]
        identity_solution, identity_trace = preconditioned_conjugate_gradient(
            matrix, right_side, preconditioner="identity",
        )
        jacobi_solution, jacobi_trace = preconditioned_conjugate_gradient(
            matrix, right_side, preconditioner="jacobi",
        )
        self.assertEqual(len(identity_trace), 3)
        self.assertEqual(len(jacobi_trace), 1)
        for identity_value, jacobi_value in zip(identity_solution, jacobi_solution):
            self.assertAlmostEqual(identity_value, jacobi_value, places=10)
        self.assertTrue(pcg_trace_certificate(
            matrix, right_side, jacobi_solution, jacobi_trace, preconditioner="jacobi",
        )["valid"])
        self.assertTrue(pcg_trace_certificate(
            matrix, right_side, identity_solution, identity_trace, preconditioner="identity",
        )["valid"])

    def test_rejects_non_symmetric_system_and_exhausted_budget(self):
        with self.assertRaises(ValueError):
            preconditioned_conjugate_gradient([[2.0, 1.0], [0.0, 2.0]], [1.0, 1.0])
        with self.assertRaises(RuntimeError):
            preconditioned_conjugate_gradient(MATRIX, RIGHT_SIDE, tolerance=1e-15, max_steps=1)
        with self.assertRaises(ValueError):
            preconditioned_conjugate_gradient(MATRIX, RIGHT_SIDE, preconditioner="unknown")

    def test_positive_diagonal_is_not_a_positive_definiteness_check(self):
        indefinite = [[1.0, 2.0], [2.0, 1.0]]
        report = spd_cholesky_report(indefinite)
        self.assertFalse(report["positive_definite"])
        self.assertEqual(report["cholesky_pivots"], [1.0, -3.0])
        self.assertEqual(report["failing_pivot_index"], 1)
        self.assertTrue(spd_cholesky_certificate(indefinite, report))
        altered = dict(report)
        altered["positive_definite"] = True
        self.assertFalse(spd_cholesky_certificate(indefinite, altered))
        with self.assertRaisesRegex(ValueError, "positive-definite"):
            preconditioned_conjugate_gradient(indefinite, [1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
