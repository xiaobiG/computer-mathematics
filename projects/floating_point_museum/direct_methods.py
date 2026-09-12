"""Replayable two-by-two Gaussian-elimination comparisons for teaching."""

from __future__ import annotations

from math import isfinite


def _validate_system(matrix: list[list[float]], right_side: list[float]) -> tuple[list[list[float]], list[float]]:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix) or len(right_side) != 2:
        raise ValueError("this teaching experiment requires a 2-by-2 system")
    values = [value for row in matrix for value in row] + right_side
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) for value in values):
        raise ValueError("matrix and right side must contain finite numbers")
    return [[float(value) for value in row] for row in matrix], [float(value) for value in right_side]


def _infinity_norm(values: list[float]) -> float:
    return max(abs(value) for value in values)


def _residual(matrix: list[list[float]], solution: list[float], right_side: list[float]) -> list[float]:
    return [right_side[row] - sum(matrix[row][column] * solution[column] for column in range(2)) for row in range(2)]


def _relative_forward_error(solution: list[float], reference_solution: list[float]) -> float:
    denominator = _infinity_norm(reference_solution)
    if denominator == 0.0:
        raise ValueError("reference_solution must have non-zero infinity norm")
    return _infinity_norm([candidate - reference for candidate, reference in zip(solution, reference_solution)]) / denominator


def _eliminate(matrix: list[list[float]], right_side: list[float], partial_pivoting: bool) -> tuple[list[float], list[dict[str, object]]]:
    augmented = [row[:] + [right_side[index]] for index, row in enumerate(matrix)]
    trace: list[dict[str, object]] = []
    for column in range(2):
        pivot_row = max(range(column, 2), key=lambda row: abs(augmented[row][column])) if partial_pivoting else column
        if augmented[pivot_row][column] == 0.0:
            raise ValueError("zero pivot: this method cannot continue")
        swapped = pivot_row != column
        augmented[column], augmented[pivot_row] = augmented[pivot_row], augmented[column]
        pivot = augmented[column][column]
        factors = []
        for row in range(column + 1, 2):
            factor = augmented[row][column] / pivot
            factors.append(factor)
            for item in range(column, 3):
                augmented[row][item] -= factor * augmented[column][item]
        trace.append({
            "column": column,
            "pivot_row": pivot_row,
            "swapped": swapped,
            "pivot": pivot,
            "factors": factors,
            "augmented_after": [row[:] for row in augmented],
        })
    solution = [0.0, 0.0]
    for row in range(1, -1, -1):
        solution[row] = (augmented[row][2] - sum(augmented[row][column] * solution[column] for column in range(row + 1, 2))) / augmented[row][row]
    return solution, trace


def direct_method_comparison(
    matrix: list[list[float]], right_side: list[float], reference_solution: list[float]
) -> dict[str, object]:
    """Compare no-pivot and partial-pivot elimination on one known system.

    ``reference_solution`` is an external teaching oracle, not a production
    luxury: forward error cannot be measured in practice when the true answer
    is unknown.  Residual and scaled backward error remain available there.
    """
    matrix, right_side = _validate_system(matrix, right_side)
    if len(reference_solution) != 2 or any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)
        for value in reference_solution
    ):
        raise ValueError("reference_solution must be a finite length-two vector")
    reference_solution = [float(value) for value in reference_solution]
    without_solution, without_trace = _eliminate(matrix, right_side, partial_pivoting=False)
    pivoted_solution, pivoted_trace = _eliminate(matrix, right_side, partial_pivoting=True)

    def method_report(solution: list[float], trace: list[dict[str, object]]) -> dict[str, object]:
        residual = _residual(matrix, solution, right_side)
        matrix_norm = max(sum(abs(value) for value in row) for row in matrix)
        denominator = matrix_norm * _infinity_norm(solution) + _infinity_norm(right_side)
        return {
            "solution": solution,
            "trace": trace,
            "residual": residual,
            "residual_norm": _infinity_norm(residual),
            "scaled_backward_error": _infinity_norm(residual) / denominator,
            "relative_forward_error": _relative_forward_error(solution, reference_solution),
        }

    without = method_report(without_solution, without_trace)
    pivoted = method_report(pivoted_solution, pivoted_trace)
    return {
        "without_pivoting": without,
        "partial_pivoting": pivoted,
        "certificate": {
            "partial_pivoting_used_a_swap": any(event["swapped"] for event in pivoted_trace),
            "partial_pivoting_has_small_backward_error": pivoted["scaled_backward_error"] <= 1e-12,
            "partial_pivoting_is_no_worse_in_forward_error": pivoted["relative_forward_error"] <= without["relative_forward_error"],
        },
    }


def direct_method_comparison_certificate(
    matrix: list[list[float]], right_side: list[float], reference_solution: list[float], report: dict[str, object]
) -> bool:
    """Replay both elimination traces and reject a changed metric or decision."""
    if not isinstance(report, dict):
        return False
    try:
        return report == direct_method_comparison(matrix, right_side, reference_solution)
    except (TypeError, ValueError, ZeroDivisionError):
        return False
