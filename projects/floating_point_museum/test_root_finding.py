import unittest
from math import sqrt

from projects.floating_point_museum.root_finding import secant_root


class SecantRootTests(unittest.TestCase):
    def test_finds_square_root_without_derivative(self):
        root = secant_root(lambda value: value * value - 2, 1.0, 2.0)
        self.assertAlmostEqual(root, sqrt(2), places=10)

    def test_accepts_root_at_initial_right_endpoint(self):
        self.assertEqual(secant_root(lambda value: value - 3, 1.0, 3.0), 3.0)

    def test_rejects_vanishing_slope_and_invalid_contract(self):
        with self.assertRaises(RuntimeError):
            secant_root(lambda _: 1.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            secant_root(lambda value: value, 0.0, 1.0, max_steps=0)


if __name__ == "__main__":
    unittest.main()
