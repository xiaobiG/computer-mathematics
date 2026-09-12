import copy
import unittest

from projects.floating_point_museum.importance_sampling import importance_sampling_certificate, importance_sampling_report


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
