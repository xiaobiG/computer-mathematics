import unittest

from projects.crypto_toybox.root_rotation import (
    trust_root_rotation_certificate,
    trust_root_rotation_report,
)


def state():
    return {"epoch": 4, "root_ids": ["root-a", "root-b", "root-c"], "threshold": 2}


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


if __name__ == "__main__":
    unittest.main()
