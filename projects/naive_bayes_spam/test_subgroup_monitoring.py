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

    def test_predeclared_pair_uses_a_family_adjusted_difference_interval(self):
        # Accuracy is 15/20 in a and 8/20 in b.  This is a normal
        # approximation for independent finite groups, not a causal claim.
        window = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [.9] * 15 + [.1] * 5 + [.9] * 8 + [.1] * 12,
            "labels": [1] * 40,
        }
        groups = ["a"] * 20 + ["b"] * 20
        report = subgroup_report(window, groups, 20, ["a", "b", "c"], [["a", "b"], ["a", "c"]])
        observed, refused = report["comparisons"]
        self.assertEqual(observed["groups"], ["a", "b"])
        self.assertEqual(observed["status"], "difference_interval_excludes_zero")
        self.assertAlmostEqual(observed["accuracy_difference_left_minus_right"], .35)
        self.assertLess(observed["interval"][0], observed["accuracy_difference_left_minus_right"])
        self.assertEqual(refused["status"], "insufficient_sample_for_pairwise_comparison")
        self.assertTrue(subgroup_certificate(window, groups, report))
        altered = copy.deepcopy(report)
        altered["policy"]["comparison_pairs"] = [["a", "c"]]
        self.assertFalse(subgroup_certificate(window, groups, altered))

    def test_sparse_success_or_failure_cells_refuse_normal_difference_interval(self):
        window = {
            "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
            "probabilities": [.9] * 20 + [.1] * 20,
            "labels": [1] * 40,
        }
        report = subgroup_report(window, ["a"] * 20 + ["b"] * 20, 20, ["a", "b"], [["a", "b"]])
        comparison = report["comparisons"][0]
        self.assertEqual(comparison["status"], "normal_approximation_inapplicable")
        self.assertEqual(comparison["interval"], None)
        self.assertEqual(comparison["observed_success_and_failure_counts"], [20.0, 0.0, 0.0, 20.0])

    def test_comparison_pairs_must_be_frozen_and_nonduplicated(self):
        groups = ["a", "a", "a", "a", "b", "b"]
        with self.assertRaisesRegex(ValueError, "distinct declared"):
            subgroup_report(self.window, groups, 3, ["a", "b"], [["a", "a"]])
        with self.assertRaisesRegex(ValueError, "repeat"):
            subgroup_report(self.window, groups, 3, ["a", "b"], [["a", "b"], ["b", "a"]])
