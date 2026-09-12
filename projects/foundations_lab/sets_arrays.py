"""Finite set operations and rectangular-array shape reports for teaching."""

from __future__ import annotations

from math import isfinite


SETS_ARRAYS_CONTRACT_VERSION = "sets-arrays/v1"


def _members(value: object, name: str) -> list[int | float | str]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    if any(isinstance(item, bool) or not isinstance(item, (int, float, str)) for item in value):
        raise ValueError(f"{name} elements must be finite numbers or strings")
    if any(isinstance(item, float) and not isfinite(item) for item in value):
        raise ValueError(f"{name} elements must be finite numbers or strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} must not contain duplicate members")
    return list(value)


def _matrix(value: object) -> list[list[int | float | str]]:
    if not isinstance(value, list) or not value or any(not isinstance(row, list) or not row for row in value):
        raise ValueError("matrix must be a non-empty list of non-empty rows")
    width = len(value[0])
    if any(len(row) != width for row in value):
        raise ValueError("matrix rows must have one shared width")
    if any(isinstance(item, bool) or not isinstance(item, (int, float, str)) for row in value for item in row):
        raise ValueError("matrix entries must be finite numbers or strings")
    if any(isinstance(item, float) and not isfinite(item) for row in value for item in row):
        raise ValueError("matrix entries must be finite numbers or strings")
    return [list(row) for row in value]


def _coordinate(value: object, bound: int, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < bound:
        raise ValueError(f"{name} must be an integer index inside the matrix")
    return value


def sets_arrays_report(
    left: object, right: object, matrix: object, row: object, column: object
) -> dict[str, object]:
    """Bind finite set semantics to a zero-based rectangular-array lookup."""
    left_values, right_values, matrix_values = _members(left, "left"), _members(right, "right"), _matrix(matrix)
    row_index = _coordinate(row, len(matrix_values), "row")
    column_index = _coordinate(column, len(matrix_values[0]), "column")
    left_set, right_set = set(left_values), set(right_values)
    sort_key = lambda item: (type(item).__name__, repr(item))
    return {
        "contract_version": SETS_ARRAYS_CONTRACT_VERSION,
        "sets": {
            "left": left_values,
            "right": right_values,
            "union": sorted(left_set | right_set, key=sort_key),
            "intersection": sorted(left_set & right_set, key=sort_key),
            "left_minus_right": sorted(left_set - right_set, key=sort_key),
            "right_minus_left": sorted(right_set - left_set, key=sort_key),
        },
        "array": {
            "values": matrix_values,
            "shape": [len(matrix_values), len(matrix_values[0])],
            "index": [row_index, column_index],
            "value": matrix_values[row_index][column_index],
            "index_origin": 0,
        },
    }


def sets_arrays_certificate(left: object, right: object, matrix: object, row: object, column: object, report: object) -> bool:
    """Rebuild set operations and the shape lookup to reject altered claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == sets_arrays_report(left, right, matrix, row, column)
    except (TypeError, ValueError):
        return False
