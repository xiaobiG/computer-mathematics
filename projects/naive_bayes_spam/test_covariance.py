import unittest

from projects.naive_bayes_spam.covariance import (
    covariance_report,
    sample_correlation,
    sample_covariance,
)


class CovarianceTests(unittest.TestCase):
    def test_covariance_report_certifies_centering_symmetry_and_variances(self):
        report = covariance_report([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]])
        self.assertEqual(report["means"], [2.0, 4.0])
        self.assertEqual(report["covariance"], [[1.0, 2.0], [2.0, 4.0]])
        self.assertTrue(report["certificate"]["valid"])
        self.assertAlmostEqual(sample_correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]), 1.0)

    def test_quadratic_dependence_can_have_zero_covariance(self):
        xs = [-2.0, -1.0, 0.0, 1.0, 2.0]
        ys = [value * value for value in xs]
        self.assertAlmostEqual(sample_covariance(xs, ys), 0.0)
        self.assertAlmostEqual(sample_correlation(xs, ys), 0.0)
        self.assertEqual(ys, [4.0, 1.0, 0.0, 1.0, 4.0])

    def test_rejects_constant_mismatched_and_nonfinite_inputs(self):
        with self.assertRaises(ValueError):
            sample_correlation([1.0, 1.0], [2.0, 3.0])
        with self.assertRaises(ValueError):
            sample_covariance([1.0, 2.0], [1.0])
        with self.assertRaises(ValueError):
            covariance_report([[1.0, float("nan")], [2.0, 3.0]])


if __name__ == "__main__":
    unittest.main()
