import copy
import unittest

from projects.foundations_lab.tensor_shapes import (
    batch_linear_report,
    elementwise_add_report,
    square_batch_transpose_counterexample_report,
    tensor_shape,
    tensor_shapes_certificate,
)


class TensorShapeTests(unittest.TestCase):
    def test_scalar_vector_and_matrix_shapes_are_distinct(self):
        self.assertEqual(tensor_shape(2.5), [])
        self.assertEqual(tensor_shape([2, 5, 7]), [3])
        self.assertEqual(tensor_shape([[2], [5], [7]]), [3, 1])
        self.assertEqual(tensor_shape([[1, 2, 3], [4, 5, 6]]), [2, 3])

    def test_elementwise_addition_preserves_vector_shape_and_certificate(self):
        report = elementwise_add_report([2, 5, 7], [1, 1, 1])
        self.assertEqual(report["output"], {"values": [3, 6, 8], "shape": [3]})
        self.assertTrue(tensor_shapes_certificate("elementwise_add", {"left": [2, 5, 7], "right": [1, 1, 1]}, report))
        altered = copy.deepcopy(report)
        altered["output"]["shape"] = [3, 1]
        self.assertFalse(tensor_shapes_certificate("elementwise_add", {"left": [2, 5, 7], "right": [1, 1, 1]}, altered))

    def test_batch_linear_shape_and_values(self):
        report = batch_linear_report([[1, 2, 3], [4, 5, 6]], [[1, 0], [0, 1], [1, 1]], [10, 20])
        self.assertEqual(report["batch"]["shape"], [2, 3])
        self.assertEqual(report["weights"]["shape"], [3, 2])
        self.assertEqual(report["output"], {"values": [[14, 25], [20, 31]], "shape": [2, 2]})
        self.assertTrue(tensor_shapes_certificate("batch_linear", {"batch": [[1, 2, 3], [4, 5, 6]], "weights": [[1, 0], [0, 1], [1, 1]], "bias": [10, 20]}, report))

    def test_rejects_ragged_values_and_incompatible_contracts(self):
        with self.assertRaisesRegex(ValueError, "rectangular"):
            tensor_shape([[1, 2], [3]])
        with self.assertRaisesRegex(ValueError, "identical"):
            elementwise_add_report([1, 2], [3])
        with self.assertRaisesRegex(ValueError, "feature width"):
            batch_linear_report([[1, 2]], [[1], [2], [3]], [0])
        with self.assertRaisesRegex(ValueError, "bias width"):
            batch_linear_report([[1, 2]], [[1], [2]], [0, 0])

    def test_square_transpose_can_preserve_shape_while_swapping_axis_roles(self):
        inputs = {
            "batch": [[1, 2], [3, 4]],
            "weights": [[1, 0], [0, 1]],
            "bias": [0, 0],
            "sample_labels": ["alice", "bob"],
        }
        report = square_batch_transpose_counterexample_report(**inputs)
        self.assertEqual(report["normal"]["output"], {"values": [[1, 2], [3, 4]], "shape": [2, 2]})
        self.assertEqual(report["transposed"]["output"], {"values": [[1, 3], [2, 4]], "shape": [2, 2]})
        self.assertEqual(report["normal"]["row_labels"], ["alice", "bob"])
        self.assertEqual(report["transposed"]["row_labels"], ["feature_0", "feature_1"])
        self.assertTrue(report["same_numeric_shape"])
        self.assertTrue(report["axis_semantics_changed"])
        self.assertTrue(tensor_shapes_certificate("square_batch_transpose_counterexample", inputs, report))
        altered = copy.deepcopy(report)
        altered["transposed_axis_roles"] = ["sample", "feature"]
        self.assertFalse(tensor_shapes_certificate("square_batch_transpose_counterexample", inputs, altered))

    def test_transpose_counterexample_requires_square_batch_and_valid_labels(self):
        with self.assertRaisesRegex(ValueError, "square"):
            square_batch_transpose_counterexample_report(
                [[1, 2, 3], [4, 5, 6]], [[1], [1], [1]], [0], ["alice", "bob"]
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            square_batch_transpose_counterexample_report(
                [[1, 2], [3, 4]], [[1, 0], [0, 1]], [0, 0], ["same", "same"]
            )
