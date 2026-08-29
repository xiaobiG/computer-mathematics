import unittest

from projects.floating_point_museum.simulation import estimate_pi, simulation_report


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

    def test_report_rejects_missing_repetitions(self):
        with self.assertRaises(ValueError):
            simulation_report(100, seeds=())


if __name__ == "__main__":
    unittest.main()
