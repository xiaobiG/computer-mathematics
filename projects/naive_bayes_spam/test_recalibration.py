import unittest

from projects.naive_bayes_spam.recalibration import PlattCalibrator, brier_score, log_loss


class RecalibrationTests(unittest.TestCase):
    def setUp(self):
        # Deliberately over-confident validation forecasts: 0.9 is correct
        # three quarters of the time and 0.1 is correct one quarter of the time.
        self.validation_scores = [0.9] * 8 + [0.1] * 8
        self.validation_labels = [True, True, True, True, True, True, False, False] + [True, True, False, False, False, False, False, False]

    def test_platt_scaling_improves_validation_probability_losses(self):
        calibrator = PlattCalibrator(learning_rate=0.2, max_steps=1000).fit(
            self.validation_scores, self.validation_labels
        )
        calibrated = calibrator.predict_proba(self.validation_scores)
        self.assertLess(log_loss(calibrated, self.validation_labels), log_loss(self.validation_scores, self.validation_labels))
        self.assertLess(brier_score(calibrated, self.validation_labels), brier_score(self.validation_scores, self.validation_labels))
        self.assertTrue(all(next_value <= value + 1e-12 for value, next_value in zip(calibrator.objective_trace, calibrator.objective_trace[1:])))

    def test_output_is_bounded_and_preserves_order_for_positive_slope(self):
        calibrator = PlattCalibrator().fit(self.validation_scores, self.validation_labels)
        transformed = calibrator.predict_proba([0.0, 0.1, 0.5, 0.9, 1.0])
        self.assertTrue(all(0.0 <= value <= 1.0 for value in transformed))
        self.assertGreater(calibrator.slope, 0.0)
        self.assertEqual(transformed, sorted(transformed))

    def test_input_contract_and_test_leakage_boundary_are_explicit(self):
        calibrator = PlattCalibrator()
        with self.assertRaises(ValueError):
            calibrator.predict_proba([0.5])
        with self.assertRaises(ValueError):
            calibrator.fit([0.5, 0.7], [True, True])
        with self.assertRaises(ValueError):
            calibrator.fit([0.5], [True, False])
        with self.assertRaises(ValueError):
            brier_score([1.2], [True])
        with self.assertRaises(ValueError):
            log_loss([0.5], [2])
