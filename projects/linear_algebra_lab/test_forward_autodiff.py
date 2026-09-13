import unittest

from projects.linear_algebra_lab.forward_autodiff import (
    Dual,
    ReverseNode,
    demo_hvp_certificate,
    demo_jvp_certificate,
    demo_loss_hessian,
    demo_loss_dual,
    demo_loss_reverse,
    demo_reverse_vjp_certificate,
    forward_jvp,
    reverse_vjp,
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

    def test_one_reverse_pass_returns_all_scalar_loss_gradient_components(self):
        report = demo_reverse_vjp_certificate([0.4, -1.2])
        self.assertTrue(report["matches"])
        self.assertEqual(len(report["reverse_vjp"]), 2)
        value, gradient = reverse_vjp(demo_loss_reverse, [0.4, -1.2])
        forward_value = forward_jvp(demo_loss_dual, [0.4, -1.2], [0.0, 0.0]).value
        self.assertAlmostEqual(value, forward_value)
        self.assertEqual(gradient, report["reverse_vjp"])

    def test_hessian_vector_product_matches_a_central_gradient_difference(self):
        report = demo_hvp_certificate([0.4, -1.2], [0.3, -0.4])
        self.assertTrue(report["matches"])
        hessian = demo_loss_hessian([0.4, -1.2])
        self.assertAlmostEqual(hessian[0][1], hessian[1][0])
        self.assertEqual(len(report["analytic_hvp"]), 2)

    def test_dual_contract_rejects_bad_dimensions_and_negative_powers(self):
        with self.assertRaises(ValueError):
            forward_jvp(demo_loss_dual, [1.0], [1.0])
        with self.assertRaises(ValueError):
            Dual(2.0, 1.0) ** -1
        with self.assertRaises(ValueError):
            demo_hvp_certificate([1.0, 2.0], [1.0], step=1e-5)
        with self.assertRaises(ValueError):
            ReverseNode(2.0, adjoint=float("nan"))
        with self.assertRaises(ValueError):
            reverse_vjp(demo_loss_reverse, [])


if __name__ == "__main__":
    unittest.main()
