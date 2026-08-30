import unittest

from projects.naive_bayes_spam.drift_monitoring import (
    categorical_drift_certificate,
    categorical_drift_report,
)


class DriftMonitoringTests(unittest.TestCase):
    def test_identical_distributions_have_zero_distance_and_no_review(self):
        reference = ["ham"] * 50 + ["prize"] * 50
        report = categorical_drift_report(reference, list(reversed(reference)), psi_threshold=0.01)
        self.assertAlmostEqual(report["psi"], 0.0, places=12)
        self.assertAlmostEqual(report["total_variation"], 0.0, places=12)
        self.assertFalse(report["needs_review"])
        self.assertTrue(categorical_drift_certificate(reference, list(reversed(reference)), report))

    def test_shift_and_new_category_are_reported_not_silenced(self):
        reference = ["ham"] * 50 + ["prize"] * 50
        current = ["ham"] * 80 + ["prize"] * 10 + ["invoice"] * 10
        report = categorical_drift_report(reference, current, psi_threshold=0.1)
        self.assertGreater(report["psi"], 0.1)
        self.assertGreater(report["total_variation"], 0.0)
        self.assertTrue(report["needs_review"])
        rows = {row["category"]: row for row in report["categories"]}
        self.assertEqual(rows["invoice"]["reference_count"], 0)
        self.assertEqual(rows["invoice"]["current_count"], 10)
        self.assertAlmostEqual(sum(row["reference_share"] for row in report["categories"]), 1.0)
        self.assertAlmostEqual(sum(row["current_share"] for row in report["categories"]), 1.0)

    def test_certificate_rejects_tampered_conclusion_and_bad_contracts(self):
        reference = ["ham", "prize"]
        current = ["ham", "ham"]
        report = categorical_drift_report(reference, current)
        report["needs_review"] = not report["needs_review"]
        self.assertFalse(categorical_drift_certificate(reference, current, report))
        with self.assertRaises(ValueError):
            categorical_drift_report([], current)
        with self.assertRaises(ValueError):
            categorical_drift_report(reference, current, smoothing=0)
        with self.assertRaises(ValueError):
            categorical_drift_report(reference, current, psi_threshold=float("inf"))
