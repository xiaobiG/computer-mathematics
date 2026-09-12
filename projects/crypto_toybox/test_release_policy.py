import unittest

from projects.crypto_toybox.release_policy import (
    signed_release_policy_certificate,
    signed_release_policy_report,
)


def release(version=8, **overrides):
    value = {
        "version": version,
        "key_id": "demo-release-key-2026",
        "algorithm": "Ed25519",
        "context": "software-update/v1",
        "signature_claim_valid": True,
        "key_identity_trusted": True,
        "key_status": "active",
        "revocation_info_available": True,
    }
    value.update(overrides)
    return value


class SignedReleasePolicyTests(unittest.TestCase):
    def test_newer_complete_fictional_release_is_policy_accepted_but_not_installed(self):
        report = signed_release_policy_report(7, release())
        self.assertEqual(report["decision"], "accept_for_policy_only")
        self.assertEqual(report["failed_checks"], [])
        self.assertFalse(report["automatic_install"])
        self.assertTrue(signed_release_policy_certificate(report)["valid"])

    def test_valid_signature_claim_does_not_defeat_rollback_or_key_replacement(self):
        rollback = signed_release_policy_report(7, release(version=7))
        replacement = signed_release_policy_report(7, release(key_identity_trusted=False))
        self.assertEqual(rollback["decision"], "reject")
        self.assertIn("newer_than_protected_state", rollback["failed_checks"])
        self.assertEqual(replacement["decision"], "reject")
        self.assertIn("key_identity_trusted", replacement["failed_checks"])

    def test_unavailable_revocation_information_is_explicit_policy_choice(self):
        reject = signed_release_policy_report(7, release(revocation_info_available=False))
        review = signed_release_policy_report(
            7, release(revocation_info_available=False), on_revocation_info_unavailable="manual_review",
        )
        self.assertEqual(reject["decision"], "reject")
        self.assertEqual(review["decision"], "manual_review")
        self.assertFalse(review["automatic_install"])

    def test_certificate_rejects_changed_policy_conclusion(self):
        report = signed_release_policy_report(7, release())
        report["decision"] = "reject"
        certificate = signed_release_policy_certificate(report)
        self.assertFalse(certificate["decision_replays"])
        self.assertFalse(certificate["valid"])

    def test_contract_rejects_extra_or_missing_metadata(self):
        malformed = release()
        malformed["publisher"] = "untrusted display name"
        with self.assertRaises(ValueError):
            signed_release_policy_report(7, malformed)


if __name__ == "__main__":
    unittest.main()
