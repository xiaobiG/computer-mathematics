import unittest

from projects.linear_algebra_lab.forward_autodiff import (
    Dual,
    demo_jvp_certificate,
    demo_loss_dual,
    forward_jvp,
)


class ForwardAutodiffTests(unittest.TestCase):
    def test_forward_mode_jvp_matches_gradient_dot_direction(self):
        report = demo_jvp_certificate([0.4, -1.2], [0.3, -0.4])
        self.assertTrue(report["matches"])
        self.assertNotEqual(report["forward_jvp"], 0.0)

    def test_coordinate_directions_recover_the_two_gradient_components(self):
        first = forward_jvp(demo_loss_dual, [0.4, -1.2], [1.0, 0.0])
        second = forward_jvp(demo_loss_dual, [0.4, -1.2], [0.0, 1.0])
        self.assertTrue(demo_jvp_certificate([0.4, -1.2], [1.0, 0.0])["matches"])
        self.assertTrue(demo_jvp_certificate([0.4, -1.2], [0.0, 1.0])["matches"])
        self.assertNotEqual(first.tangent, second.tangent)

    def test_dual_contract_rejects_bad_dimensions_and_negative_powers(self):
        with self.assertRaises(ValueError):
            forward_jvp(demo_loss_dual, [1.0], [1.0])
        with self.assertRaises(ValueError):
            Dual(2.0, 1.0) ** -1


if __name__ == "__main__":
    unittest.main()
