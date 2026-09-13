import unittest

from projects.floating_point_museum.simulation import (
    estimate_pi, simulation_report, simulation_report_certificate,
    truth_target_stopping_report, truth_target_stopping_report_certificate,
)


class SimulationTests(unittest.TestCase):
    def test_same_seed_reproduces_same_estimate(self):
        self.assertEqual(estimate_pi(1_000, seed=2026), estimate_pi(1_000, seed=2026))

    def test_different_sample_counts_are_validated(self):
        with self.assertRaises(ValueError):
            estimate_pi(0, seed=2026)

    def test_report_has_expected_shape_and_nonnegative_uncertainty(self):
        report = simulation_report(1_000, seeds=(1, 2, 3))
        self.assertEqual(report["runs"], 3)
        self.assertEqual(report["samples_per_run"], 1_000)
        self.assertGreater(report["mean"], 2.5)
        self.assertLess(report["mean"], 3.8)
        self.assertGreaterEqual(report["sample_std"], 0.0)
        self.assertGreaterEqual(report["standard_error"], 0.0)
        self.assertTrue(simulation_report_certificate(1_000, seeds=(1, 2, 3), report=report))
        tampered = dict(report)
        tampered["mean"] = 3.141592653589793
        self.assertFalse(simulation_report_certificate(1_000, seeds=(1, 2, 3), report=tampered))

    def test_report_rejects_missing_repetitions(self):
        with self.assertRaises(ValueError):
            simulation_report(100, seeds=())

    def test_truth_target_stopping_tracks_prefixes_and_certifies_selection(self):
        report = truth_target_stopping_report(100, 5, seed=2026, tolerance=4.0)
        self.assertEqual(report["contract"], "truth-target-stopping-counterexample/v1")
        self.assertEqual(report["stage_samples"], (100, 200, 300, 400, 500))
        self.assertEqual(report["first_within_tolerance_stage"], 1)
        self.assertEqual(report["stopping_status"], "stopped_by_truth_target")
        self.assertEqual(report["automatic_action"], "none")
        self.assertTrue(truth_target_stopping_report_certificate(
            100, 5, seed=2026, tolerance=4.0, report=report,
        ))
        tampered = dict(report)
        tampered["first_within_tolerance_stage"] = 2
        self.assertFalse(truth_target_stopping_report_certificate(
            100, 5, seed=2026, tolerance=4.0, report=tampered,
        ))

    def test_zero_tolerance_does_not_forge_a_truth_target_hit(self):
        report = truth_target_stopping_report(100, 3, seed=2026, tolerance=0.0)
        self.assertIsNone(report["first_within_tolerance_stage"])
        self.assertEqual(report["stopping_status"], "truth_target_not_met")
        with self.assertRaisesRegex(ValueError, "positive integer"):
            truth_target_stopping_report(0, 3, seed=2026, tolerance=0.1)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            truth_target_stopping_report(100, 3, seed=2026, tolerance=-0.1)


if __name__ == "__main__":
    unittest.main()
