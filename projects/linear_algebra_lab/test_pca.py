import unittest
from dataclasses import replace
from math import sqrt

from projects.linear_algebra_lab.pca import pca_2d_report, pca_2d_report_certificate


class Pca2DTests(unittest.TestCase):
    def test_rank_one_diagonal_cloud_has_one_exact_component(self):
        report = pca_2d_report([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        self.assertEqual(report.mean, (1.0, 1.0))
        self.assertAlmostEqual(abs(report.component[0]), 1 / sqrt(2), places=9)
        self.assertAlmostEqual(abs(report.component[1]), 1 / sqrt(2), places=9)
        self.assertAlmostEqual(report.explained_variance_ratio, 1.0, places=10)
        self.assertLess(report.reconstruction_error_squared, 1e-18)
        self.assertTrue(report.certificate["valid"])

    def test_pca_certifies_projection_orthogonality_and_discarded_variance(self):
        report = pca_2d_report([[0.0, 0.0], [1.0, 2.0], [2.0, 1.0], [3.0, 3.0]])
        self.assertGreater(report.explained_variance_ratio, 0.5)
        self.assertLess(report.explained_variance_ratio, 1.0)
        self.assertTrue(report.certificate["residuals_are_orthogonal_to_component"])
        self.assertTrue(report.certificate["reconstruction_error_matches_discarded_variance"])

    def test_pca_report_replayer_rejects_tampered_measurements_and_flags(self):
        rows = [[0.0, 0.0], [1.0, 2.0], [2.0, 1.0], [3.0, 3.0]]
        report = pca_2d_report(rows)
        self.assertTrue(pca_2d_report_certificate(rows, report))
        self.assertFalse(pca_2d_report_certificate(
            rows, replace(report, reconstruction_error_squared=report.reconstruction_error_squared + 1.0)
        ))
        altered_certificate = dict(report.certificate)
        altered_certificate["valid"] = False
        self.assertFalse(pca_2d_report_certificate(
            rows, replace(report, certificate=altered_certificate)
        ))

    def test_pca_rejects_zero_variance_wrong_shapes_and_nonfinite_samples(self):
        with self.assertRaises(ValueError):
            pca_2d_report([[1.0, 1.0], [1.0, 1.0]])
        with self.assertRaises(ValueError):
            pca_2d_report([[1.0], [2.0]])
        with self.assertRaises(ValueError):
            pca_2d_report([[1.0, float("nan")], [2.0, 3.0]])


if __name__ == "__main__":
    unittest.main()
