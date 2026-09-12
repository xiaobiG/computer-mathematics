import unittest

from projects.linear_algebra_lab.recommendation import (
    AlsEvent, rank_one_als_report, rank_one_als_trace_certificate,
)


class RankOneAlsTests(unittest.TestCase):
    def setUp(self):
        self.ratings = [[5.0, None, 2.0], [4.0, 2.0, None], [None, 1.0, 1.0]]

    def test_observed_fit_and_trace_certificate(self):
        report = rank_one_als_report(self.ratings, iterations=20, regularization=0.1)
        self.assertLess(report.observed_rmse, 0.7)
        self.assertEqual(len(report.events), 20)
        self.assertTrue(rank_one_als_trace_certificate(self.ratings, report, iterations=20, regularization=0.1))

        tampered_events = list(report.events)
        event = tampered_events[4]
        tampered_events[4] = AlsEvent(
            event.iteration, event.user_factors, event.item_factors, event.observed_squared_error + 1.0,
        )
        tampered = report.__class__(
            report.user_factors, report.item_factors, report.predictions, report.observed_rmse,
            tuple(tampered_events),
        )
        self.assertFalse(rank_one_als_trace_certificate(self.ratings, tampered, iterations=20, regularization=0.1))

    def test_rejects_cold_start_and_invalid_contracts(self):
        with self.assertRaises(ValueError):
            rank_one_als_report([[None, None], [1.0, 2.0]])
        with self.assertRaises(ValueError):
            rank_one_als_report([[1.0, None], [2.0, None]])
        with self.assertRaises(ValueError):
            rank_one_als_report([[1.0]], iterations=0)


if __name__ == "__main__":
    unittest.main()
