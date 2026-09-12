import copy
import unittest

from projects.foundations_lab.relations import finite_relation_certificate, finite_relation_report


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
