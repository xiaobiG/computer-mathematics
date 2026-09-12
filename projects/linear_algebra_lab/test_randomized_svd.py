import unittest
from dataclasses import replace

from projects.linear_algebra_lab.randomized_range import randomized_range_report
from projects.linear_algebra_lab.randomized_svd import (
    randomized_svd_certificate,
    randomized_svd_from_range_report,
    randomized_svd_report,
)


class RandomizedSVDTests(unittest.TestCase):
    def test_consumes_the_reader_supplied_range_artifact(self):
        matrix = [[5., 0.], [0., 1.]]
        range_report = randomized_range_report(matrix, rank=1, oversampling=1, seed=3)
        report = randomized_svd_from_range_report(matrix, range_report, rank=1)
        self.assertIs(report.source_range_report, range_report)
        self.assertTrue(randomized_svd_certificate(matrix, report))
        self.assertFalse(randomized_svd_certificate(
            matrix, replace(report, source_range_report=replace(range_report, oversampling=0))
        ))
        with self.assertRaises(ValueError):
            randomized_svd_from_range_report([[5., 0.], [0., 2.]], range_report, rank=1)

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

    def test_same_seed_replays_the_entire_report(self):
        matrix = [[3., 1., 0.], [0., 2., 1.], [1., 0., 2.]]
        first = randomized_svd_report(matrix, rank=1, oversampling=1, seed=29)
        second = randomized_svd_report(matrix, rank=1, oversampling=1, seed=29)
        self.assertEqual(first, second)

    def test_certificate_rejects_approximation_with_missing_or_extra_shape(self):
        matrix = [[3., 1.], [0., 2.], [1., 0.]]
        report = randomized_svd_report(matrix, rank=1, oversampling=1, seed=29)
        self.assertFalse(randomized_svd_certificate(
            matrix, replace(report, approximation=report.approximation[:-1])
        ))
        self.assertFalse(randomized_svd_certificate(
            matrix, replace(report, approximation=(report.approximation[0][:-1],) + report.approximation[1:])
        ))
