import copy
import unittest

from projects.foundations_lab.relations import (
    bitset_batch_relation_query_certificate, bitset_batch_relation_query_report,
    boolean_relation_composition_certificate, boolean_relation_composition_report,
    finite_relation_certificate, finite_relation_report, relation_reachability_certificate, relation_reachability_report,
)


class RelationTests(unittest.TestCase):
    def test_equivalence_relation_has_symmetric_matrix_and_certificate(self):
        domain, pairs = ["a", "b"], [["a", "a"], ["b", "b"], ["a", "b"], ["b", "a"]]
        report = finite_relation_report(domain, pairs)
        self.assertTrue(report["properties"]["equivalence_relation"])
        self.assertEqual(report["adjacency_matrix"], [[1, 1], [1, 1]])
        self.assertTrue(finite_relation_certificate(domain, pairs, report))

    def test_missing_composed_edge_breaks_transitivity_and_tampering_fails(self):
        domain, pairs = ["a", "b", "c"], [["a", "b"], ["b", "c"]]
        report = finite_relation_report(domain, pairs)
        self.assertFalse(report["properties"]["transitive"])
        changed = copy.deepcopy(report); changed["adjacency_matrix"][0][2] = 1
        self.assertFalse(finite_relation_certificate(domain, pairs, changed))

    def test_contract_rejects_duplicate_or_outside_pairs(self):
        with self.assertRaises(ValueError): finite_relation_report(["a"], [["a", "a"], ["a", "a"]])
        with self.assertRaises(ValueError): finite_relation_report(["a"], [["a", "b"]])

    def test_reachability_closure_records_intermediate_invariant(self):
        report = relation_reachability_report(["a", "b", "c"], [["a", "b"], ["b", "c"]])
        self.assertIn(["a", "c"], report["closure_pairs"])
        self.assertTrue(relation_reachability_certificate(["a", "b", "c"], [["a", "b"], ["b", "c"]], report))

    def test_boolean_composition_matches_sparse_two_hop_scan_and_replays(self):
        report = boolean_relation_composition_report(
            ["a", "b", "c"], [["a", "b"], ["b", "c"]], [["b", "a"], ["c", "a"]],
        )
        self.assertEqual(report["composition_pairs"], [["a", "a"], ["b", "a"]])
        self.assertTrue(report["verification"]["dense_and_sparse_pairs_match"])
        self.assertTrue(boolean_relation_composition_certificate(
            ["a", "b", "c"], [["a", "b"], ["b", "c"]], [["b", "a"], ["c", "a"]], report,
        ))
        altered = copy.deepcopy(report); altered["work"]["sparse_two_hop_scans"] = 0
        self.assertFalse(boolean_relation_composition_certificate(
            ["a", "b", "c"], [["a", "b"], ["b", "c"]], [["b", "a"], ["c", "a"]], altered,
        ))

    def test_bitset_batch_reuses_repeated_source_and_matches_sparse_outputs(self):
        report = bitset_batch_relation_query_report(
            ["a", "b", "c", "d"],
            [["a", "b"], ["a", "c"], ["b", "d"]],
            [["b", "a"], ["b", "d"], ["c", "d"], ["d", "c"]],
            ["a", "a", "b"], 2,
        )
        self.assertEqual([item["reachable_targets"] for item in report["batch_outputs"]], [["a", "d"], ["a", "d"], ["c"]])
        self.assertEqual(report["work"]["bitset_cache_hits"], 1)
        self.assertEqual(report["work"]["unique_source_count"], 2)
        self.assertTrue(report["verification"]["sparse_and_bitset_outputs_match"])
        self.assertTrue(bitset_batch_relation_query_certificate(
            ["a", "b", "c", "d"], [["a", "b"], ["a", "c"], ["b", "d"]],
            [["b", "a"], ["b", "d"], ["c", "d"], ["d", "c"]], ["a", "a", "b"], 2, report,
        ))
        altered = copy.deepcopy(report); altered["work"]["bitset_cache_hits"] = 0
        self.assertFalse(bitset_batch_relation_query_certificate(
            ["a", "b", "c", "d"], [["a", "b"], ["a", "c"], ["b", "d"]],
            [["b", "a"], ["b", "d"], ["c", "d"], ["d", "c"]], ["a", "a", "b"], 2, altered,
        ))

    def test_bitset_batch_contract_rejects_unknown_source_or_invalid_word_width(self):
        with self.assertRaises(ValueError):
            bitset_batch_relation_query_report(["a"], [], [], ["missing"], 8)
        with self.assertRaises(ValueError):
            bitset_batch_relation_query_report(["a"], [], [], ["a"], 0)
