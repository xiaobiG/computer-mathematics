import math
import unittest
from dataclasses import replace
from fractions import Fraction

from projects.floating_point_museum.representation import (
    adjacent_values,
    decimal_rounding_certificate,
    decimal_rounding_report,
    float64_parts,
    spacing_at,
)


class RepresentationTests(unittest.TestCase):
    def test_binary64_fields_distinguish_normal_zero_subnormal_and_special_values(self):
        self.assertEqual(float64_parts(0.1).classification, "normal")
        self.assertEqual(float64_parts(0.0).classification, "zero")
        self.assertEqual(float64_parts(-0.0).sign, 1)
        self.assertEqual(float64_parts(math.nextafter(0.0, 1.0)).classification, "subnormal")
        self.assertEqual(float64_parts(float("inf")).classification, "infinity")
        self.assertEqual(float64_parts(float("nan")).classification, "nan")

    def test_adjacent_values_and_ulp_show_scale_dependent_spacing(self):
        lower, upper = adjacent_values(1.0)
        self.assertLess(lower, 1.0)
        self.assertGreater(upper, 1.0)
        self.assertEqual(upper - 1.0, 2.0 ** -52)
        self.assertEqual(spacing_at(1e16), 2.0)
        self.assertEqual(1e16 + 1.0, 1e16)

    def test_decimal_rounding_report_keeps_source_and_stored_values_separate(self):
        report = decimal_rounding_report("0.1")
        self.assertEqual(report.exact_value, Fraction(1, 10))
        self.assertGreater(report.rounding_error, 0)
        self.assertEqual(report.rounding_direction, "up")
        self.assertTrue(report.certificate["rounding_error_is_within_half_ulp"])
        self.assertTrue(report.certificate["valid"])
        self.assertTrue(decimal_rounding_certificate(report)["valid"])

        exact = decimal_rounding_report("0.5")
        self.assertEqual(exact.rounding_direction, "exact")
        self.assertEqual(exact.rounding_error, 0)

    def test_decimal_rounding_certificate_rejects_tampered_fields(self):
        report = decimal_rounding_report("0.1")
        tampered = replace(report, rounding_error=Fraction(0, 1), rounding_direction="exact")
        certificate = decimal_rounding_certificate(tampered)
        self.assertFalse(certificate["fields_match_recomputed_literal"])
        self.assertFalse(certificate["valid"])

    def test_decimal_rounding_report_rejects_nonfinite_or_unknown_source_values(self):
        for literal in ("nan", "inf", "1e400"):
            with self.assertRaises(ValueError):
                decimal_rounding_report(literal)
        with self.assertRaises(TypeError):
            decimal_rounding_report(0.1)  # type: ignore[arg-type]

    def test_nonfinite_neighbour_and_spacing_requests_are_rejected(self):
        with self.assertRaises(ValueError):
            adjacent_values(float("inf"))
        with self.assertRaises(ValueError):
            spacing_at(float("nan"))
