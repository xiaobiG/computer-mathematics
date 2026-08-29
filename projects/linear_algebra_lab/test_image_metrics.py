import unittest
from dataclasses import replace
from math import inf

from projects.linear_algebra_lab.image_metrics import image_quality_certificate, image_quality_report


class ImageMetricsTests(unittest.TestCase):
    def test_exact_reconstruction_has_zero_error_and_infinite_psnr(self):
        pixels = [[0.0, 255.0], [64.0, 128.0]]
        report = image_quality_report(pixels, pixels)
        self.assertEqual(report.samples, 4)
        self.assertEqual(report.mse, 0.0)
        self.assertEqual(report.rmse, 0.0)
        self.assertEqual(report.psnr, inf)
        self.assertEqual(report.max_absolute_error, 0.0)
        self.assertTrue(image_quality_certificate(pixels, pixels, report))

    def test_report_measures_and_certifies_known_error(self):
        reference = [[0.0, 255.0]]
        approximation = [[0.0, 0.0]]
        report = image_quality_report(reference, approximation)
        self.assertAlmostEqual(report.mse, 255.0 ** 2 / 2)
        self.assertAlmostEqual(report.rmse, (255.0 ** 2 / 2) ** 0.5)
        self.assertAlmostEqual(report.psnr, 3.010299956639812)
        self.assertEqual(report.max_absolute_error, 255.0)
        self.assertTrue(image_quality_certificate(reference, approximation, report))
        self.assertFalse(image_quality_certificate(reference, approximation, replace(report, mse=report.mse + 1.0)))

    def test_rejects_bad_shapes_values_and_peak(self):
        with self.assertRaises(ValueError):
            image_quality_report([[0.0]], [[0.0, 1.0]])
        with self.assertRaises(ValueError):
            image_quality_report([[float("nan")]], [[0.0]])
        with self.assertRaises(ValueError):
            image_quality_report([[0.0]], [[0.0]], peak=0)


if __name__ == "__main__":
    unittest.main()
