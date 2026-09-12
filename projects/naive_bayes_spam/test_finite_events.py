import unittest
from dataclasses import replace

from projects.naive_bayes_spam.finite_events import (
    event_probability,
    finite_event_certificate,
    finite_event_report,
)


class FiniteEventTests(unittest.TestCase):
    def setUp(self):
        self.two_coins = {
            ("H", "H"): 0.25, ("H", "T"): 0.25,
            ("T", "H"): 0.25, ("T", "T"): 0.25,
        }

    def test_event_identities_conditioning_and_independence_are_certified(self):
        first_head = {("H", "H"), ("H", "T")}
        second_head = {("H", "H"), ("T", "H")}
        report = finite_event_report(self.two_coins, first_head, second_head)
        self.assertEqual(event_probability(self.two_coins, first_head), 0.5)
        self.assertEqual(report.intersection_probability, 0.25)
        self.assertEqual(report.union_probability, 0.75)
        self.assertEqual(report.complement_left_probability, 0.5)
        self.assertEqual(report.conditional_right_given_left, 0.5)
        self.assertEqual(report.independence_residual, 0.0)
        self.assertTrue(finite_event_certificate(self.two_coins, first_head, second_head, report))
        self.assertFalse(finite_event_certificate(
            self.two_coins, first_head, second_head, replace(report, union_probability=1.0)))

    def test_rejects_invalid_space_unknown_events_and_zero_conditioning(self):
        with self.assertRaises(ValueError):
            event_probability({"heads": 0.6, "tails": 0.6}, {"heads"})
        with self.assertRaises(ValueError):
            event_probability({"heads": 0.5, "tails": 0.5}, {"edge"})
        with self.assertRaises(ValueError):
            finite_event_report({"heads": 1.0, "tails": 0.0}, {"tails"}, {"heads"})


if __name__ == "__main__":
    unittest.main()
