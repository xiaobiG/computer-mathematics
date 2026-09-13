import copy
import unittest

from projects.foundations_lab.summation import finite_sum, sum_of_squares_certificate, sum_of_squares_report


class SummationTests(unittest.TestCase):
    def test_sigma_style_half_open_loop_matches_square_closed_form(self):
        report = sum_of_squares_report(10)
        self.assertEqual(report["enumerated_sum"], 385.0)
        self.assertEqual(report["closed_form"], 385.0)
        self.assertTrue(report["certificate"]["enumeration_matches_closed_form"])
        self.assertTrue(sum_of_squares_certificate(10, report)["valid"])

    def test_sum_certificate_rejects_tampered_enumeration_or_closed_form(self):
        report = sum_of_squares_report(4)
        tampered = dict(report)
        tampered["enumerated_sum"] = 31.0
        certificate = sum_of_squares_certificate(4, tampered)
        self.assertFalse(certificate["enumeration_matches_half_open_sum"])
        self.assertFalse(certificate["valid"])

    def test_induction_trace_matches_the_closed_form_increment(self):
        report = sum_of_squares_report(4)
        self.assertEqual(
            report["induction"],
            {
                "case": "step",
                "previous_count": 3,
                "previous_closed_form": 14.0,
                "added_square": 16.0,
                "recursive_sum": 30.0,
                "closed_form_increment": 16.0,
                "step_preserves_closed_form": True,
            },
        )
        tampered = copy.deepcopy(report)
        tampered["induction"]["closed_form_increment"] = 15.0
        certificate = sum_of_squares_certificate(4, tampered)
        self.assertFalse(certificate["induction_trace_matches"])
        self.assertFalse(certificate["valid"])

    def test_empty_sum_and_interval_contracts_are_explicit(self):
        self.assertEqual(finite_sum(lambda value: value, 3, 3), 0.0)
        base_report = sum_of_squares_report(0)
        self.assertTrue(base_report["certificate"]["empty_sum_is_zero"])
        self.assertEqual(base_report["induction"]["case"], "base")
        self.assertTrue(sum_of_squares_certificate(0, base_report)["valid"])
        with self.assertRaises(ValueError):
            finite_sum(lambda value: value, 4, 3)
        with self.assertRaises(ValueError):
            finite_sum(lambda value: float("nan"), 0, 1)
        with self.assertRaises(ValueError):
            sum_of_squares_report(-1)
