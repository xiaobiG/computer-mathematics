import unittest

from projects.crypto_toybox.root_rotation import (
    root_rotation_log_link_review,
    root_rotation_recovery_compatibility_certificate,
    root_rotation_recovery_compatibility_report,
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
    def test_emergency_recovery_separates_client_format_and_predeclared_authority_coverage(self):
        rotation = trust_root_rotation_report(state(), proposal())
        clients = [
            {
                "client_id": "modern", "trusted_root_ids": ["root-a", "root-b", "root-c"], "stored_epoch": 4,
                "supported_policy_versions": [1, 2], "recovery_operator_ids": ["recovery-a", "recovery-b"],
                "minimum_distinct_recovery_operators": 2,
            },
            {
                "client_id": "legacy", "trusted_root_ids": ["root-a", "root-b", "root-c"], "stored_epoch": 4,
                "supported_policy_versions": [1], "recovery_operator_ids": ["recovery-a", "recovery-b"],
                "minimum_distinct_recovery_operators": 2,
            },
            {
                "client_id": "isolated", "trusted_root_ids": ["root-a"], "stored_epoch": 4,
                "supported_policy_versions": [2], "recovery_operator_ids": ["recovery-a", "recovery-c"],
                "minimum_distinct_recovery_operators": 2,
            },
        ]
        plan = {
            "policy_format_version": 2, "compromised_root_ids": ["root-a"],
            "recovery_claim_operator_ids": ["recovery-a", "recovery-b"], "out_of_band_channel_declared": True,
        }
        report = root_rotation_recovery_compatibility_report(rotation, clients, plan)
        by_id = {item["client"]["client_id"]: item for item in report["client_reports"]}
        self.assertEqual(by_id["modern"]["decision"], "manual_recovery_with_declared_authorities")
        self.assertFalse(by_id["modern"]["checks"]["regular_approval_avoids_declared_compromised_roots"])
        self.assertEqual(by_id["legacy"]["decision"], "manual_recovery_required_unsupported_policy_format")
        self.assertEqual(by_id["isolated"]["decision"], "manual_recovery_missing_declared_authority_coverage")
        self.assertFalse(report["automatic_apply"])
        self.assertTrue(root_rotation_recovery_compatibility_certificate(rotation, clients, plan, report))

    def test_emergency_recovery_certificate_rejects_tampering_or_unpinned_incident_root(self):
        rotation = trust_root_rotation_report(state(), proposal())
        clients = [{
            "client_id": "modern", "trusted_root_ids": ["root-a", "root-b"], "stored_epoch": 4,
            "supported_policy_versions": [2], "recovery_operator_ids": ["recovery-a", "recovery-b"],
            "minimum_distinct_recovery_operators": 2,
        }]
        plan = {
            "policy_format_version": 2, "compromised_root_ids": ["root-a"],
            "recovery_claim_operator_ids": ["recovery-a", "recovery-b"], "out_of_band_channel_declared": True,
        }
        report = root_rotation_recovery_compatibility_report(rotation, clients, plan)
        report["client_reports"][0]["decision"] = "accept"
        self.assertFalse(root_rotation_recovery_compatibility_certificate(rotation, clients, plan, report))
        plan["compromised_root_ids"] = ["unknown-root"]
        with self.assertRaises(ValueError):
            root_rotation_recovery_compatibility_report(rotation, clients, plan)

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
