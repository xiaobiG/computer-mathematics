import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import (
    LABELED_WINDOW_CONTRACT_VERSION,
    labeled_window_degradation_certificate,
    labeled_window_degradation_report,
)


class LabeledWindowMonitoringTests(unittest.TestCase):
    def setUp(self):
        self.reference = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [0.9, 0.1, 0.8, 0.2],
            "labels": [1, 0, 1, 0],
        }

    def test_stable_labeled_window_reports_metrics_without_a_policy_signal(self):
        report = labeled_window_degradation_report(self.reference, copy.deepcopy(self.reference), 0.2, 0.2)
        self.assertEqual(report["reference_metrics"]["confusion_matrix"], {"tp": 2, "fp": 0, "tn": 2, "fn": 0})
        self.assertEqual(report["deltas"]["accuracy_drop"], 0.0)
        self.assertFalse(report["needs_review"])
        self.assertEqual(report["policy"]["automatic_action"], "none")
        self.assertTrue(labeled_window_degradation_certificate(self.reference, self.reference, report))

    def test_degraded_window_signals_accuracy_and_log_loss_for_human_review(self):
        current = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [0.1, 0.9, 0.2, 0.8],
            "labels": [1, 0, 1, 0],
        }
        report = labeled_window_degradation_report(self.reference, current, 0.25, 0.5)
        self.assertEqual(report["current_metrics"]["accuracy"], 0.0)
        self.assertTrue(report["signals"]["accuracy_drop"])
        self.assertTrue(report["signals"]["log_loss_increase"])
        self.assertTrue(report["needs_review"])
        self.assertEqual(report["interpretation"], "review_labeled_window")

    def test_certificate_rejects_tampering_and_contract_rejects_missing_labels(self):
        current = copy.deepcopy(self.reference)
        current["probabilities"] = [0.4, 0.6, 0.4, 0.6]
        report = labeled_window_degradation_report(self.reference, current)
        tampered = copy.deepcopy(report)
        tampered["policy"]["automatic_action"] = "retrain"
        self.assertFalse(labeled_window_degradation_certificate(self.reference, current, tampered))
        incomplete = copy.deepcopy(self.reference)
        incomplete["labels"] = []
        with self.assertRaisesRegex(ValueError, "equal length"):
            labeled_window_degradation_report(self.reference, incomplete)
