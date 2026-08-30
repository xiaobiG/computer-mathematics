import unittest

from projects.floating_point_museum.preconditioned_cg import CgEvent, pcg_trace_certificate, preconditioned_conjugate_gradient


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

    def test_rejects_non_symmetric_system_and_exhausted_budget(self):
        with self.assertRaises(ValueError):
            preconditioned_conjugate_gradient([[2.0, 1.0], [0.0, 2.0]], [1.0, 1.0])
        with self.assertRaises(RuntimeError):
            preconditioned_conjugate_gradient(MATRIX, RIGHT_SIDE, tolerance=1e-15, max_steps=1)


if __name__ == "__main__":
    unittest.main()
