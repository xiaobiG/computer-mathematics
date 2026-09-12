import unittest

from projects.linear_algebra_lab.gradient_check import (
    demo_loss,
    demo_loss_gradient,
    gradient_check,
)


class GradientCheckTests(unittest.TestCase):
    def test_analytic_gradient_matches_central_difference(self):
        report = gradient_check(demo_loss, demo_loss_gradient, [0.4, -1.2])
        self.assertTrue(all(item.absolute_error < 1e-6 for item in report))
        self.assertTrue(all(item.relative_error < 1e-6 for item in report))

    def test_gradient_check_catches_a_deliberate_sign_error(self):
        def wrong_gradient(point: list[float]) -> list[float]:
            correct = demo_loss_gradient(point)
            return [-correct[0], correct[1]]

        report = gradient_check(demo_loss, wrong_gradient, [0.4, -1.2])
        self.assertGreater(report[0].relative_error, 0.1)
        self.assertLess(report[1].relative_error, 1e-6)

    def test_gradient_check_rejects_invalid_contracts(self):
        with self.assertRaises(ValueError):
            gradient_check(demo_loss, demo_loss_gradient, [], 1e-6)
        with self.assertRaises(ValueError):
            gradient_check(demo_loss, demo_loss_gradient, [1.0, 2.0], 0.0)
        with self.assertRaises(ValueError):
            gradient_check(demo_loss, lambda _: [1.0], [1.0, 2.0])
