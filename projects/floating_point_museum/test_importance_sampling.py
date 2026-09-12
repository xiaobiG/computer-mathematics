import copy
import unittest

from projects.floating_point_museum.importance_sampling import (
    importance_sampling_certificate, importance_sampling_report,
    log_weight_diagnostics, log_weight_diagnostics_certificate,
)


class ImportanceSamplingTests(unittest.TestCase):
    def test_fixed_benchmark_replays_with_ess(self):
        report = importance_sampling_report(200, 17)
        self.assertGreater(report["importance"]["effective_sample_size"], 0)
        self.assertLessEqual(report["importance"]["effective_sample_size"], 200)
        self.assertTrue(importance_sampling_certificate(200, 17, report))

    def test_certificate_rejects_changed_weight_diagnostic(self):
        report = importance_sampling_report(200, 17)
        altered = copy.deepcopy(report); altered["importance"]["max_normalized_weight"] = 0.0
        self.assertFalse(importance_sampling_certificate(200, 17, altered))

    def test_contract_rejects_invalid_budget_or_seed(self):
        with self.assertRaises(ValueError): importance_sampling_report(1, 0)
        with self.assertRaises(ValueError): importance_sampling_report(20, -1)

    def test_log_weight_diagnostics_avoid_overflow_and_are_shift_invariant(self):
        report = log_weight_diagnostics([1000.0, 999.0, 990.0])
        shifted = log_weight_diagnostics([1500.0, 1499.0, 1490.0])
        self.assertAlmostEqual(sum(report["normalized_weights"]), 1.0)
        self.assertEqual(report["normalized_weights"], shifted["normalized_weights"])
        self.assertTrue(log_weight_diagnostics_certificate([1000.0, 999.0, 990.0], report))
        altered = copy.deepcopy(report); altered["effective_sample_size"] = 3.0
        self.assertFalse(log_weight_diagnostics_certificate([1000.0, 999.0, 990.0], altered))

    def test_log_weight_diagnostics_reject_nonfinite_or_too_short_inputs(self):
        with self.assertRaises(ValueError): log_weight_diagnostics([0.0])
        with self.assertRaises(ValueError): log_weight_diagnostics([0.0, float("inf")])
