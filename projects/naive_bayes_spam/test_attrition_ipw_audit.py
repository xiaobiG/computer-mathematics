import copy
import unittest

from projects.naive_bayes_spam.attrition_ipw_audit import (
    attrition_ipw_observation_audit_certificate,
    attrition_ipw_observation_audit_report,
)


class AttritionIpwAuditTests(unittest.TestCase):
    def setUp(self):
        self.cohort = [
            {"unit_id": "a", "observed": True, "observation_probability": .8, "outcome": 1.0},
            {"unit_id": "b", "observed": True, "observation_probability": .4, "outcome": 0.0},
            {"unit_id": "c", "observed": False, "observation_probability": .8},
            {"unit_id": "d", "observed": False, "observation_probability": .4},
        ]

    def test_report_keeps_enrolled_denominator_and_replays(self):
        report = attrition_ipw_observation_audit_report(self.cohort, positivity_floor=.5)
        self.assertEqual(report["cohort_shape"]["enrolled_units"], 4)
        self.assertAlmostEqual(report["estimates"]["complete_case_mean"], .5)
        self.assertAlmostEqual(report["estimates"]["horvitz_thompson_mean"], .3125)
        self.assertTrue(report["observation_policy"]["positivity_review_required"])
        self.assertTrue(attrition_ipw_observation_audit_certificate(self.cohort, report))

    def test_certificate_and_contract_reject_tampering_and_hidden_missing_outcome(self):
        report = attrition_ipw_observation_audit_report(self.cohort)
        altered = copy.deepcopy(report)
        altered["estimates"]["hajek_mean"] = 1.0
        self.assertFalse(attrition_ipw_observation_audit_certificate(self.cohort, altered))
        malformed = copy.deepcopy(self.cohort)
        malformed[2]["outcome"] = 1.0
        with self.assertRaises(ValueError):
            attrition_ipw_observation_audit_report(malformed)
        malformed = copy.deepcopy(self.cohort)
        malformed[0]["observation_probability"] = 0
        with self.assertRaises(ValueError):
            attrition_ipw_observation_audit_report(malformed)


if __name__ == "__main__":
    unittest.main()
