import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.window_calibration_comparison import (
    window_calibration_comparison_certificate,
    window_calibration_comparison_report,
)


class WindowCalibrationComparisonTests(unittest.TestCase):
    def setUp(self):
        self.reference = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [0.5] * 10, "labels": [1] * 5 + [0] * 5}
        self.current = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [0.8] * 10, "labels": [1] * 5 + [0] * 5}

    def test_frozen_windows_report_descriptive_ece_delta_and_review_only(self):
        report = window_calibration_comparison_report("2025-Q1", self.reference, "2025-Q2", self.current, bins=5, minimum_window_size=10, ece_delta_review_threshold=.2)
        self.assertAlmostEqual(report["comparison"]["expected_calibration_error_delta"], .3)
        self.assertTrue(report["comparison"]["needs_review"])
        self.assertEqual(report["causal_interpretation"], "not_established")
        self.assertTrue(window_calibration_comparison_certificate("2025-Q1", self.reference, "2025-Q2", self.current, report))

    def test_certificate_rejects_changed_policy_or_delta(self):
        report = window_calibration_comparison_report("baseline", self.reference, "current", self.current, minimum_window_size=10)
        altered = copy.deepcopy(report)
        altered["comparison"]["brier_delta"] = 0.0
        self.assertFalse(window_calibration_comparison_certificate("baseline", self.reference, "current", self.current, altered))
        altered = copy.deepcopy(report)
        altered["policy"]["ece_delta_review_threshold"] = .9
        self.assertFalse(window_calibration_comparison_certificate("baseline", self.reference, "current", self.current, altered))

    def test_contract_requires_distinct_names_and_sufficient_frozen_windows(self):
        with self.assertRaisesRegex(ValueError, "differ"):
            window_calibration_comparison_report("same", self.reference, "same", self.current, minimum_window_size=10)
        with self.assertRaisesRegex(ValueError, "minimum_window_size"):
            window_calibration_comparison_report("old", self.reference, "new", self.current, minimum_window_size=11)
