import copy
import unittest

from projects.naive_bayes_spam.stratified_association import (
    stratified_association_certificate,
    stratified_association_report,
)


class StratifiedAssociationTests(unittest.TestCase):
    def setUp(self):
        # In each severity stratum exposure has a higher success rate, while
        # its concentration in the severe stratum reverses the pooled rate.
        self.reversal_counts = {
            "mild": {
                "exposed_success": 81, "exposed_failure": 6,
                "unexposed_success": 234, "unexposed_failure": 36,
            },
            "severe": {
                "exposed_success": 192, "exposed_failure": 71,
                "unexposed_success": 55, "unexposed_failure": 25,
            },
        }

    def test_same_input_exposes_pooled_and_stratum_direction_reversal(self):
        report = stratified_association_report(self.reversal_counts)
        self.assertEqual(report["strata"]["mild"]["direction"], "exposed_higher")
        self.assertEqual(report["strata"]["severe"]["direction"], "exposed_higher")
        self.assertEqual(report["pooled"]["direction"], "exposed_lower")
        self.assertTrue(report["reversal"]["detected"])
        self.assertEqual(report["interpretation"], "descriptive_association_only")
        self.assertEqual(report["automatic_action"], "none")
        self.assertTrue(stratified_association_certificate(self.reversal_counts, report))

    def test_certificate_rejects_tampered_direction_or_reversal_claim(self):
        report = stratified_association_report(self.reversal_counts)
        tampered = copy.deepcopy(report)
        tampered["pooled"]["direction"] = "exposed_higher"
        self.assertFalse(stratified_association_certificate(self.reversal_counts, tampered))
        tampered = copy.deepcopy(report)
        tampered["reversal"]["detected"] = False
        self.assertFalse(stratified_association_certificate(self.reversal_counts, tampered))

    def test_rejects_missing_denominators_and_invalid_counts(self):
        invalid = copy.deepcopy(self.reversal_counts)
        invalid["mild"]["exposed_failure"] = -1
        with self.assertRaises(ValueError):
            stratified_association_report(invalid)
        invalid = copy.deepcopy(self.reversal_counts)
        invalid["mild"]["unexposed_success"] = 0
        invalid["mild"]["unexposed_failure"] = 0
        with self.assertRaises(ValueError):
            stratified_association_report(invalid)
        invalid = copy.deepcopy(self.reversal_counts)
        invalid["mild"]["extra"] = 1
        with self.assertRaises(ValueError):
            stratified_association_report(invalid)

    def test_mixed_stratum_directions_are_not_called_a_reversal(self):
        counts = copy.deepcopy(self.reversal_counts)
        counts["severe"] = {
            "exposed_success": 1, "exposed_failure": 9,
            "unexposed_success": 9, "unexposed_failure": 1,
        }
        report = stratified_association_report(counts)
        self.assertFalse(report["reversal"]["all_strata_same_nonzero_direction"])
        self.assertFalse(report["reversal"]["detected"])


if __name__ == "__main__":
    unittest.main()
