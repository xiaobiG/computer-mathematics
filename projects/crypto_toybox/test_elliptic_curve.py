import unittest

from projects.crypto_toybox.elliptic_curve import ToyCurve


class ToyCurveTests(unittest.TestCase):
    def setUp(self):
        self.curve = ToyCurve(p=17, a=2, b=2)
        self.generator = (5, 1)

    def test_identity_and_inverse(self):
        inverse = (5, 16)
        self.assertEqual(self.curve.add(self.generator, None), self.generator)
        self.assertEqual(self.curve.add(self.generator, inverse), None)

    def test_doubling_and_scalar_multiplication_stay_on_curve(self):
        twice = self.curve.add(self.generator, self.generator)
        self.assertEqual(twice, (6, 3))
        self.assertTrue(self.curve.contains(twice))
        self.assertEqual(self.curve.scalar_multiply(7, self.generator), (0, 6))
        self.assertEqual(self.curve.scalar_multiply(0, self.generator), None)

    def test_repeated_addition_agrees_with_double_and_add(self):
        repeated = None
        for _ in range(5):
            repeated = self.curve.add(repeated, self.generator)
        self.assertEqual(self.curve.scalar_multiply(5, self.generator), repeated)

    def test_rejects_singular_curve_off_curve_point_and_negative_scalar(self):
        with self.assertRaises(ValueError):
            ToyCurve(p=17, a=0, b=0)
        with self.assertRaises(ValueError):
            ToyCurve(p=15, a=2, b=2)
        with self.assertRaises(ValueError):
            self.curve.add(self.generator, (1, 1))
        with self.assertRaises(ValueError):
            self.curve.scalar_multiply(-1, self.generator)


if __name__ == "__main__":
    unittest.main()
