import copy
import unittest

from projects.naive_bayes_spam.cluster_window_calibration_bootstrap import (
    cluster_window_calibration_bootstrap_certificate,
    cluster_window_calibration_bootstrap_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION


def cluster(identifier, probabilities, labels):
    return {"cluster_id": identifier, "window": {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": probabilities, "labels": labels,
    }}


class ClusterWindowCalibrationBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.reference = [cluster("u-1", [.5, .5], [1, 0]), cluster("u-2", [.5], [0])]
        self.current = [cluster("d-1", [.8, .8], [1, 0]), cluster("d-2", [.8], [0])]

    def test_cluster_report_replays_and_preserves_declared_units(self):
        report = cluster_window_calibration_bootstrap_report(
            "old", self.reference, "new", self.current, minimum_window_size=3, repeats=20, seed=7,
        )
        self.assertEqual(report["bootstrap_policy"]["resampling_unit"], "predefined_labeled_user_or_device_cluster")
        self.assertEqual(report["cluster_sizes"]["reference"], [{"cluster_id": "u-1", "observations": 2}, {"cluster_id": "u-2", "observations": 1}])
        self.assertEqual(report["bootstrap_policy"]["automatic_action"], "none")
        self.assertTrue(cluster_window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, report))

    def test_certificate_and_contract_reject_tampering_or_ambiguous_clusters(self):
        report = cluster_window_calibration_bootstrap_report(
            "old", self.reference, "new", self.current, minimum_window_size=3, repeats=20, seed=7,
        )
        tampered = copy.deepcopy(report)
        tampered["cluster_sizes"]["current"][0]["observations"] = 9
        self.assertFalse(cluster_window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, tampered))
        with self.assertRaisesRegex(ValueError, "at least two"):
            cluster_window_calibration_bootstrap_report("old", self.reference[:1], "new", self.current, minimum_window_size=2, repeats=20)
        with self.assertRaisesRegex(ValueError, "unique"):
            cluster_window_calibration_bootstrap_report("old", self.reference + [self.reference[0]], "new", self.current, minimum_window_size=2, repeats=20)


if __name__ == "__main__":
    unittest.main()
