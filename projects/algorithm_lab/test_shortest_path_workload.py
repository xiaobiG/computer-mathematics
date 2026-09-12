import copy
import unittest

from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION
from projects.algorithm_lab.shortest_path_workload import (
    WORKLOAD_CONTRACT_VERSION,
    shortest_path_workload_certificate,
    shortest_path_workload_report,
)


class ShortestPathWorkloadTests(unittest.TestCase):
    def setUp(self):
        self.unit_payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 4,
            "edges": [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1]],
            "source": 0,
            "target": 3,
        }

    def test_unit_graph_replays_source_count_and_work_counters(self):
        report = shortest_path_workload_report(self.unit_payload, 2)
        self.assertEqual(report["contract_version"], WORKLOAD_CONTRACT_VERSION)
        self.assertEqual(report["query_sources"], [0, 1])
        self.assertEqual(report["algorithms"]["bfs"]["work"]["runs"], 2)
        self.assertGreater(report["algorithms"]["dijkstra"]["work"]["edge_scans"], 0)
        self.assertEqual(report["algorithms"]["floyd_warshall"]["work"]["candidate_cells"], 64)
        self.assertTrue(shortest_path_workload_certificate(self.unit_payload, 2, report))

    def test_preconditions_and_floyd_query_independence_are_explicit(self):
        weighted = copy.deepcopy(self.unit_payload)
        weighted["edges"] = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        report_one = shortest_path_workload_report(weighted, 1)
        report_three = shortest_path_workload_report(weighted, 3)
        self.assertEqual(report_one["algorithms"]["bfs"]["status"], "rejected")
        self.assertEqual(report_one["algorithms"]["dijkstra"]["status"], "applicable")
        self.assertEqual(report_one["algorithms"]["floyd_warshall"]["work"]["candidate_cells"], report_three["algorithms"]["floyd_warshall"]["work"]["candidate_cells"])
        self.assertEqual(report_three["algorithms"]["floyd_warshall"]["work"]["requested_sources"], 3)

    def test_certificate_and_query_bounds_reject_tampering(self):
        report = shortest_path_workload_report(self.unit_payload, 1)
        tampered = copy.deepcopy(report)
        tampered["algorithms"]["floyd_warshall"]["work"]["candidate_cells"] = 63
        self.assertFalse(shortest_path_workload_certificate(self.unit_payload, 1, tampered))
        with self.assertRaisesRegex(ValueError, "query_count"):
            shortest_path_workload_report(self.unit_payload, 0)

    def test_negative_cycle_is_rejected_for_affected_single_source_and_all_pairs_cards(self):
        payload = copy.deepcopy(self.unit_payload)
        payload["vertex_count"] = 3
        payload["edges"] = [[0, 1, 1], [1, 2, -3], [2, 1, 1]]
        payload["target"] = 2
        report = shortest_path_workload_report(payload, 1)
        self.assertEqual(report["algorithms"]["bellman_ford"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["floyd_warshall"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["floyd_warshall"]["work"]["candidate_cells"], 27)
