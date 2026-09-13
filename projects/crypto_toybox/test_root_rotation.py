import unittest

from projects.crypto_toybox.root_rotation import (
    root_rotation_log_link_review,
    trust_root_rotation_certificate,
    trust_root_rotation_report,
)
from projects.crypto_toybox.transparency_log import append_only_report


def state():
    return {
        "epoch": 4, "root_ids": ["root-a", "root-b", "root-c"], "threshold": 2,
        "root_operator_ids": ["operator-a", "operator-b", "operator-c"],
        "minimum_distinct_approval_operators": 2,
    }


def proposal(**overrides):
    value = {
        "new_epoch": 5,
        "new_root_ids": ["root-b", "root-d", "root-e"],
        "new_threshold": 2,
        "approval_claims": ["root-a", "root-b"],
        "witness_evidence_available": True,
    }
    value.update(overrides)
    return value


class TrustRootRotationTests(unittest.TestCase):
    def test_append_only_log_artifact_flows_into_root_rotation_manual_review(self):
        rotation = trust_root_rotation_report(state(), proposal())
        log = append_only_report(
            ["key:root-a", "key:root-b", "key:root-c"],
            ["key:root-a", "key:root-b", "key:root-c", "key:root-d", "key:root-e"],
        )
        review = root_rotation_log_link_review(rotation, log)
        self.assertTrue(review["log_covers_added_roots"])
        self.assertEqual(review["decision"], "manual_review_with_policy_and_append_only_log_evidence")
        self.assertFalse(review["automatic_apply"])
        self.assertEqual(review["identity_binding"], "not_established_by_log_entries")

    def test_missing_log_entry_or_tampered_log_cannot_be_promoted_to_evidence(self):
        rotation = trust_root_rotation_report(state(), proposal())
        incomplete_log = append_only_report(
            ["key:root-a", "key:root-b", "key:root-c"],
            ["key:root-a", "key:root-b", "key:root-c", "key:root-d"],
        )
        review = root_rotation_log_link_review(rotation, incomplete_log)
        self.assertEqual(review["missing_log_entries"], ["key:root-e"])
        self.assertEqual(review["decision"], "manual_review_missing_added_root_log_entries")
        incomplete_log["new_entries"].append("key:root-e")
        with self.assertRaises(ValueError):
            root_rotation_log_link_review(rotation, incomplete_log)

    def test_log_coverage_cannot_promote_an_unresolved_policy_decision(self):
        rotation = trust_root_rotation_report(state(), proposal(witness_evidence_available=False))
        log = append_only_report(
            ["key:root-a", "key:root-b", "key:root-c"],
            ["key:root-a", "key:root-b", "key:root-c", "key:root-d", "key:root-e"],
        )
        review = root_rotation_log_link_review(rotation, log)
        self.assertEqual(rotation["decision"], "manual_review")
        self.assertEqual(review["decision"], "manual_review_with_append_only_log_evidence_and_unresolved_policy")

    def test_current_threshold_and_witness_evidence_allow_policy_only_transition(self):
        report = trust_root_rotation_report(state(), proposal())
        self.assertEqual(report["decision"], "accept_for_policy_only")
        self.assertFalse(report["automatic_apply"])
        self.assertEqual(report["cryptographic_verification"], "not_performed")
        self.assertTrue(trust_root_rotation_certificate(report)["valid"])

    def test_one_current_root_or_an_outsider_cannot_authorize_rotation(self):
        too_few = trust_root_rotation_report(state(), proposal(approval_claims=["root-a"]))
        outsider = trust_root_rotation_report(state(), proposal(approval_claims=["root-a", "attacker"]))
        self.assertEqual(too_few["decision"], "reject")
        self.assertIn("current_threshold_claimed", too_few["failed_checks"])
        self.assertEqual(outsider["decision"], "reject")
        self.assertIn("approval_claims_belong_to_current_roots", outsider["failed_checks"])

    def test_multiple_root_ids_from_one_operator_do_not_satisfy_independence_policy(self):
        concentrated = state() | {"root_operator_ids": ["operator-a", "operator-a", "operator-c"]}
        report = trust_root_rotation_report(concentrated, proposal())
        self.assertEqual(report["approval_operator_ids"], ["operator-a"])
        self.assertEqual(report["decision"], "reject")
        self.assertIn("approval_claims_meet_independent_operator_threshold", report["failed_checks"])

    def test_missing_witness_evidence_requires_review_not_acceptance(self):
        report = trust_root_rotation_report(state(), proposal(witness_evidence_available=False))
        self.assertEqual(report["decision"], "manual_review")
        self.assertFalse(report["automatic_apply"])

    def test_certificate_rejects_tampered_decision_and_contract_rejects_duplicates(self):
        report = trust_root_rotation_report(state(), proposal())
        report["decision"] = "reject"
        self.assertFalse(trust_root_rotation_certificate(report)["valid"])
        with self.assertRaises(ValueError):
            trust_root_rotation_report(state(), proposal(approval_claims=["root-a", "root-a"]))
        with self.assertRaises(ValueError):
            trust_root_rotation_report(state() | {"root_operator_ids": ["operator-a"]}, proposal())


if __name__ == "__main__":
    unittest.main()
