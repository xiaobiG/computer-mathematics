import copy
import unittest

from projects.algorithm_lab.batch_shortest_path_updates import (
    ordered_shortest_path_updates_certificate,
    ordered_shortest_path_updates_report,
    versioned_shortest_path_query_certificate,
    versioned_shortest_path_query_report,
    replacement_path_cache_certificate,
    replacement_path_cache_report,
)


def state():
    return {
        "vertex_count": 3, "source": 0, "target": 2,
        "edges": [["fast", 0, 1, 1], ["slow-parallel", 0, 1, 9], ["to-target", 1, 2, 1]],
    }


class OrderedShortestPathUpdateTests(unittest.TestCase):
    def test_parallel_edge_deletion_uses_stable_id_and_each_snapshot_replays(self):
        updates = [{"kind": "delete", "edge_id": "fast"}, {"kind": "insert", "edge": ["shortcut", 0, 2, 2]}]
        report = ordered_shortest_path_updates_report(state(), updates)
        self.assertEqual(report["steps"][0]["dijkstra"]["target_distance"], 2.0)
        self.assertEqual(report["steps"][1]["dijkstra"]["target_distance"], 10.0)
        self.assertEqual(report["steps"][2]["dijkstra"]["target_distance"], 2.0)
        self.assertTrue(ordered_shortest_path_updates_certificate(state(), updates, report))

    def test_certificate_rejects_reordered_or_changed_snapshot(self):
        updates = [{"kind": "set_weight", "edge_id": "slow-parallel", "weight": 3.0}]
        report = ordered_shortest_path_updates_report(state(), updates)
        altered = copy.deepcopy(report); altered["steps"][1]["dijkstra"]["target_distance"] = 0.0
        self.assertFalse(ordered_shortest_path_updates_certificate(state(), updates, altered))

    def test_contract_rejects_missing_or_duplicate_stable_ids(self):
        with self.assertRaises(ValueError):
            ordered_shortest_path_updates_report(state(), [{"kind": "delete", "edge_id": "missing"}])
        with self.assertRaises(ValueError):
            ordered_shortest_path_updates_report(state(), [{"kind": "insert", "edge": ["fast", 0, 2, 1]}])

    def test_queries_read_declared_old_and_new_snapshots(self):
        updates = [{"kind": "delete", "edge_id": "fast"}, {"kind": "insert", "edge": ["shortcut", 0, 2, 2]}]
        report = versioned_shortest_path_query_report(state(), updates, [0, 1, 2, 0])
        self.assertEqual([item["target_distance"] for item in report["queries"]], [2.0, 10.0, 2.0, 2.0])
        self.assertIn("fast", report["queries"][0]["snapshot_edge_ids"])
        self.assertNotIn("fast", report["queries"][1]["snapshot_edge_ids"])
        self.assertTrue(versioned_shortest_path_query_certificate(state(), updates, [0, 1, 2, 0], report))
        report["queries"][1]["visible_version"] = 2
        self.assertFalse(versioned_shortest_path_query_certificate(state(), updates, [0, 1, 2, 0], report))

    def test_replacement_cache_separates_precomputation_and_lookup(self):
        report = replacement_path_cache_report(state(), ["fast", "fast", "slow-parallel"])
        self.assertEqual(report["cache"]["fast"]["target_distance"], 10.0)
        self.assertEqual([item["target_distance"] for item in report["queries"]], [10.0, 10.0, 2.0])
        self.assertEqual(report["work"], {"precomputation_full_dijkstra_runs": 4, "cache_reads": 3})
        self.assertTrue(replacement_path_cache_certificate(state(), ["fast", "fast", "slow-parallel"], report))
        report["cache"]["fast"]["target_distance"] = 2.0
        self.assertFalse(replacement_path_cache_certificate(state(), ["fast", "fast", "slow-parallel"], report))


if __name__ == "__main__":
    unittest.main()
