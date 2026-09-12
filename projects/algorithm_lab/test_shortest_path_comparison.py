import copy
import unittest

from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    normalize_shortest_path_input,
    shortest_path_comparison,
    shortest_path_comparison_certificate,
    shortest_path_replay_certificate,
    shortest_path_replay_json,
    shortest_path_replay_report,
)


class ShortestPathComparisonTests(unittest.TestCase):
    def test_unit_weight_graph_allows_every_algorithm(self):
        report = shortest_path_comparison(4, [(0, 1, 1.0), (0, 2, 1.0), (1, 3, 1.0), (2, 3, 1.0)], 0, 3)
        self.assertTrue(report["properties"]["all_unit_weights"])
        self.assertTrue(all(card["status"] == "applicable" for card in report["algorithms"].values()))
        self.assertEqual(report["algorithms"]["bfs"]["distance"], 2.0)
        self.assertTrue(shortest_path_comparison_certificate(4, [(0, 1, 1.0), (0, 2, 1.0), (1, 3, 1.0), (2, 3, 1.0)], 0, 3, report))

    def test_nonnegative_weight_graph_rejects_bfs_but_keeps_dijkstra(self):
        edges = [(0, 1, 5.0), (0, 2, 1.0), (2, 1, 1.0), (1, 3, 1.0), (2, 3, 10.0)]
        report = shortest_path_comparison(4, edges, 0, 3)
        self.assertEqual(report["algorithms"]["bfs"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["dijkstra"]["distance"], 3.0)
        self.assertEqual(report["algorithms"]["dijkstra"]["path"], [0, 2, 1, 3])

    def test_negative_edges_and_cycles_are_explicitly_separated(self):
        negative_edge = [(0, 1, 2.0), (0, 2, 5.0), (2, 1, -10.0), (1, 3, 4.0)]
        report = shortest_path_comparison(4, negative_edge, 0, 3)
        self.assertEqual(report["algorithms"]["dijkstra"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["bellman_ford"]["distance"], -1.0)
        self.assertEqual(report["algorithms"]["floyd_warshall"]["distance"], -1.0)

        negative_cycle = [(0, 1, 1.0), (1, 2, -3.0), (2, 1, 1.0)]
        report = shortest_path_comparison(3, negative_cycle, 0, 2)
        self.assertEqual(report["algorithms"]["bellman_ford"]["status"], "rejected")
        self.assertEqual(report["algorithms"]["floyd_warshall"]["status"], "rejected")

    def test_certificate_rejects_changed_distance_or_rejection_reason(self):
        edges = [(0, 1, 2.0), (1, 2, 2.0)]
        report = shortest_path_comparison(3, edges, 0, 2)
        tampered = copy.deepcopy(report)
        tampered["algorithms"]["dijkstra"]["distance"] = 9.0
        self.assertFalse(shortest_path_comparison_certificate(3, edges, 0, 2, tampered))
        with self.assertRaises(ValueError):
            shortest_path_comparison(2, [(0, 2, 1.0)], 0, 1)

    def test_small_graph_replay_contract_is_json_safe_and_tamper_evident(self):
        payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 4,
            "edges": [[0, 1, 5], [0, 2, 1], [2, 1, 1], [1, 3, 1]],
            "source": 0,
            "target": 3,
        }
        normalized = normalize_shortest_path_input(payload)
        self.assertEqual(normalized["edges"][0], [0, 1, 5.0])
        report = shortest_path_replay_report(payload)
        self.assertEqual(report["input"], normalized)
        self.assertTrue(shortest_path_replay_certificate(payload, report))
        self.assertEqual(shortest_path_replay_json(payload), shortest_path_replay_json(payload))
        tampered = copy.deepcopy(report)
        tampered["comparison"]["algorithms"]["dijkstra"]["distance"] = 99.0
        self.assertFalse(shortest_path_replay_certificate(payload, tampered))

    def test_small_graph_contract_rejects_oversized_or_ambiguous_input(self):
        payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 9,
            "edges": [],
            "source": 0,
            "target": 1,
        }
        with self.assertRaisesRegex(ValueError, "2 to 8"):
            normalize_shortest_path_input(payload)
        payload["vertex_count"] = 2
        payload["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "exactly"):
            normalize_shortest_path_input(payload)
