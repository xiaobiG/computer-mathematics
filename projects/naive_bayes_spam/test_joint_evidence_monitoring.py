import copy
import unittest

from projects.naive_bayes_spam.joint_evidence_monitoring import (
    JOINT_EVIDENCE_CONTRACT_VERSION,
    joint_evidence_certificate,
    joint_evidence_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION


def snapshot(categories, probabilities, labels):
    return {
        "contract_version": JOINT_EVIDENCE_CONTRACT_VERSION,
        "categories": categories,
        "labeled_window": {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": probabilities,
            "labels": labels,
        },
    }


class JointEvidenceMonitoringTests(unittest.TestCase):
    def setUp(self):
        self.reference = snapshot(["ham", "ham", "prize", "prize"], [.9, .1, .8, .2], [1, 0, 1, 0])

    def test_joint_report_keeps_input_and_outcome_evidence_separate(self):
        current = snapshot(["invoice", "invoice", "prize", "prize"], [.1, .9, .2, .8], [1, 0, 1, 0])
        report = joint_evidence_report(self.reference, current, psi_threshold=.1, accuracy_drop_threshold=.25)
        self.assertTrue(report["signals"]["input_distribution"])
        self.assertTrue(report["signals"]["labeled_performance"])
        self.assertTrue(report["needs_review"])
        self.assertEqual(report["causal_interpretation"], "not_established")
        self.assertEqual(report["policy"]["automatic_action"], "none")
        self.assertTrue(joint_evidence_certificate(self.reference, current, report))

    def test_input_signal_can_exist_without_labeled_performance_signal(self):
        current = snapshot(["invoice", "invoice", "prize", "prize"], [.9, .1, .8, .2], [1, 0, 1, 0])
        report = joint_evidence_report(self.reference, current, psi_threshold=.1, accuracy_drop_threshold=.25)
        self.assertTrue(report["signals"]["input_distribution"])
        self.assertFalse(report["signals"]["labeled_performance"])
        self.assertTrue(report["needs_review"])

    def test_certificate_rejects_causal_claim_and_mismatched_observation_count(self):
        current = copy.deepcopy(self.reference)
        report = joint_evidence_report(self.reference, current)
        tampered = copy.deepcopy(report)
        tampered["causal_interpretation"] = "input_drift_caused_loss"
        self.assertFalse(joint_evidence_certificate(self.reference, current, tampered))
        malformed = copy.deepcopy(current)
        malformed["categories"].pop()
        with self.assertRaisesRegex(ValueError, "equal length"):
            joint_evidence_report(self.reference, malformed)
