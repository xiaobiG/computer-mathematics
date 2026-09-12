import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.subgroup_monitoring import subgroup_certificate, subgroup_report


class SubgroupMonitoringTests(unittest.TestCase):
    def setUp(self):
        self.window = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [.9, .1, .8, .2, .7, .3], "labels": [1, 0, 1, 0, 1, 0]}

    def test_small_group_is_refused_and_large_group_has_metrics(self):
        declared = ["a", "b", "c"]
        report = subgroup_report(self.window, ["a", "a", "a", "a", "b", "b"], 3, declared)
        self.assertTrue(report["subgroups"][0]["sufficient_sample"])
        self.assertFalse(report["subgroups"][1]["sufficient_sample"])
        self.assertEqual(report["subgroups"][1]["interpretation"], "insufficient_sample_for_group_conclusion")
        self.assertEqual(report["subgroups"][2], {
            "group": "c", "count": 0, "sufficient_sample": False,
            "metrics": None, "interpretation": "insufficient_sample_for_group_conclusion",
        })
        self.assertTrue(subgroup_certificate(self.window, ["a", "a", "a", "a", "b", "b"], report))

    def test_certificate_rejects_a_fabricated_group_conclusion(self):
        groups = ["a", "a", "a", "a", "b", "b"]
        report = subgroup_report(self.window, groups, 3, ["a", "b"])
        tampered = copy.deepcopy(report)
        tampered["subgroups"][1]["sufficient_sample"] = True
        self.assertFalse(subgroup_certificate(self.window, groups, tampered))

    def test_declared_groups_are_required_and_bind_the_observed_universe(self):
        groups = ["a", "a", "a", "a", "b", "b"]
        with self.assertRaisesRegex(ValueError, "declared_groups"):
            subgroup_report(self.window, groups, 3)
        with self.assertRaisesRegex(ValueError, "belong"):
            subgroup_report(self.window, groups, 3, ["a"])
        with self.assertRaisesRegex(ValueError, "unique"):
            subgroup_report(self.window, groups, 3, ["a", "a", "b"])
        report = subgroup_report(self.window, groups, 3, ["a", "b", "c"])
        tampered = copy.deepcopy(report)
        tampered["policy"]["declared_groups"] = ["a", "b"]
        self.assertFalse(subgroup_certificate(self.window, groups, tampered))
