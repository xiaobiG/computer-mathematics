"""Integration regression for the v1.2 shortest-path learning chain."""

import copy
import unittest

from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    shortest_path_replay_certificate,
    shortest_path_replay_report,
)
from projects.algorithm_lab.shortest_path_query_boundary import (
    shortest_path_query_boundary_certificate,
    shortest_path_query_boundary_report,
)
from projects.algorithm_lab.shortest_path_update import (
    shortest_path_update_certificate,
    shortest_path_update_report,
)
from projects.algorithm_lab.shortest_path_workload import (
    shortest_path_workload_certificate,
    shortest_path_workload_report,
)


class ShortestPathLearningChainTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 5,
            "edges": [[0, 1, 1], [1, 2, 1], [2, 4, 1], [4, 3, 1]],
            "source": 0,
            "target": 4,
        }

    def test_one_contract_drives_comparison_workload_target_boundary_and_update_audits(self):
        comparison = shortest_path_replay_report(self.payload)
        workload = shortest_path_workload_report(self.payload, query_count=2)
        boundary = shortest_path_query_boundary_report(self.payload)
        self.assertEqual(comparison["input"], workload["input"])
        self.assertEqual(comparison["input"], boundary["input"])
        self.assertTrue(shortest_path_replay_certificate(self.payload, comparison))
        self.assertTrue(shortest_path_workload_certificate(self.payload, 2, workload))
        self.assertTrue(shortest_path_query_boundary_certificate(self.payload, boundary))
        self.assertLess(
            boundary["algorithms"]["dijkstra"]["target_only"]["edge_scans"],
            boundary["algorithms"]["dijkstra"]["full_source"]["edge_scans"],
        )

        updated = copy.deepcopy(self.payload)
        updated["edges"].append([0, 4, 1])
        update = shortest_path_update_report(self.payload, updated)
        self.assertFalse(update["invalidation"]["old_comparison_report_valid_for_after"])
        self.assertIn("dijkstra", update["algorithm_outcome_changes"])
        self.assertTrue(shortest_path_update_certificate(self.payload, updated, update))

    def test_negative_edge_is_consistently_rejected_by_greedy_cards_across_reports(self):
        payload = copy.deepcopy(self.payload)
        payload["edges"] = [[0, 1, 2], [1, 2, -3], [2, 4, 4]]
        comparison = shortest_path_replay_report(payload)
        workload = shortest_path_workload_report(payload, query_count=1)
        boundary = shortest_path_query_boundary_report(payload)
        self.assertEqual(comparison["comparison"]["algorithms"]["dijkstra"]["status"], "rejected")
        self.assertEqual(workload["algorithms"]["dijkstra"]["status"], "rejected")
        self.assertEqual(boundary["algorithms"]["dijkstra"]["status"], "rejected")

