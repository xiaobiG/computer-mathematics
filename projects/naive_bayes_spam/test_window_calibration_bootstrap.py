import copy
import unittest

from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION
from projects.naive_bayes_spam.window_calibration_bootstrap import window_calibration_bootstrap_certificate, window_calibration_bootstrap_report


class WindowCalibrationBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.reference = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [0.5] * 10, "labels": [1] * 5 + [0] * 5}
        self.current = {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": [0.8] * 10, "labels": [1] * 5 + [0] * 5}

    def test_fixed_seed_interval_replays_and_stays_descriptive(self):
        report = window_calibration_bootstrap_report("old", self.reference, "new", self.current, minimum_window_size=10, repeats=40, seed=11)
        self.assertEqual(report["bootstrap_policy"]["resampling_unit"], "labeled_observation")
        self.assertEqual(report["bootstrap_policy"]["automatic_action"], "none")
        self.assertTrue(window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, report))

    def test_certificate_rejects_interval_or_seed_change(self):
        report = window_calibration_bootstrap_report("old", self.reference, "new", self.current, minimum_window_size=10, repeats=40, seed=11)
        altered = copy.deepcopy(report); altered["ece_delta_percentile_interval"][0] = 0.0
        self.assertFalse(window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, altered))
        altered = copy.deepcopy(report); altered["bootstrap_policy"]["seed"] = 12
        self.assertFalse(window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, altered))

    def test_policy_rejects_too_few_repeats(self):
        with self.assertRaises(ValueError):
            window_calibration_bootstrap_report("old", self.reference, "new", self.current, minimum_window_size=10, repeats=19)
