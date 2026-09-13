import unittest

from projects.crypto_toybox.transparency_log import (
    append_only_certificate, append_only_report, checkpoint_certificate, checkpoint_from_entries,
    inclusion_certificate, inclusion_proof, merkle_root, split_view_certificate, split_view_report,
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

    def test_same_size_different_roots_are_only_candidate_equivocation(self):
        first = checkpoint_from_entries("fictional-log", self.entries)
        second = checkpoint_from_entries("fictional-log", ["key:alpha", "key:evil", "key:gamma"])
        report = split_view_report(first, second)
        self.assertTrue(checkpoint_certificate(first))
        self.assertTrue(report["candidate_equivocation"])
        self.assertEqual(report["decision"], "candidate_equivocation_requires_authenticated_checkpoints")
        self.assertEqual(report["checkpoint_authentication"], "not_verified")
        self.assertEqual(report["automatic_response"], "none")
        self.assertTrue(split_view_certificate(first, second, report))
        report["candidate_equivocation"] = False
        self.assertFalse(split_view_certificate(first, second, report))

    def test_different_tree_sizes_need_append_only_evidence_not_a_fork_claim(self):
        old = checkpoint_from_entries("fictional-log", self.entries)
        newer = checkpoint_from_entries("fictional-log", self.entries + ["key:delta"])
        report = split_view_report(old, newer)
        self.assertFalse(report["candidate_equivocation"])
        self.assertEqual(report["decision"], "inconclusive_requires_append_only_consistency_evidence")
        self.assertTrue(append_only_certificate(append_only_report(self.entries, self.entries + ["key:delta"])))
