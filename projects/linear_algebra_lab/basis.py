"""Small, auditable experiments for column independence and basis coordinates."""

from __future__ import annotations

from math import isfinite, sqrt

from projects.linear_algebra_lab.main import EPSILON, solve


def _validate_columns(columns: list[list[float]], tolerance: float) -> int:
    if not columns or not columns[0] or any(len(column) != len(columns[0]) for column in columns):
        raise ValueError("columns must be a non-empty list of equally sized vectors")
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
           for column in columns for value in column):
        raise ValueError("columns must contain finite real values")
    return len(columns[0])


def column_independence_report(columns: list[list[float]], tolerance: float = EPSILON) -> dict[str, object]:
    """Return an order-preserving independent subfamily using Gram--Schmidt.

    A nonzero orthogonal residual means that the next column contributes a new
    direction; a residual at or below ``tolerance`` is numerically dependent on
    earlier retained directions.  This is a teaching rank diagnostic, not a
    replacement for pivoted QR/SVD on ill-conditioned production data.
    """
    ambient_dimension = _validate_columns(columns, tolerance)
    orthonormal: list[list[float]] = []
    basis_indices: list[int] = []
    residual_norms: list[float] = []
    for index, column in enumerate(columns):
        residual = [float(value) for value in column]
        for direction in orthonormal:
            coefficient = sum(left * right for left, right in zip(residual, direction))
            residual = [value - coefficient * direction[row] for row, value in enumerate(residual)]
        residual_norm = sqrt(sum(value * value for value in residual))
        residual_norms.append(residual_norm)
        if residual_norm > tolerance:
            orthonormal.append([value / residual_norm for value in residual])
            basis_indices.append(index)
    rank = len(basis_indices)
    return {
        "ambient_dimension": ambient_dimension,
        "rank": rank,
        "basis_indices": basis_indices,
        "residual_norms": residual_norms,
        "is_linearly_independent": rank == len(columns),
        "is_basis_for_ambient_space": len(columns) == ambient_dimension and rank == ambient_dimension,
    }


def basis_coordinate_report(
    columns: list[list[float]], target: list[float], tolerance: float = EPSILON,
) -> dict[str, object]:
    """Recover unique coordinates in a basis and return an Ax=b certificate."""
    report = column_independence_report(columns, tolerance)
    dimension = report["ambient_dimension"]
    if not report["is_basis_for_ambient_space"]:
        raise ValueError("coordinate recovery requires a linearly independent ambient-space basis")
    if len(target) != dimension or any(not isinstance(value, (int, float)) or isinstance(value, bool)
                                       or not isfinite(value) for value in target):
        raise ValueError("target must be a finite vector in the basis ambient space")
    matrix = [[columns[column][row] for column in range(dimension)] for row in range(dimension)]
    coordinates = solve(matrix, target, tolerance)
    reconstruction = [sum(matrix[row][column] * coordinates[column] for column in range(dimension))
                      for row in range(dimension)]
    residual = [reconstruction[row] - target[row] for row in range(dimension)]
    return {
        **report,
        "coordinates": coordinates,
        "reconstruction": reconstruction,
        "residual": residual,
        "reconstructs_target": all(abs(value) <= tolerance for value in residual),
    }
