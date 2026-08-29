import unittest

from projects.floating_point_museum.interpolation import divided_differences, evaluate_newton


class InterpolationTests(unittest.TestCase):
    def test_recovers_a_quadratic_at_nodes_and_between_them(self):
        nodes = [-1.0, 0.0, 2.0]
        coefficients = divided_differences(nodes, [2.0, 1.0, 5.0])  # x^2 + 1
        self.assertEqual(coefficients, [2.0, -1.0, 1.0])
        self.assertAlmostEqual(evaluate_newton(nodes, coefficients, 3.0), 10.0)
        self.assertTrue(all(evaluate_newton(nodes, coefficients, node) == value for node, value in zip(nodes, [2.0, 1.0, 5.0])))

    def test_rejects_repeated_or_mismatched_nodes(self):
        with self.assertRaises(ValueError):
            divided_differences([0.0, 0.0], [1.0, 1.0])
        with self.assertRaises(ValueError):
            divided_differences([0.0], [1.0, 2.0])
        with self.assertRaises(ValueError):
            evaluate_newton([0.0], [1.0, 2.0], 0.0)
