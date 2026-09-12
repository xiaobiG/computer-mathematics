import unittest

from projects.floating_point_museum.interpolation import (
    divided_differences,
    evaluate_newton,
    interpolation_certificate,
)


class InterpolationTests(unittest.TestCase):
    def test_recovers_a_quadratic_at_nodes_and_between_them(self):
        nodes = [-1.0, 0.0, 2.0]
        coefficients = divided_differences(nodes, [2.0, 1.0, 5.0])  # x^2 + 1
        self.assertEqual(coefficients, [2.0, -1.0, 1.0])
        self.assertAlmostEqual(evaluate_newton(nodes, coefficients, 3.0), 10.0)
        self.assertTrue(all(evaluate_newton(nodes, coefficients, node) == value for node, value in zip(nodes, [2.0, 1.0, 5.0])))
        self.assertTrue(interpolation_certificate(nodes, [2.0, 1.0, 5.0], coefficients)["valid"])

    def test_certificate_rejects_a_tampered_coefficient_or_node_fit(self):
        nodes, values = [-1.0, 0.0, 2.0], [2.0, 1.0, 5.0]
        coefficients = divided_differences(nodes, values)
        tampered = list(coefficients)
        tampered[-1] += 0.1
        certificate = interpolation_certificate(nodes, values, tampered)
        self.assertFalse(certificate["coefficients_match_divided_differences"])
        self.assertFalse(certificate["all_nodes_are_reconstructed_within_tolerance"])
        self.assertFalse(certificate["valid"])

    def test_rejects_repeated_or_mismatched_nodes(self):
        with self.assertRaises(ValueError):
            divided_differences([0.0, 0.0], [1.0, 1.0])
        with self.assertRaises(ValueError):
            divided_differences([0.0], [1.0, 2.0])
        with self.assertRaises(ValueError):
            evaluate_newton([0.0], [1.0, 2.0], 0.0)
