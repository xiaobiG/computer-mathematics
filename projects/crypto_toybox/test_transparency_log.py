import unittest

from projects.crypto_toybox.transparency_log import (
    append_only_certificate, append_only_report, inclusion_certificate, inclusion_proof, merkle_root,
)


class TransparencyLogTests(unittest.TestCase):
    def setUp(self): self.entries = ["key:alpha", "key:beta", "key:gamma"]

    def test_inclusion_proof_replays(self):
        proof = inclusion_proof(self.entries, 1)
        self.assertTrue(inclusion_certificate(proof))
        self.assertEqual(proof["root"], merkle_root(self.entries))

    def test_changed_entry_or_sibling_is_rejected(self):
        proof = inclusion_proof(self.entries, 1)
        proof["entry"] = "key:attacker"
        self.assertFalse(inclusion_certificate(proof))

    def test_append_keeps_prefix_but_rewrite_does_not(self):
        appended = append_only_report(self.entries, self.entries + ["key:delta"])
        rewritten = append_only_report(self.entries, ["key:alpha", "key:evil", "key:gamma", "key:delta"])
        self.assertEqual(appended["decision"], "append_only")
        self.assertTrue(append_only_certificate(appended))
        self.assertEqual(rewritten["decision"], "not_append_only")

    def test_certificate_rejects_changed_root_or_trust_claim(self):
        report = append_only_report(self.entries, self.entries + ["key:delta"])
        report["trust_anchor_update_verified"] = True
        self.assertFalse(append_only_certificate(report))

    def test_empty_or_invalid_logs_fail(self):
        with self.assertRaises(ValueError): merkle_root([])
        with self.assertRaises(ValueError): inclusion_proof(self.entries, 3)
