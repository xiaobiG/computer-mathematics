import unittest
from math import sqrt

from projects.floating_point_museum.root_finding import (
    safeguarded_newton_trace, secant_root, secant_trace, secant_trace_certificate,
)


class SecantRootTests(unittest.TestCase):
    def test_finds_square_root_without_derivative(self):
        root = secant_root(lambda value: value * value - 2, 1.0, 2.0)
        self.assertAlmostEqual(root, sqrt(2), places=10)

    def test_accepts_root_at_initial_right_endpoint(self):
        self.assertEqual(secant_root(lambda value: value - 3, 1.0, 3.0), 3.0)

    def test_secant_trace_certifies_interpolation_formula_and_event_linkage(self):
        function = lambda value: value * value - 2.0
        root, events = secant_trace(function, 1.0, 2.0)
        self.assertAlmostEqual(root, sqrt(2.0), places=10)
        self.assertTrue(events)
        self.assertLess(abs(events[-1].candidate_value), 1e-12)
        self.assertTrue(secant_trace_certificate(function, events))
        tampered = list(events)
        tampered[0] = tampered[0].__class__(
            tampered[0].iteration, tampered[0].previous, tampered[0].current,
            tampered[0].previous_value, tampered[0].current_value,
            tampered[0].candidate + 0.1, tampered[0].candidate_value,
        )
        self.assertFalse(secant_trace_certificate(function, tampered))

    def test_rejects_vanishing_slope_and_invalid_contract(self):
        with self.assertRaises(RuntimeError):
            secant_root(lambda _: 1.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            secant_root(lambda value: value, 0.0, 1.0, max_steps=0)

    def test_safeguarded_newton_returns_a_sign_change_certificate(self):
        root, events = safeguarded_newton_trace(
            lambda value: value * value - 2.0, lambda value: 2.0 * value,
            0.0, 2.0, initial=1.0,
        )
        self.assertAlmostEqual(root, sqrt(2.0), places=10)
        self.assertTrue(events)
        for event in events:
            self.assertLessEqual(event.left, root)
            self.assertLessEqual(root, event.right)
            self.assertLessEqual(event.left_value * event.right_value, 0.0)

    def test_safeguard_falls_back_when_newton_step_leaves_the_bracket(self):
        root, events = safeguarded_newton_trace(
            lambda value: value ** 3 - 2.0 * value + 2.0,
            lambda value: 3.0 * value * value - 2.0,
            -3.0, 0.0, initial=0.0,
        )
        self.assertEqual(events[0].method, "bisection")
        self.assertLess(abs(root ** 3 - 2.0 * root + 2.0), 1e-12)

    def test_safeguarded_newton_rejects_missing_bracket_and_bad_derivative(self):
        with self.assertRaises(ValueError):
            safeguarded_newton_trace(lambda value: value * value + 1.0, lambda value: 2.0 * value,
                                     -1.0, 1.0, initial=0.0)
        with self.assertRaises(RuntimeError):
            safeguarded_newton_trace(lambda value: value - 0.2, lambda _: float("nan"),
                                     0.0, 1.0, initial=0.0, max_steps=1)


if __name__ == "__main__":
    unittest.main()
