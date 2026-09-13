import unittest
from dataclasses import replace
from math import sqrt

from projects.linear_algebra_lab.pca import (
    pca_2d_centering_comparison_certificate,
    pca_2d_centering_comparison_report,
    pca_2d_report,
    pca_2d_report_certificate,
)


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
        with self.assertRaises(ValueError):
            pca_2d_report(((1.0, 2.0), (3.0, 4.0)))
        with self.assertRaises(ValueError):
            pca_2d_report([[True, 0.0], [1.0, 2.0]])
        with self.assertRaises(ValueError):
            pca_2d_report(None)  # type: ignore[arg-type]

    def test_centering_comparison_separates_mean_offset_from_variation(self):
        rows = [[100.0, -1.0], [100.0, 0.0], [100.0, 1.0]]
        report = pca_2d_centering_comparison_report(rows)
        self.assertGreater(abs(report["centered_component"][1]), .999)
        self.assertGreater(abs(report["uncentered_component"][0]), .999)
        self.assertTrue(report["uncentered_is_more_aligned_to_mean"])
        self.assertTrue(report["components_are_different_directions"])
        self.assertTrue(pca_2d_centering_comparison_certificate(rows, report))
        altered = dict(report)
        altered["uncentered_is_more_aligned_to_mean"] = False
        self.assertFalse(pca_2d_centering_comparison_certificate(rows, altered))

    def test_centering_comparison_requires_a_mean_direction(self):
        with self.assertRaises(ValueError):
            pca_2d_centering_comparison_report([[-1.0, 0.0], [1.0, 0.0]])


if __name__ == "__main__":
    unittest.main()
