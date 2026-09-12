import copy
import unittest

from projects.algorithm_lab.incremental_shortest_path import (
    incremental_shortest_path_certificate,
    incremental_shortest_path_report,
)
from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION


class IncrementalShortestPathTests(unittest.TestCase):
    def setUp(self):
        self.before = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 5,
            "edges": [[0, 1, 10], [1, 2, 1], [2, 3, 1], [0, 4, 2]],
            "source": 0,
            "target": 3,
        }

    def test_inserted_edge_repairs_downstream_distances_and_matches_full_rerun(self):
        after = copy.deepcopy(self.before)
        after["edges"].append([0, 1, 1])
        report = incremental_shortest_path_report(self.before, after)
        self.assertTrue(report["repair"]["seed_improved"])
        self.assertEqual(report["repair"]["target_distance"], 3.0)
        self.assertEqual(report["repair"]["target_path"], [0, 1, 2, 3])
        self.assertEqual(report["repair"]["distances"], report["full_recomputation"]["distances"])
        self.assertTrue(report["verification"]["all_distances_match_full_recomputation"])
        self.assertTrue(incremental_shortest_path_certificate(self.before, after, report))

    def test_irrelevant_insertion_is_a_valid_no_work_repair(self):
        after = copy.deepcopy(self.before)
        after["edges"].append([4, 3, 100])
        report = incremental_shortest_path_report(self.before, after)
        self.assertFalse(report["repair"]["seed_improved"])
        self.assertEqual(report["repair"]["edge_scans"], 0)
        self.assertEqual(report["repair"]["distances"], report["full_recomputation"]["distances"])

    def test_certificate_and_contract_reject_broader_updates(self):
        after = copy.deepcopy(self.before)
        after["edges"].append([0, 1, 1])
        report = incremental_shortest_path_report(self.before, after)
        tampered = copy.deepcopy(report)
        tampered["repair"]["edge_scans"] = 0
        self.assertFalse(incremental_shortest_path_certificate(self.before, after, tampered))
        removed = copy.deepcopy(self.before)
        removed["edges"].pop()
        with self.assertRaisesRegex(ValueError, "exactly one inserted edge"):
            incremental_shortest_path_report(self.before, removed)
        negative = copy.deepcopy(self.before)
        negative["edges"].append([0, 3, -1])
        with self.assertRaisesRegex(ValueError, "non-negative"):
            incremental_shortest_path_report(self.before, negative)
        changed_scope = copy.deepcopy(after)
        changed_scope["target"] = 2
        with self.assertRaisesRegex(ValueError, "keep vertex_count, source and target fixed"):
            incremental_shortest_path_report(self.before, changed_scope)
