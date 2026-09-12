import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.paired_longitudinal_calibration_bootstrap import (
    paired_longitudinal_cluster_calibration_bootstrap_certificate,
    paired_longitudinal_cluster_calibration_bootstrap_report,
)


def window(probabilities, labels):
    return {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": probabilities, "labels": labels}


def trajectory(identifier, early_reference, early_current, late_reference, late_current):
    return {"cluster_id": identifier, "time_strata": [
        {"time_stratum_id": "early", "reference_window": early_reference, "current_window": early_current},
        {"time_stratum_id": "late", "reference_window": late_reference, "current_window": late_current},
    ]}


class PairedLongitudinalBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.trajectories = [
            trajectory("u-1", window([.5, .5], [1, 0]), window([.8, .8], [1, 0]), window([.4, .4], [1, 0]), window([.95, .95], [1, 0])),
            trajectory("u-2", window([.5, .5], [0, 1]), window([.8, .8], [0, 1]), window([.4, .4], [0, 1]), window([.95, .95], [0, 1])),
        ]

    def test_report_resamples_whole_paired_trajectories_and_replays(self):
        report = paired_longitudinal_cluster_calibration_bootstrap_report(
            "old", "new", self.trajectories, minimum_window_size=4, repeats=20, seed=7,
        )
        self.assertEqual(report["bootstrap_policy"]["resampling_unit"], "whole_paired_cluster_trajectory_across_frozen_time_strata")
        self.assertEqual([row["time_stratum_id"] for row in report["per_time_stratum_ece_delta_intervals"]], ["early", "late"])
        self.assertEqual(report["first_to_last_time_trend"]["from_time_stratum_id"], "early")
        self.assertTrue(paired_longitudinal_cluster_calibration_bootstrap_certificate("old", "new", self.trajectories, report))

    def test_certificate_binds_trend_and_contract_rejects_misaligned_trajectories(self):
        report = paired_longitudinal_cluster_calibration_bootstrap_report(
            "old", "new", self.trajectories, minimum_window_size=4, repeats=20, seed=7,
        )
        altered = copy.deepcopy(report)
        altered["first_to_last_time_trend"]["point_estimate"] = 1.0
        self.assertFalse(paired_longitudinal_cluster_calibration_bootstrap_certificate("old", "new", self.trajectories, altered))
        malformed = copy.deepcopy(self.trajectories)
        malformed[1]["time_strata"][1]["time_stratum_id"] = "week-two"
        with self.assertRaises(ValueError):
            paired_longitudinal_cluster_calibration_bootstrap_report("old", "new", malformed, minimum_window_size=4, repeats=20)
        duplicate = copy.deepcopy(self.trajectories)
        duplicate[1]["cluster_id"] = "u-1"
        with self.assertRaises(ValueError):
            paired_longitudinal_cluster_calibration_bootstrap_report("old", "new", duplicate, minimum_window_size=4, repeats=20)


if __name__ == "__main__":
    unittest.main()
