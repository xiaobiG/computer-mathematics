import copy
import unittest

from projects.algorithm_lab.batch_shortest_path_updates import (
    ordered_shortest_path_updates_certificate,
    ordered_shortest_path_updates_report,
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


if __name__ == "__main__":
    unittest.main()
