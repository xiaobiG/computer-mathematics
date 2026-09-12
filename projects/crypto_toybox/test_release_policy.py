import unittest

from projects.crypto_toybox.release_policy import (
    signed_release_policy_certificate,
    signed_release_policy_report,
)


def release(version=8, **overrides):
    value = {
        "version": version,
        "issuer": "example-updates",
        "key_id": "demo-release-key-2026",
        "algorithm": "Ed25519",
        "purpose": "code-signing",
        "context": "software-update/v1",
        "signature_claim_valid": True,
        "revocation_info_available": True,
    }
    value.update(overrides)
    return value


def registry(**overrides):
    record = {
        "issuer": "example-updates",
        "key_id": "demo-release-key-2026",
        "algorithm": "Ed25519",
        "purpose": "code-signing",
        "status": "active",
    }
    record.update(overrides)
    return [record]


class SignedReleasePolicyTests(unittest.TestCase):
    def test_newer_complete_fictional_release_is_policy_accepted_but_not_installed(self):
        report = signed_release_policy_report(7, release(), registry())
        self.assertEqual(report["decision"], "accept_for_policy_only")
        self.assertEqual(report["failed_checks"], [])
        self.assertFalse(report["automatic_install"])
        self.assertTrue(signed_release_policy_certificate(report)["valid"])

    def test_valid_signature_claim_does_not_defeat_rollback_or_key_replacement(self):
        rollback = signed_release_policy_report(7, release(version=7), registry())
        replacement = signed_release_policy_report(7, release(issuer="attacker"), registry())
        self.assertEqual(rollback["decision"], "reject")
        self.assertIn("newer_than_protected_state", rollback["failed_checks"])
        self.assertEqual(replacement["decision"], "reject")
        self.assertIn("issuer_key_binding_is_registered", replacement["failed_checks"])

    def test_unavailable_revocation_information_is_explicit_policy_choice(self):
        reject = signed_release_policy_report(7, release(revocation_info_available=False), registry())
        review = signed_release_policy_report(
            7, release(revocation_info_available=False), registry(), on_revocation_info_unavailable="manual_review",
        )
        self.assertEqual(reject["decision"], "reject")
        self.assertEqual(review["decision"], "manual_review")
        self.assertFalse(review["automatic_install"])

    def test_certificate_rejects_changed_policy_conclusion(self):
        report = signed_release_policy_report(7, release(), registry())
        report["decision"] = "reject"
        certificate = signed_release_policy_certificate(report)
        self.assertFalse(certificate["decision_replays"])
        self.assertFalse(certificate["valid"])

    def test_contract_rejects_extra_or_missing_metadata(self):
        malformed = release()
        malformed["publisher"] = "untrusted display name"
        with self.assertRaises(ValueError):
            signed_release_policy_report(7, malformed, registry())

    def test_registry_binds_issuer_key_algorithm_purpose_and_status(self):
        wrong_algorithm = signed_release_policy_report(7, release(algorithm="RSA-PSS-SHA256"), registry())
        revoked = signed_release_policy_report(7, release(), registry(status="revoked"))
        wrong_purpose = signed_release_policy_report(7, release(purpose="tls-auth"), registry())
        self.assertIn("algorithm_matches_registered_key", wrong_algorithm["failed_checks"])
        self.assertIn("key_is_active", revoked["failed_checks"])
        self.assertIn("purpose_matches_expected_protocol", wrong_purpose["failed_checks"])
        report = signed_release_policy_report(7, release(), registry())
        report["trusted_key_registry"][0]["status"] = "revoked"
        self.assertFalse(signed_release_policy_certificate(report)["valid"])

    def test_registry_contract_rejects_duplicate_bindings(self):
        with self.assertRaisesRegex(ValueError, "must not repeat"):
            signed_release_policy_report(7, release(), registry() + registry())


if __name__ == "__main__":
    unittest.main()
