import copy
import unittest

from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION
from projects.algorithm_lab.shortest_path_query_boundary import (
    QUERY_BOUNDARY_CONTRACT_VERSION,
    shortest_path_query_boundary_certificate,
    shortest_path_query_boundary_report,
)


class ShortestPathQueryBoundaryTests(unittest.TestCase):
    def test_unit_graph_exposes_safe_bfs_and_dijkstra_early_stop(self):
        payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 5,
            "edges": [[0, 1, 1], [1, 2, 1], [2, 4, 1], [4, 3, 1]],
            "source": 0,
            "target": 4,
        }
        report = shortest_path_query_boundary_report(payload)
        self.assertEqual(report["contract_version"], QUERY_BOUNDARY_CONTRACT_VERSION)
        for name in ("bfs", "dijkstra"):
            self.assertEqual(report["algorithms"][name]["status"], "applicable")
            self.assertLess(report["algorithms"][name]["target_only"]["edge_scans"], report["algorithms"][name]["full_source"]["edge_scans"])
        self.assertEqual(report["storage"]["adjacency_list_slots"], 9)
        self.assertEqual(report["storage"]["floyd_matrix_cells"], 25)
        self.assertTrue(shortest_path_query_boundary_certificate(payload, report))

    def test_weight_and_negative_edge_boundaries_are_not_hidden(self):
        payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 4,
            "edges": [[0, 1, 2], [1, 2, -1], [2, 3, 2]],
            "source": 0,
            "target": 3,
        }
        report = shortest_path_query_boundary_report(payload)
        self.assertEqual(report["algorithms"]["bfs"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["dijkstra"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["bellman_ford"]["target_only"]["status"], "not_safe")
        self.assertEqual(report["algorithms"]["floyd_warshall"]["target_only"]["status"], "not_safe")

    def test_certificate_rejects_changed_density_storage_or_stop_claim(self):
        payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 3,
            "edges": [[0, 1, 1], [1, 2, 1]],
            "source": 0,
            "target": 2,
        }
        report = shortest_path_query_boundary_report(payload)
        tampered = copy.deepcopy(report)
        tampered["graph"]["density_class"] = "dense"
        self.assertFalse(shortest_path_query_boundary_certificate(payload, tampered))
        tampered = copy.deepcopy(report)
        tampered["algorithms"]["bellman_ford"]["target_only"]["status"] = "safe"
        self.assertFalse(shortest_path_query_boundary_certificate(payload, tampered))

