import unittest

from projects.floating_point_museum.comparison import (
    close_enough,
    comparison_certificate,
    comparison_report,
)


class ComparisonContractTests(unittest.TestCase):
    def test_combines_absolute_and_relative_tolerances(self):
        self.assertTrue(close_enough(0.1 + 0.2, 0.3))
        self.assertTrue(close_enough(1_000_000_000.5, 1_000_000_000.0, rel_tol=1e-9))
        self.assertFalse(close_enough(1.0, 1.1))

    def test_special_values_and_invalid_contracts_are_explicit(self):
        self.assertFalse(close_enough(float("nan"), float("nan")))
        self.assertTrue(close_enough(float("inf"), float("inf")))
        self.assertFalse(close_enough(float("inf"), float("-inf")))
        with self.assertRaises(ValueError):
            close_enough(1.0, 1.0, abs_tol=-1.0)

    def test_report_certificate_rejects_a_tampered_threshold_or_decision(self):
        report = comparison_report(1e12, 1e12 + 1.0, abs_tol=1e-6, rel_tol=1e-9)
        self.assertTrue(report["close"])
        self.assertTrue(report["certificate"]["valid"])

        tampered = dict(report)
        tampered["threshold"] = 0.0
        self.assertFalse(comparison_certificate(tampered)["valid"])
        tampered = dict(report)
        tampered["close"] = False
        self.assertFalse(comparison_certificate(tampered)["valid"])


if __name__ == "__main__":
    unittest.main()
