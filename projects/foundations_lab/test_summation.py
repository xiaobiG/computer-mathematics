import unittest

from projects.foundations_lab.summation import finite_sum, sum_of_squares_report


class SummationTests(unittest.TestCase):
    def test_sigma_style_half_open_loop_matches_square_closed_form(self):
        report = sum_of_squares_report(10)
        self.assertEqual(report["enumerated_sum"], 385.0)
        self.assertEqual(report["closed_form"], 385.0)
        self.assertTrue(report["certificate"]["enumeration_matches_closed_form"])

    def test_empty_sum_and_interval_contracts_are_explicit(self):
        self.assertEqual(finite_sum(lambda value: value, 3, 3), 0.0)
        self.assertTrue(sum_of_squares_report(0)["certificate"]["empty_sum_is_zero"])
        with self.assertRaises(ValueError):
            finite_sum(lambda value: value, 4, 3)
        with self.assertRaises(ValueError):
            finite_sum(lambda value: float("nan"), 0, 1)
        with self.assertRaises(ValueError):
            sum_of_squares_report(-1)
