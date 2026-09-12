import unittest
from dataclasses import replace

from projects.linear_algebra_lab.randomized_range import randomized_range_certificate, randomized_range_report


class RandomizedRangeTests(unittest.TestCase):
    def test_exactly_recovers_a_rank_one_column_space_and_replays(self):
        matrix = [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]]
        report = randomized_range_report(matrix, rank=1, oversampling=1, seed=17)
        self.assertEqual(report.sample_columns, 2)
        self.assertEqual(report.basis_columns, 1)
        self.assertLess(report.frobenius_error, 1e-10)
        self.assertTrue(randomized_range_certificate(matrix, report, oversampling=1))
        self.assertFalse(randomized_range_certificate(matrix, replace(report, frobenius_error=1.0), oversampling=1))
        altered_basis = ((report.basis[0][0] + 1.0, *report.basis[0][1:]),)
        self.assertFalse(randomized_range_certificate(matrix, replace(report, basis=altered_basis), oversampling=1))

    def test_power_iteration_and_contract_boundaries(self):
        matrix = [[5.0, 0.0], [0.0, 1.0]]
        plain = randomized_range_report(matrix, rank=1, oversampling=0, power_iterations=0, seed=3)
        powered = randomized_range_report(matrix, rank=1, oversampling=0, power_iterations=3, seed=3)
        self.assertLessEqual(powered.frobenius_error, plain.frobenius_error)
        self.assertTrue(randomized_range_certificate(matrix, powered, oversampling=0))
        with self.assertRaises(ValueError):
            randomized_range_report([[0.0]], rank=0)
        with self.assertRaises(ValueError):
            randomized_range_report([[float("nan")]], rank=1)
        with self.assertRaises(ValueError):
            randomized_range_report([[0.0]], rank=1, seed=True)


if __name__ == "__main__":
    unittest.main()
