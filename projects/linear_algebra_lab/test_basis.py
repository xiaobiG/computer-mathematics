import unittest

from projects.linear_algebra_lab.basis import basis_coordinate_report, column_independence_report


class BasisTests(unittest.TestCase):
    def test_column_report_exposes_a_redundant_direction(self):
        report = column_independence_report([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        self.assertEqual(report["rank"], 2)
        self.assertEqual(report["basis_indices"], [0, 1])
        self.assertFalse(report["is_linearly_independent"])
        self.assertFalse(report["is_basis_for_ambient_space"])
        self.assertLess(report["residual_norms"][2], 1e-12)

    def test_nonstandard_basis_recovers_unique_coordinates_and_reconstruction(self):
        report = basis_coordinate_report([[1.0, 1.0], [1.0, -1.0]], [4.0, 2.0])
        self.assertTrue(report["is_basis_for_ambient_space"])
        self.assertEqual(report["coordinates"], [3.0, 1.0])
        self.assertEqual(report["reconstruction"], [4.0, 2.0])
        self.assertTrue(report["reconstructs_target"])

    def test_coordinate_recovery_rejects_dependent_and_nonfinite_inputs(self):
        with self.assertRaises(ValueError):
            basis_coordinate_report([[1.0, 0.0], [2.0, 0.0]], [1.0, 0.0])
        with self.assertRaises(ValueError):
            column_independence_report([[1.0, float("nan")]])


if __name__ == "__main__":
    unittest.main()
