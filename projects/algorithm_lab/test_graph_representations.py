import copy
import unittest

from projects.algorithm_lab.graph_representations import (
    graph_representations_certificate,
    graph_representations_report,
)


class GraphRepresentationTests(unittest.TestCase):
    def setUp(self):
        self.edges = [[0, 1], [0, 3], [1, 2], [2, 3]]
        self.queries = [[0, 3], [1, 3]]

    def test_undirected_representations_agree_and_expose_tradeoffs(self):
        report = graph_representations_report(4, self.edges, False, self.queries)
        self.assertEqual(report["adjacency_list"], [[1, 3], [0, 2], [1, 3], [0, 2]])
        self.assertEqual(report["adjacency_matrix"][0], [0, 1, 0, 1])
        self.assertEqual(report["storage"], {"adjacency_list_vertex_slots": 4, "adjacency_list_neighbor_slots": 8, "adjacency_matrix_cells": 16})
        self.assertEqual(report["neighbor_enumeration"][0], {"vertex": 0, "list_checks": 2, "matrix_checks": 4})
        self.assertEqual([row["answers_agree"] for row in report["edge_queries"]], [True, True])
        self.assertTrue(graph_representations_certificate(4, self.edges, False, self.queries, report))

    def test_directed_edges_preserve_orientation(self):
        report = graph_representations_report(3, [[0, 1]], True, [[0, 1], [1, 0]])
        self.assertEqual(report["adjacency_list"], [[1], [], []])
        self.assertEqual(report["edge_queries"][0]["adjacency_matrix_answer"], True)
        self.assertEqual(report["edge_queries"][1]["adjacency_list_answer"], False)
        self.assertEqual(report["storage"]["adjacency_list_neighbor_slots"], 1)

    def test_certificate_rejects_altered_storage_or_query_answer(self):
        report = graph_representations_report(4, self.edges, False, self.queries)
        altered = copy.deepcopy(report)
        altered["storage"]["adjacency_matrix_cells"] = 7
        self.assertFalse(graph_representations_certificate(4, self.edges, False, self.queries, altered))
        altered = copy.deepcopy(report)
        altered["edge_queries"][1]["adjacency_list_answer"] = True
        self.assertFalse(graph_representations_certificate(4, self.edges, False, self.queries, altered))

    def test_contract_rejects_duplicate_loops_and_invalid_queries(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            graph_representations_report(3, [[0, 1], [1, 0]], False, [])
        with self.assertRaisesRegex(ValueError, "distinct"):
            graph_representations_report(3, [[0, 0]], True, [])
        with self.assertRaisesRegex(ValueError, "in range"):
            graph_representations_report(3, [], True, [[0, 3]])
