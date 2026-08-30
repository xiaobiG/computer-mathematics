"""Cross-module audit for the v1.3 delayed-label learning chain."""

import unittest

from projects.naive_bayes_spam.joint_evidence_monitoring import (
    JOINT_EVIDENCE_CONTRACT_VERSION,
    joint_evidence_certificate,
    joint_evidence_report,
)
from projects.naive_bayes_spam.labeled_window_monitoring import (
    LABELED_WINDOW_CONTRACT_VERSION,
    labeled_window_degradation_certificate,
    labeled_window_degradation_report,
)
from projects.naive_bayes_spam.subgroup_monitoring import subgroup_certificate, subgroup_report


class MonitoringLearningChainTests(unittest.TestCase):
    def test_same_window_replays_overall_joint_and_subgroup_evidence(self):
        reference = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [.9, .1, .8, .2, .7, .3], "labels": [1, 0, 1, 0, 1, 0]}
        current = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [.1, .9, .2, .8, .7, .3], "labels": [1, 0, 1, 0, 1, 0]}
        overall = labeled_window_degradation_report(reference, current, .2, .2)
        self.assertTrue(overall["needs_review"])
        self.assertTrue(labeled_window_degradation_certificate(reference, current, overall))
        reference_snapshot = {"contract_version": JOINT_EVIDENCE_CONTRACT_VERSION, "categories": ["ham", "ham", "prize", "prize", "ham", "prize"], "labeled_window": reference}
        current_snapshot = {"contract_version": JOINT_EVIDENCE_CONTRACT_VERSION, "categories": ["invoice", "invoice", "prize", "prize", "ham", "prize"], "labeled_window": current}
        joint = joint_evidence_report(reference_snapshot, current_snapshot, psi_threshold=.1, accuracy_drop_threshold=.2)
        self.assertEqual(joint["causal_interpretation"], "not_established")
        self.assertTrue(joint_evidence_certificate(reference_snapshot, current_snapshot, joint))
        subgroup = subgroup_report(current, ["source-a"] * 4 + ["source-b"] * 2, 3)
        self.assertTrue(subgroup_certificate(current, ["source-a"] * 4 + ["source-b"] * 2, subgroup))
        self.assertFalse(subgroup["subgroups"][1]["sufficient_sample"])
