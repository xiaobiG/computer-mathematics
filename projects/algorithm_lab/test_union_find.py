import copy
import unittest

from projects.algorithm_lab.union_find import (
    UnionFind, path_compression_chain_certificate, path_compression_chain_report,
)


class UnionFindTests(unittest.TestCase):
    def test_union_find_maintains_the_insertion_only_connectivity_partition(self):
        union_find = UnionFind(5)
        self.assertTrue(union_find.union(0, 1))
        self.assertTrue(union_find.union(1, 2))
        self.assertTrue(union_find.connected(0, 2))
        self.assertFalse(union_find.union(0, 2))
        self.assertFalse(union_find.connected(0, 3))
        self.assertEqual(union_find.components, 3)

    def test_path_compression_report_compares_repeated_queries_on_one_chain(self):
        report = path_compression_chain_report(6)
        self.assertEqual(report["first_find_hops"], 5)
        self.assertEqual(report["uncompressed_second_find_hops"], 5)
        self.assertEqual(report["compressed_second_find_hops"], 1)
        self.assertTrue(report["roots_agree"])
        self.assertTrue(report["compression_reduces_repeated_path_hops"])
        self.assertTrue(path_compression_chain_certificate(6, report))
        altered = copy.deepcopy(report)
        altered["compressed_second_find_hops"] = 5
        self.assertFalse(path_compression_chain_certificate(6, altered))

    def test_contracts_reject_invalid_vertices_and_tiny_chain_reports(self):
        with self.assertRaises(IndexError):
            UnionFind(2).find(2)
        with self.assertRaises(ValueError):
            UnionFind(-1)
        with self.assertRaises(ValueError):
            path_compression_chain_report(1)


if __name__ == "__main__":
    unittest.main()
