import copy
import unittest

from projects.crypto_toybox.revocation_freshness import (
    revocation_status_freshness_certificate,
    revocation_status_freshness_report,
)


def response(**overrides):
    value = {
        "issuer": "example-updates", "key_id": "release-key-2026", "status": "good",
        "this_update": 100, "produced_at": 101, "next_update": 120, "signer_authorized": True,
    }
    value.update(overrides)
    return value


class RevocationFreshnessTests(unittest.TestCase):
    def test_authorized_fresh_good_status_is_only_policy_accepted(self):
        report = revocation_status_freshness_report("example-updates", "release-key-2026", response(), 110)
        self.assertEqual(report["decision"], "fresh_good_status_for_policy_only")
        self.assertFalse(report["automatic_install"])
        self.assertTrue(revocation_status_freshness_certificate("example-updates", "release-key-2026", response(), 110, report))

    def test_expired_or_unknown_status_is_rejected_instead_of_treated_as_good(self):
        expired = revocation_status_freshness_report("example-updates", "release-key-2026", response(), 121)
        unknown = revocation_status_freshness_report(
            "example-updates", "release-key-2026", response(status="unknown"), 110,
        )
        self.assertIn("next_update_has_not_elapsed", expired["failed_checks"])
        self.assertIn("status_is_good", unknown["failed_checks"])
        self.assertEqual(expired["decision"], "reject")
        self.assertEqual(unknown["decision"], "reject")

    def test_target_authority_and_certificate_are_tamper_evident(self):
        report = revocation_status_freshness_report(
            "example-updates", "release-key-2026", response(signer_authorized=False), 110,
        )
        self.assertIn("status_signer_is_authorized", report["failed_checks"])
        altered = copy.deepcopy(report)
        altered["decision"] = "fresh_good_status_for_policy_only"
        self.assertFalse(
            revocation_status_freshness_certificate(
                "example-updates", "release-key-2026", response(signer_authorized=False), 110, altered,
            ),
        )
        with self.assertRaises(ValueError):
            revocation_status_freshness_report("example-updates", "release-key-2026", response(next_update=100), 110)


if __name__ == "__main__":
    unittest.main()
