import copy
import unittest

from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION
from projects.algorithm_lab.shortest_path_update import (
    UPDATE_CONTRACT_VERSION,
    shortest_path_update_certificate,
    shortest_path_update_report,
)


class ShortestPathUpdateTests(unittest.TestCase):
    def setUp(self):
        self.before = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 4,
            "edges": [[0, 1, 5], [0, 2, 1], [2, 1, 1], [1, 3, 1]],
            "source": 0,
            "target": 3,
        }

    def test_added_edge_invalidates_old_evidence_and_exposes_outcome_change(self):
        after = copy.deepcopy(self.before)
        after["edges"].append([0, 3, 1])
        report = shortest_path_update_report(self.before, after)
        self.assertEqual(report["contract_version"], UPDATE_CONTRACT_VERSION)
        self.assertTrue(report["delta"]["graph_changed"])
        self.assertEqual(report["delta"]["added_edges"], [[0, 3, 1.0]])
        self.assertFalse(report["invalidation"]["old_comparison_report_valid_for_after"])
        self.assertIn("dijkstra", report["algorithm_outcome_changes"])
        self.assertTrue(shortest_path_update_certificate(self.before, after, report))

    def test_irrelevant_edge_still_invalidates_input_bound_report_even_when_outcome_matches(self):
        after = copy.deepcopy(self.before)
        after["edges"].append([3, 2, 4])
        report = shortest_path_update_report(self.before, after)
        self.assertFalse(report["invalidation"]["old_workload_report_valid_for_after"])
        self.assertEqual(report["algorithm_outcome_changes"], {})

    def test_certificate_detects_changed_fingerprint_delta_and_query_scope(self):
        after = copy.deepcopy(self.before)
        after["edges"][0][2] = 2
        report = shortest_path_update_report(self.before, after)
        tampered = copy.deepcopy(report)
        tampered["invalidation"]["old_query_boundary_report_valid_for_after"] = True
        self.assertFalse(shortest_path_update_certificate(self.before, after, tampered))
        after["target"] = 2
        with self.assertRaisesRegex(ValueError, "keep vertex_count, source and target fixed"):
            shortest_path_update_report(self.before, after)

