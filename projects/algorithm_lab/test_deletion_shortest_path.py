import copy
import unittest

from projects.algorithm_lab.deletion_shortest_path import (
    deletion_shortest_path_certificate,
    deletion_shortest_path_report,
)
from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION


class DeletionShortestPathTests(unittest.TestCase):
    def setUp(self):
        self.before = {
            "contract_version": CONTRACT_VERSION,
            "vertex_count": 5,
            "edges": [[0, 1, 1], [1, 3, 1], [0, 2, 4], [2, 3, 4], [0, 4, 2]],
            "source": 0,
            "target": 3,
        }

    def test_deleting_a_recorded_path_edge_requires_full_rerun_and_can_worsen_target(self):
        after = copy.deepcopy(self.before)
        after["edges"].remove([1, 3, 1])
        report = deletion_shortest_path_report(self.before, after)
        self.assertEqual(report["before"]["distances"], 2.0)
        self.assertEqual(report["after"]["distances"], 8.0)
        self.assertTrue(report["audit"]["deleted_endpoint_pair_is_in_recorded_old_target_path"])
        self.assertTrue(report["audit"]["target_distance_worsened_or_became_unreachable"])
        self.assertTrue(deletion_shortest_path_certificate(self.before, after, report))

    def test_deleting_an_irrelevant_edge_can_leave_target_distance_unchanged(self):
        after = copy.deepcopy(self.before)
        after["edges"].remove([0, 4, 2])
        report = deletion_shortest_path_report(self.before, after)
        self.assertEqual(report["before"]["distances"], report["after"]["distances"])
        self.assertFalse(report["audit"]["deleted_endpoint_pair_is_in_recorded_old_target_path"])
        self.assertFalse(report["audit"]["target_distance_worsened_or_became_unreachable"])

    def test_contract_and_certificate_reject_insertions_or_tampering(self):
        after = copy.deepcopy(self.before)
        after["edges"].remove([1, 3, 1])
        report = deletion_shortest_path_report(self.before, after)
        tampered = copy.deepcopy(report)
        tampered["audit"]["full_recomputation_required_by_this_contract"] = False
        self.assertFalse(deletion_shortest_path_certificate(self.before, after, tampered))
        changed = copy.deepcopy(self.before)
        changed["edges"].append([3, 4, 1])
        with self.assertRaisesRegex(ValueError, "exactly one removed edge"):
            deletion_shortest_path_report(self.before, changed)


if __name__ == "__main__":
    unittest.main()
