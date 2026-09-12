import copy
import unittest

from projects.naive_bayes_spam.categorical_drift_bootstrap import (
    categorical_drift_bootstrap_certificate,
    categorical_drift_bootstrap_report,
)


def width(interval):
    return interval[1] - interval[0]


class CategoricalDriftBootstrapTests(unittest.TestCase):
    def test_same_empirical_shift_has_wider_uncertainty_in_small_windows(self):
        small = categorical_drift_bootstrap_report(
            ["ham"] * 8 + ["spam"] * 2, ["ham"] * 2 + ["spam"] * 8,
            repeats=200, seed=11,
        )
        large = categorical_drift_bootstrap_report(
            ["ham"] * 800 + ["spam"] * 200, ["ham"] * 200 + ["spam"] * 800,
            repeats=200, seed=11,
        )
        # Additive smoothing makes PSI only approximately equal across the
        # two denominators even though their empirical proportions match.
        self.assertAlmostEqual(small["point_report"]["psi"], large["point_report"]["psi"], places=5)
        self.assertAlmostEqual(small["point_report"]["total_variation"], large["point_report"]["total_variation"], places=5)
        self.assertGreater(width(small["psi_percentile_interval"]), width(large["psi_percentile_interval"]))
        self.assertGreater(width(small["total_variation_percentile_interval"]), width(large["total_variation_percentile_interval"]))

    def test_fixed_seed_report_replays_with_frozen_support(self):
        reference, current = ["ham"] * 9 + ["spam"], ["ham"] * 4 + ["spam"] * 6
        report = categorical_drift_bootstrap_report(reference, current, repeats=20, seed=7)
        self.assertEqual(report["category_universe"], ["ham", "spam"])
        self.assertEqual(report["sample_sizes"], {"reference": 10, "current": 10})
        self.assertEqual(report["bootstrap_policy"]["resampling_unit"], "iid_categorical_observation")
        self.assertTrue(categorical_drift_bootstrap_certificate(reference, current, report))

    def test_certificate_rejects_interval_or_policy_tampering_and_bad_inputs(self):
        reference, current = ["ham"] * 9 + ["spam"], ["ham"] * 4 + ["spam"] * 6
        report = categorical_drift_bootstrap_report(reference, current, repeats=20, seed=7)
        tampered = copy.deepcopy(report)
        tampered["psi_percentile_interval"][1] += .01
        self.assertFalse(categorical_drift_bootstrap_certificate(reference, current, tampered))
        tampered = copy.deepcopy(report)
        tampered["bootstrap_policy"]["automatic_action"] = "retrain"
        self.assertFalse(categorical_drift_bootstrap_certificate(reference, current, tampered))
        with self.assertRaisesRegex(ValueError, "at least 20"):
            categorical_drift_bootstrap_report(reference, current, repeats=19)
        with self.assertRaisesRegex(ValueError, "confidence_level"):
            categorical_drift_bootstrap_report(reference, current, confidence_level=1)


if __name__ == "__main__":
    unittest.main()
