import unittest

from projects.linear_algebra_lab.basis import (
    basis_coordinate_certificate,
    basis_coordinate_report,
    column_independence_certificate,
    column_independence_report,
    fundamental_subspaces_certificate,
    fundamental_subspaces_report,
)


class BasisTests(unittest.TestCase):
    def test_column_report_exposes_a_redundant_direction(self):
        report = column_independence_report([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        self.assertEqual(report["rank"], 2)
        self.assertEqual(report["basis_indices"], [0, 1])
        self.assertFalse(report["is_linearly_independent"])
        self.assertFalse(report["is_basis_for_ambient_space"])
        self.assertLess(report["residual_norms"][2], 1e-12)
        self.assertTrue(column_independence_certificate(
            [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], report,
        )["valid"])

        tampered = dict(report)
        tampered["basis_indices"] = [0, 2]
        self.assertFalse(column_independence_certificate(
            [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], tampered,
        )["valid"])

    def test_nonstandard_basis_recovers_unique_coordinates_and_reconstruction(self):
        report = basis_coordinate_report([[1.0, 1.0], [1.0, -1.0]], [4.0, 2.0])
        self.assertTrue(report["is_basis_for_ambient_space"])
        self.assertEqual(report["coordinates"], [3.0, 1.0])
        self.assertEqual(report["reconstruction"], [4.0, 2.0])
        self.assertTrue(report["reconstructs_target"])
        self.assertTrue(basis_coordinate_certificate(
            [[1.0, 1.0], [1.0, -1.0]], [4.0, 2.0], report,
        )["valid"])

        tampered = dict(report)
        tampered["coordinates"] = [2.0, 2.0]
        self.assertFalse(basis_coordinate_certificate(
            [[1.0, 1.0], [1.0, -1.0]], [4.0, 2.0], tampered,
        )["valid"])

    def test_coordinate_recovery_rejects_dependent_and_nonfinite_inputs(self):
        with self.assertRaises(ValueError):
            basis_coordinate_report([[1.0, 0.0], [2.0, 0.0]], [1.0, 0.0])
        with self.assertRaises(ValueError):
            column_independence_report([[1.0, float("nan")]])

    def test_four_subspaces_connect_rank_nullity_and_orthogonal_complements(self):
        matrix = [[1.0, 1.0], [2.0, 2.0]]
        report = fundamental_subspaces_report(matrix)
        self.assertEqual(report["pivot_columns"], [0])
        self.assertEqual(report["column_space_basis"], [[1.0, 2.0]])
        self.assertEqual(report["dimensions"], {
            "rank": 1, "column_space": 1, "row_space": 1,
            "null_space": 1, "left_null_space": 1,
        })
        self.assertEqual(report["null_space_basis"], [[-1.0, 1.0]])
        self.assertEqual(report["left_null_space_basis"], [[-2.0, 1.0]])
        self.assertTrue(all(report["certificate"].values()))
        self.assertTrue(fundamental_subspaces_certificate(matrix, report))

    def test_rectangular_left_null_space_and_tampering_are_visible(self):
        matrix = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
        report = fundamental_subspaces_report(matrix)
        self.assertEqual(report["dimensions"]["rank"], 2)
        self.assertEqual(report["dimensions"]["null_space"], 0)
        self.assertEqual(report["dimensions"]["left_null_space"], 1)
        altered = dict(report)
        altered["dimensions"] = dict(report["dimensions"])
        altered["dimensions"]["rank"] = 1
        self.assertFalse(fundamental_subspaces_certificate(matrix, altered))
        with self.assertRaises(ValueError):
            fundamental_subspaces_report([[1.0, float("nan")]])


if __name__ == "__main__":
    unittest.main()
