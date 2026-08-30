import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.subgroup_calibration import (
    subgroup_calibration_certificate,
    subgroup_calibration_report,
)


class SubgroupCalibrationTests(unittest.TestCase):
    def test_pooled_calibration_can_hide_opposite_group_errors(self):
        # Both groups forecast 0.8.  Across the pooled 20 examples, 16 are
        # positive, so pooled ECE is zero; group A realizes 0.6 and group B 1.
        window = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [0.8] * 20,
            "labels": [1] * 6 + [0] * 4 + [1] * 10,
        }
        groups = ["a"] * 10 + ["b"] * 10
        report = subgroup_calibration_report(window, groups, bins=5, minimum_group_size=10, ece_review_threshold=0.15)
        self.assertEqual(report["overall_metrics"]["expected_calibration_error"], 0.0)
        self.assertTrue(report["needs_review"])
        self.assertEqual([row["needs_review"] for row in report["subgroups"]], [True, True])
        self.assertTrue(subgroup_calibration_certificate(window, groups, report))

    def test_small_group_refuses_a_calibration_conclusion(self):
        window = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [0.9, 0.1, 0.9, 0.1, 0.9, 0.1],
            "labels": [1, 0, 1, 0, 1, 0],
        }
        groups = ["large"] * 4 + ["small"] * 2
        report = subgroup_calibration_report(window, groups, minimum_group_size=3)
        small = next(row for row in report["subgroups"] if row["group"] == "small")
        self.assertIsNone(small["metrics"])
        self.assertEqual(small["interpretation"], "insufficient_sample_for_group_calibration_conclusion")

    def test_certificate_rejects_changed_policy_or_conclusion(self):
        window = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [0.7] * 8,
            "labels": [1] * 4 + [0] * 4,
        }
        groups = ["review"] * 8
        report = subgroup_calibration_report(window, groups, minimum_group_size=4)
        tampered = copy.deepcopy(report)
        tampered["policy"]["ece_review_threshold"] = 0.9
        self.assertFalse(subgroup_calibration_certificate(window, groups, tampered))
        tampered = copy.deepcopy(report)
        tampered["causal_interpretation"] = "established"
        self.assertFalse(subgroup_calibration_certificate(window, groups, tampered))

    def test_input_contract_rejects_unsafe_bin_and_group_policies(self):
        window = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [0.5, 0.5],
            "labels": [0, 1],
        }
        with self.assertRaises(ValueError):
            subgroup_calibration_report(window, ["a", "a"], bins=1)
        with self.assertRaises(ValueError):
            subgroup_calibration_report(window, ["a", "a"], minimum_group_size=1)
        with self.assertRaises(ValueError):
            subgroup_calibration_report(window, ["a", "a"], ece_review_threshold=1.1)
        with self.assertRaises(ValueError):
            subgroup_calibration_report(window, ["a"])
