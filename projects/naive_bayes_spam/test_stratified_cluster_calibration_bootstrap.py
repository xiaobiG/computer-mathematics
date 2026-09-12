import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.stratified_cluster_calibration_bootstrap import (
    time_stratified_cluster_calibration_bootstrap_certificate,
    time_stratified_cluster_calibration_bootstrap_report,
)


def cluster(identifier, probabilities, labels):
    return {"cluster_id": identifier, "window": {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": probabilities, "labels": labels,
    }}


class TimeStratifiedClusterBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.reference = [
            {"time_stratum_id": "early", "clusters": [cluster("r-1", [.5], [1]), cluster("r-2", [.5], [0])]},
            {"time_stratum_id": "late", "clusters": [cluster("r-3", [.5], [1]), cluster("r-4", [.5], [0])]},
        ]
        self.current = [
            {"time_stratum_id": "early", "clusters": [cluster("c-1", [.8], [1]), cluster("c-2", [.8], [0])]},
            {"time_stratum_id": "late", "clusters": [cluster("c-3", [.8], [1]), cluster("c-4", [.8], [0])]},
        ]

    def test_report_preserves_frozen_time_strata_and_cluster_units(self):
        report = time_stratified_cluster_calibration_bootstrap_report(
            "old", self.reference, "new", self.current, minimum_window_size=4, repeats=20, seed=7,
        )
        self.assertEqual(
            report["bootstrap_policy"]["resampling_unit"],
            "predefined_cluster_within_frozen_time_stratum",
        )
        self.assertEqual(
            [item["time_stratum_id"] for item in report["time_stratum_cluster_sizes"]["reference"]],
            ["early", "late"],
        )
        self.assertTrue(time_stratified_cluster_calibration_bootstrap_certificate(
            "old", self.reference, "new", self.current, report,
        ))

    def test_certificate_rejects_tampering_and_contract_rejects_cross_stratum_cluster(self):
        report = time_stratified_cluster_calibration_bootstrap_report(
            "old", self.reference, "new", self.current, minimum_window_size=4, repeats=20, seed=7,
        )
        altered = copy.deepcopy(report)
        altered["time_stratum_cluster_sizes"]["reference"][1]["clusters"][0]["observations"] = 2
        self.assertFalse(time_stratified_cluster_calibration_bootstrap_certificate(
            "old", self.reference, "new", self.current, altered,
        ))
        invalid = copy.deepcopy(self.reference)
        invalid[1]["clusters"][0]["cluster_id"] = "r-1"
        with self.assertRaises(ValueError):
            time_stratified_cluster_calibration_bootstrap_report(
                "old", invalid, "new", self.current, minimum_window_size=4, repeats=20,
            )


if __name__ == "__main__":
    unittest.main()
