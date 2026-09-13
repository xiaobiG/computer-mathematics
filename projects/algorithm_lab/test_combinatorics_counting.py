import copy
import unittest

from projects.algorithm_lab.combinatorics_counting import (
    inclusion_exclusion_certificate,
    inclusion_exclusion_report,
    pigeonhole_collision_certificate,
    pigeonhole_collision_report,
)


class CombinatoricsCountingTests(unittest.TestCase):
    def test_inclusion_exclusion_replays_all_signed_intersections(self):
        universe = ["a", "b", "c", "d", "e"]
        sets = {"A": ["a", "b", "c"], "B": ["b", "c", "d"], "C": ["c", "d", "e"]}
        report = inclusion_exclusion_report(universe, sets)
        self.assertEqual(report["direct_union_count"], 5)
        self.assertEqual(report["inclusion_exclusion_count"], 5)
        self.assertTrue(report["counts_match"])
        self.assertEqual(len(report["terms"]), 7)
        self.assertTrue(inclusion_exclusion_certificate(universe, sets, report))
        altered = copy.deepcopy(report)
        altered["terms"][3]["sign"] = 1
        self.assertFalse(inclusion_exclusion_certificate(universe, sets, altered))

    def test_pigeonhole_report_returns_a_witness_only_when_forced(self):
        crowded = {"u1": "0", "u2": "1", "u3": "0"}
        report = pigeonhole_collision_report(crowded, ["0", "1"])
        self.assertTrue(report["collision_is_forced"])
        self.assertEqual(report["collision_witness"], ("0", ("u1", "u3")))
        self.assertTrue(pigeonhole_collision_certificate(crowded, ["0", "1"], report))
        altered = dict(report)
        altered["collision_witness"] = None
        self.assertFalse(pigeonhole_collision_certificate(crowded, ["0", "1"], altered))

        uncrowded = pigeonhole_collision_report({"u1": "0", "u2": "1"}, ["0", "1", "2"])
        self.assertFalse(uncrowded["collision_is_forced"])
        self.assertIsNone(uncrowded["collision_witness"])

        accidental = pigeonhole_collision_report({"u1": "0", "u2": "0"}, ["0", "1", "2"])
        self.assertFalse(accidental["collision_is_forced"])
        self.assertEqual(accidental["collision_witness"], ("0", ("u1", "u2")))

    def test_contract_rejects_ambiguous_members_and_nonstring_assignments(self):
        with self.assertRaises(ValueError):
            inclusion_exclusion_report(["a", "a"], {"A": ["a"], "B": ["a"]})
        with self.assertRaises(ValueError):
            inclusion_exclusion_report(["a", "b"], {"A": ["a", "a"], "B": ["b"]})
        with self.assertRaises(ValueError):
            pigeonhole_collision_report({"u": 1}, ["0"])
        with self.assertRaises(ValueError):
            pigeonhole_collision_report({"u": "unknown"}, ["0"])


if __name__ == "__main__":
    unittest.main()
