import unittest
from dataclasses import replace
from math import inf

from projects.linear_algebra_lab.image_metrics import (
    image_quality_certificate, image_quality_report, randomized_svd_image_quality_review,
    randomized_svd_image_quality_review_certificate, same_mse_structural_comparison_certificate,
    same_mse_structural_comparison_report, structural_similarity_certificate, structural_similarity_report,
    local_structural_similarity_certificate, local_structural_similarity_report,
    linear_rgb_error_certificate, linear_rgb_error_report,
    srgb_cielab_delta_e76_comparison, srgb_cielab_delta_e76_comparison_certificate,
    srgb_linear_luminance_comparison, srgb_linear_luminance_comparison_certificate, srgb_to_linear,
)
from projects.linear_algebra_lab.randomized_svd import randomized_svd_report


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

    def test_global_ssim_is_one_for_identical_matrix_and_certifies(self):
        pixels = [[0.0, 30.0], [120.0, 255.0]]
        report = structural_similarity_report(pixels, pixels)
        self.assertAlmostEqual(report.ssim, 1.0)
        self.assertTrue(structural_similarity_certificate(pixels, pixels, report))

    def test_global_ssim_detects_structure_change_and_tampering(self):
        reference = [[0.0, 255.0], [0.0, 255.0]]
        shifted = [[255.0, 0.0], [255.0, 0.0]]
        report = structural_similarity_report(reference, shifted)
        self.assertLess(report.ssim, 0.0)
        self.assertFalse(structural_similarity_certificate(reference, shifted, replace(report, covariance=0.0)))

    def test_same_mse_can_have_different_global_structure_scores(self):
        reference = [[128.0] * 4 for _ in range(4)]
        brightness_shift = [[138.0] * 4 for _ in range(4)]
        alternating_noise = [[118.0 if (row + column) % 2 == 0 else 138.0 for column in range(4)] for row in range(4)]
        report = same_mse_structural_comparison_report(reference, brightness_shift, alternating_noise)
        self.assertEqual(report.first_quality.mse, 100.0)
        self.assertEqual(report.second_quality.mse, 100.0)
        self.assertEqual(report.higher_ssim, "first")
        self.assertGreater(report.first_structure.ssim, report.second_structure.ssim)
        self.assertEqual(report.automatic_action, "none")
        self.assertTrue(same_mse_structural_comparison_certificate(reference, brightness_shift, alternating_noise, report))
        self.assertFalse(same_mse_structural_comparison_certificate(
            reference, brightness_shift, alternating_noise, replace(report, higher_ssim="second"),
        ))
        with self.assertRaisesRegex(ValueError, "matching MSE"):
            same_mse_structural_comparison_report(reference, brightness_shift, reference)

    def test_local_tiles_locate_a_defect_hidden_by_a_better_global_score(self):
        reference = [[128.0] * 4 for _ in range(4)]
        approximation = [[128.0] * 4 for _ in range(4)]
        for row in range(2):
            for column in range(2):
                approximation[row][column] = 0.0
        report = local_structural_similarity_report(reference, approximation, 2, 2)
        self.assertEqual((report.worst_window_row, report.worst_window_column), (0, 0))
        self.assertLess(report.worst_window_ssim, report.global_ssim)
        self.assertEqual(len(report.windows), 4)
        self.assertTrue(local_structural_similarity_certificate(reference, approximation, 2, 2, report))
        self.assertFalse(local_structural_similarity_certificate(
            reference, approximation, 2, 2, replace(report, worst_window_row=2),
        ))
        with self.assertRaisesRegex(ValueError, "divide"):
            local_structural_similarity_report(reference, approximation, 3, 2)

    def test_equal_rgb_mse_can_have_different_linear_luminance_error(self):
        reference = [[[0.0, 0.0, 0.0]]]
        red_error = [[[10.0, 0.0, 0.0]]]
        green_error = [[[0.0, 10.0, 0.0]]]
        red = linear_rgb_error_report(reference, red_error)
        green = linear_rgb_error_report(reference, green_error)
        self.assertAlmostEqual(red.rgb_mse, green.rgb_mse)
        self.assertLess(red.linear_luminance_mse, green.linear_luminance_mse)
        self.assertTrue(linear_rgb_error_certificate(reference, red_error, red))
        self.assertFalse(linear_rgb_error_certificate(reference, red_error, replace(red, rgb_mse=0.0)))
        with self.assertRaisesRegex(ValueError, "three finite"):
            linear_rgb_error_report(reference, [[[0.0, 0.0]]])

    def test_srgb_decoding_changes_the_declared_luminance_budget_conclusion(self):
        reference = [[[0.0, 0.0, 0.0]]]
        approximation = [[[0.5, 0.0, 0.0]]]
        report = srgb_linear_luminance_comparison(reference, approximation, luminance_mse_budget=0.005)
        self.assertEqual(report.contract, "srgb-linear-luminance-comparison/v1")
        self.assertAlmostEqual(srgb_to_linear(0.04045), 0.04045 / 12.92)
        self.assertGreater(report.encoded_as_linear_luminance_mse, report.luminance_mse_budget)
        self.assertLess(report.decoded_linear_luminance_mse, report.luminance_mse_budget)
        self.assertEqual(report.encoded_budget_status, "exceeds_luminance_mse_budget")
        self.assertEqual(report.decoded_budget_status, "within_luminance_mse_budget")
        self.assertEqual(report.automatic_action, "none")
        self.assertTrue(srgb_linear_luminance_comparison_certificate(reference, approximation, report))
        self.assertFalse(srgb_linear_luminance_comparison_certificate(
            reference, approximation, replace(report, decoded_budget_status="exceeds_luminance_mse_budget"),
        ))
        with self.assertRaisesRegex(ValueError, r"\[0, 1\]"):
            srgb_linear_luminance_comparison(reference, [[[1.1, 0.0, 0.0]]], 0.005)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            srgb_linear_luminance_comparison(reference, approximation, -1.0)

    def test_srgb_cielab_delta_e76_binds_encoding_white_and_budget(self):
        black = [[[0.0, 0.0, 0.0]]]
        encoded_red = [[[0.5, 0.0, 0.0]]]
        report = srgb_cielab_delta_e76_comparison(black, encoded_red, delta_e76_budget=40.0)
        self.assertEqual(report.contract, "srgb-cielab-delta-e76-comparison/v1")
        self.assertEqual(report.reference_white_xyz, (0.95047, 1.0, 1.08883))
        self.assertEqual(report.samples, 1)
        self.assertAlmostEqual(report.rgb_mse, 1.0 / 12.0)
        self.assertGreater(report.mean_delta_e76, 40.0)
        self.assertEqual(report.budget_status, "exceeds_delta_e76_budget")
        self.assertEqual(report.automatic_action, "none")
        self.assertTrue(srgb_cielab_delta_e76_comparison_certificate(black, encoded_red, report))
        self.assertFalse(srgb_cielab_delta_e76_comparison_certificate(
            black, encoded_red, replace(report, reference_white_xyz=(1.0, 1.0, 1.0)),
        ))
        with self.assertRaisesRegex(ValueError, "non-negative"):
            srgb_cielab_delta_e76_comparison(black, encoded_red, -1.0)

    def test_randomized_svd_artifact_drives_a_numeric_quality_budget_review(self):
        pixels = [[5.0, 0.0], [0.0, 1.0]]
        svd_report = randomized_svd_report(pixels, rank=1, oversampling=1, seed=3)
        accepted = randomized_svd_image_quality_review(pixels, svd_report, mse_budget=0.3, peak=5.0)
        rejected = randomized_svd_image_quality_review(pixels, svd_report, mse_budget=0.2, peak=5.0)
        self.assertEqual(accepted.source_seed, 3)
        self.assertEqual(accepted.mse_budget_status, "within_mse_budget")
        self.assertEqual(rejected.mse_budget_status, "exceeds_mse_budget")
        self.assertEqual(accepted.automatic_action, "none")
        self.assertTrue(randomized_svd_image_quality_review_certificate(pixels, svd_report, 0.3, accepted, peak=5.0))
        self.assertFalse(randomized_svd_image_quality_review_certificate(
            pixels, svd_report, 0.3, replace(accepted, mse_budget_status="exceeds_mse_budget"), peak=5.0
        ))
        with self.assertRaises(ValueError):
            randomized_svd_image_quality_review([[5.0, 0.0], [0.0, 2.0]], svd_report, mse_budget=0.3, peak=5.0)


if __name__ == "__main__":
    unittest.main()
