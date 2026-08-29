import unittest
from math import inf

from projects.floating_point_museum.error_analysis import (
    absolute_error,
    product_relative_error_bound,
    relative_error,
    subtraction_condition_number,
)


class ErrorAnalysisTests(unittest.TestCase):
    def test_absolute_and_relative_error_distinguish_scale(self):
        self.assertEqual(absolute_error(1000.0, 1001.0), 1.0)
        self.assertEqual(relative_error(1000.0, 1001.0), 0.001)
        self.assertAlmostEqual(absolute_error(0.001, 1.001), 1.0)
        self.assertGreater(relative_error(0.001, 1.001), 900.0)

    def test_product_bound_includes_the_second_order_term(self):
        bound = product_relative_error_bound(0.01, 0.02)
        self.assertAlmostEqual(bound, 0.0302)
        actual = relative_error(100.0 * 50.0, (100.0 * 1.01) * (50.0 * 1.02))
        self.assertLessEqual(actual, bound + 1e-15)

    def test_subtraction_condition_number_exposes_cancellation_and_contracts(self):
        self.assertEqual(subtraction_condition_number(10.0, 0.0), 1.0)
        self.assertEqual(subtraction_condition_number(1e16 + 2.0, 1e16), 1e16)
        self.assertEqual(subtraction_condition_number(2.0, 2.0), inf)
        with self.assertRaises(ValueError):
            relative_error(0.0, 1.0)
        with self.assertRaises(ValueError):
            product_relative_error_bound(-0.1, 0.2)


if __name__ == "__main__":
    unittest.main()
