import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.subgroup_monitoring import subgroup_certificate, subgroup_report


class SubgroupMonitoringTests(unittest.TestCase):
    def setUp(self):
        self.window = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [.9, .1, .8, .2, .7, .3], "labels": [1, 0, 1, 0, 1, 0]}

    def test_small_group_is_refused_and_large_group_has_metrics(self):
        report = subgroup_report(self.window, ["a", "a", "a", "a", "b", "b"], 3)
        self.assertTrue(report["subgroups"][0]["sufficient_sample"])
        self.assertFalse(report["subgroups"][1]["sufficient_sample"])
        self.assertEqual(report["subgroups"][1]["interpretation"], "insufficient_sample_for_group_conclusion")
        self.assertTrue(subgroup_certificate(self.window, ["a", "a", "a", "a", "b", "b"], report))

    def test_certificate_rejects_a_fabricated_group_conclusion(self):
        groups = ["a", "a", "a", "a", "b", "b"]
        report = subgroup_report(self.window, groups, 3)
        tampered = copy.deepcopy(report)
        tampered["subgroups"][1]["sufficient_sample"] = True
        self.assertFalse(subgroup_certificate(self.window, groups, tampered))
