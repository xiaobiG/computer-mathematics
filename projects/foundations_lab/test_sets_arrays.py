import copy
import unittest

from projects.foundations_lab.sets_arrays import sets_arrays_certificate, sets_arrays_report


class SetsArraysTests(unittest.TestCase):
    def setUp(self):
        self.left = [1, 2, 3, 4]
        self.right = [3, 4, 5]
        self.matrix = [[1, 2, 3], [4, 5, 6]]

    def test_set_operations_and_zero_based_shape_lookup(self):
        report = sets_arrays_report(self.left, self.right, self.matrix, 1, 1)
        self.assertEqual(report["sets"]["union"], [1, 2, 3, 4, 5])
        self.assertEqual(report["sets"]["intersection"], [3, 4])
        self.assertEqual(report["sets"]["left_minus_right"], [1, 2])
        self.assertEqual(report["array"]["shape"], [2, 3])
        self.assertEqual(report["array"]["index"], [1, 1])
        self.assertEqual(report["array"]["value"], 5)
        self.assertTrue(sets_arrays_certificate(self.left, self.right, self.matrix, 1, 1, report))

    def test_certificate_rejects_changed_union_or_coordinate(self):
        report = sets_arrays_report(self.left, self.right, self.matrix, 1, 1)
        tampered = copy.deepcopy(report)
        tampered["sets"]["union"] = [1, 2]
        self.assertFalse(sets_arrays_certificate(self.left, self.right, self.matrix, 1, 1, tampered))
        tampered = copy.deepcopy(report)
        tampered["array"]["index"] = [0, 0]
        self.assertFalse(sets_arrays_certificate(self.left, self.right, self.matrix, 1, 1, tampered))

    def test_contract_rejects_duplicate_sets_ragged_arrays_and_out_of_bounds_indices(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            sets_arrays_report([1, 1], [], [[1]], 0, 0)
        with self.assertRaisesRegex(ValueError, "shared width"):
            sets_arrays_report([], [], [[1, 2], [3]], 0, 0)
        with self.assertRaisesRegex(ValueError, "inside"):
            sets_arrays_report([], [], [[1]], 1, 0)
