"""Auditable sample covariance and correlation calculations for teaching."""

from __future__ import annotations

from math import isfinite, sqrt


def _validate_vector(values: list[float], name: str, *, min_length: int = 2) -> None:
    if len(values) < min_length or any(not isinstance(value, (int, float)) or isinstance(value, bool)
                                       or not isfinite(value) for value in values):
        raise ValueError(f"{name} must contain at least {min_length} finite real values")


def _validate_pair(xs: list[float], ys: list[float]) -> None:
    _validate_vector(xs, "xs")
    _validate_vector(ys, "ys")
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")


def sample_covariance(xs: list[float], ys: list[float]) -> float:
    """Return the Bessel-corrected sample covariance of two paired columns."""
    _validate_pair(xs, ys)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / (len(xs) - 1)


def sample_correlation(xs: list[float], ys: list[float]) -> float:
    """Return Pearson's r; reject a constant column with zero standard deviation."""
    covariance = sample_covariance(xs, ys)
    standard_x = sqrt(sample_covariance(xs, xs))
    standard_y = sqrt(sample_covariance(ys, ys))
    if standard_x == 0.0 or standard_y == 0.0:
        raise ValueError("correlation is undefined for a constant column")
    return covariance / (standard_x * standard_y)


def covariance_matrix(rows: list[list[float]]) -> list[list[float]]:
    """Return a Bessel-corrected covariance matrix for rows of observations."""
    if len(rows) < 2 or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("rows must contain at least two non-empty equally sized observations")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
           for row in rows for value in row):
        raise ValueError("rows must contain finite real values")
    width = len(rows[0])
    columns = [[row[column] for row in rows] for column in range(width)]
    return [[sample_covariance(left, right) for right in columns] for left in columns]


def covariance_report(rows: list[list[float]], tolerance: float = 1e-12) -> dict[str, object]:
    """Compute covariance and certify centering, symmetry, and nonnegative variances."""
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    matrix = covariance_matrix(rows)
    width = len(matrix)
    means = [sum(row[column] for row in rows) / len(rows) for column in range(width)]
    centered_column_sums = [sum(row[column] - means[column] for row in rows) for column in range(width)]
    certificate = {
        "centered_columns_sum_to_zero": all(abs(total) <= tolerance for total in centered_column_sums),
        "matrix_is_symmetric": all(abs(matrix[row][column] - matrix[column][row]) <= tolerance
                                    for row in range(width) for column in range(width)),
        "variances_are_nonnegative": all(matrix[index][index] >= -tolerance for index in range(width)),
    }
    certificate["valid"] = all(certificate.values())
    return {"means": means, "covariance": matrix, "certificate": certificate}
