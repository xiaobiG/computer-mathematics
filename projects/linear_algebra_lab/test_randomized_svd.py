import unittest
from dataclasses import replace

from projects.linear_algebra_lab.randomized_svd import randomized_svd_certificate, randomized_svd_report


class RandomizedSVDTests(unittest.TestCase):
    def test_rank_one_matrix_is_recovered_and_replayed(self):
        matrix = [[1., 2.], [2., 4.], [3., 6.]]
        report = randomized_svd_report(matrix, rank=1, oversampling=1, seed=17)
        self.assertEqual(len(report.singular_values), 1)
        self.assertLess(report.frobenius_error, 1e-10)
        self.assertTrue(randomized_svd_certificate(matrix, report))
        self.assertFalse(randomized_svd_certificate(matrix, replace(report, frobenius_error=1.)))

    def test_rank_truncation_has_a_visible_residual(self):
        report = randomized_svd_report([[5., 0.], [0., 1.]], rank=1, oversampling=1, seed=3)
        self.assertGreater(report.frobenius_error, 0.)
        self.assertTrue(randomized_svd_certificate([[5., 0.], [0., 1.]], report))
