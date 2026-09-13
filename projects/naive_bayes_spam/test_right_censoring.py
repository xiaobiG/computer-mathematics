import unittest
from dataclasses import replace

from projects.naive_bayes_spam.right_censoring import right_censoring_certificate, right_censoring_report


class RightCensoringTests(unittest.TestCase):
    def test_risk_sets_keep_censored_units_until_their_last_observation(self):
        observations = [
            ("a", 1.0, True), ("b", 2.0, False), ("c", 3.0, True), ("d", 4.0, False),
        ]
        report = right_censoring_report(observations, horizon=4.0)
        self.assertEqual([(step.time, step.at_risk, step.events) for step in report.steps], [(1.0, 4, 1), (3.0, 2, 1)])
        self.assertAlmostEqual(report.survival_at_horizon, 0.375)
        self.assertAlmostEqual(report.restricted_mean_survival_time, 2.875)
        self.assertAlmostEqual(report.mean_observed_time, 2.5)
        self.assertEqual(report.mean_observed_time_interpretation, "not_a_survival_estimate_when_right_censoring_is_present")
        self.assertEqual(report.independent_censoring_assumption, "declared_not_verified")
        self.assertEqual(report.automatic_action, "none")
        self.assertTrue(right_censoring_certificate(observations, 4.0, report))
        self.assertFalse(right_censoring_certificate(observations, 4.0, replace(report, survival_at_horizon=0.5)))

    def test_tied_events_precede_same_time_censoring_and_inputs_are_checked(self):
        observations = [("a", 2.0, True), ("b", 2.0, False), ("c", 3.0, False)]
        report = right_censoring_report(observations, 3.0)
        self.assertEqual((report.steps[0].at_risk, report.steps[0].events, report.steps[0].censored_at_time), (3, 1, 1))
        self.assertAlmostEqual(report.survival_at_horizon, 2.0 / 3.0)
        with self.assertRaisesRegex(ValueError, "unique"):
            right_censoring_report([("a", 1.0, True), ("a", 2.0, False)], 2.0)
        with self.assertRaisesRegex(ValueError, "boolean"):
            right_censoring_report([("a", 1.0, 1)], 2.0)


if __name__ == "__main__":
    unittest.main()
