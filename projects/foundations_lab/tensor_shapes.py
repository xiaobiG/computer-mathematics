"""Small, explicit tensor-shape contracts for prerequisite lessons."""

from __future__ import annotations

from math import isfinite


TENSOR_SHAPES_CONTRACT_VERSION = "tensor-shapes/v1"


def _number(value: object, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must contain finite numbers")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} must contain finite numbers")
    return value


def _vector(value: object, name: str) -> list[int | float]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty vector list")
    return [_number(item, name) for item in value]


def _matrix(value: object, name: str) -> list[list[int | float]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty matrix list")
    rows = [_vector(row, name) for row in value]
    if any(len(row) != len(rows[0]) for row in rows):
        raise ValueError(f"{name} must be rectangular")
    return rows


def tensor_shape(value: object) -> list[int]:
    """Return scalar [], vector [n], or rectangular matrix [rows, columns]."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        _number(value, "scalar")
        return []
    if isinstance(value, list) and value and all(not isinstance(item, list) for item in value):
        return [len(_vector(value, "vector"))]
    rows = _matrix(value, "matrix")
    return [len(rows), len(rows[0])]


def _matrix_shape(value: object, name: str) -> tuple[list[list[int | float]], list[int]]:
    rows = _matrix(value, name)
    return rows, [len(rows), len(rows[0])]


def _sample_labels(value: object, expected_count: int) -> list[str]:
    if not isinstance(value, list) or len(value) != expected_count:
        raise ValueError("sample_labels must have one non-empty label per batch row")
    if any(not isinstance(label, str) or not label for label in value):
        raise ValueError("sample_labels must contain non-empty strings")
    if len(set(value)) != len(value):
        raise ValueError("sample_labels must be unique")
    return value


def elementwise_add_report(left: object, right: object) -> dict[str, object]:
    """Add equal-length vectors and bind the preserved one-dimensional shape."""
    left_values, right_values = _vector(left, "left"), _vector(right, "right")
    if len(left_values) != len(right_values):
        raise ValueError("elementwise addition requires identical vector shapes")
    return {
        "contract_version": TENSOR_SHAPES_CONTRACT_VERSION,
        "operation": "elementwise_add",
        "left": {"values": left_values, "shape": [len(left_values)]},
        "right": {"values": right_values, "shape": [len(right_values)]},
        "output": {"values": [a + b for a, b in zip(left_values, right_values)], "shape": [len(left_values)]},
    }


def batch_linear_report(batch: object, weights: object, bias: object) -> dict[str, object]:
    """Run XW + b under the explicit row-batch convention X:[batch, features]."""
    batch_rows, batch_shape = _matrix_shape(batch, "batch")
    weight_rows, weight_shape = _matrix_shape(weights, "weights")
    bias_values = _vector(bias, "bias")
    if batch_shape[1] != weight_shape[0]:
        raise ValueError("batch feature width must equal weight input width")
    if len(bias_values) != weight_shape[1]:
        raise ValueError("bias width must equal weight output width")
    output = [
        [sum(row[feature] * weight_rows[feature][output_index] for feature in range(weight_shape[0])) + bias_values[output_index]
         for output_index in range(weight_shape[1])]
        for row in batch_rows
    ]
    return {
        "contract_version": TENSOR_SHAPES_CONTRACT_VERSION,
        "operation": "batch_linear",
        "convention": "rows are samples; X has shape [batch, features] and W has shape [features, outputs]",
        "batch": {"values": batch_rows, "shape": batch_shape},
        "weights": {"values": weight_rows, "shape": weight_shape},
        "bias": {"values": bias_values, "shape": [len(bias_values)]},
        "output": {"values": output, "shape": [batch_shape[0], weight_shape[1]]},
    }


def square_batch_transpose_counterexample_report(
    batch: object, weights: object, bias: object, sample_labels: object
) -> dict[str, object]:
    """Show why a square X and X.T can share a shape but not axis semantics."""
    batch_rows, batch_shape = _matrix_shape(batch, "batch")
    if batch_shape[0] != batch_shape[1]:
        raise ValueError("counterexample requires a square [batch, features] matrix")
    labels = _sample_labels(sample_labels, batch_shape[0])
    normal = batch_linear_report(batch_rows, weights, bias)
    transposed_batch = [list(column) for column in zip(*batch_rows)]
    transposed = batch_linear_report(transposed_batch, weights, bias)
    feature_labels = [f"feature_{index}" for index in range(batch_shape[1])]
    return {
        "contract_version": TENSOR_SHAPES_CONTRACT_VERSION,
        "operation": "square_batch_transpose_counterexample",
        "original_axis_roles": ["sample", "feature"],
        "transposed_axis_roles": ["feature", "sample"],
        "normal": {**normal, "row_labels": labels},
        "transposed": {**transposed, "row_labels": feature_labels},
        "same_numeric_shape": normal["output"]["shape"] == transposed["output"]["shape"],
        "axis_semantics_changed": True,
    }


def tensor_shapes_certificate(operation: str, inputs: object, report: object) -> bool:
    """Recompute a supported shape report so altered dimensions or values fail."""
    if not isinstance(inputs, dict) or not isinstance(report, dict):
        return False
    try:
        if operation == "elementwise_add":
            expected = elementwise_add_report(inputs.get("left"), inputs.get("right"))
        elif operation == "batch_linear":
            expected = batch_linear_report(inputs.get("batch"), inputs.get("weights"), inputs.get("bias"))
        elif operation == "square_batch_transpose_counterexample":
            expected = square_batch_transpose_counterexample_report(
                inputs.get("batch"),
                inputs.get("weights"),
                inputs.get("bias"),
                inputs.get("sample_labels"),
            )
        else:
            return False
        return report == expected
    except (TypeError, ValueError):
        return False
