import copy
import unittest

from projects.algorithm_lab.shortest_path_comparison import (
    shortest_path_comparison,
    shortest_path_comparison_certificate,
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
