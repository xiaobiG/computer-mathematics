"""A tiny, reproducible randomized range finder for teaching purposes."""

from dataclasses import dataclass
from math import isclose, isfinite, sqrt
from random import Random


@dataclass(frozen=True)
class RandomizedRangeReport:
    seed: int
    requested_rank: int
    sample_columns: int
    basis_columns: int
    power_iterations: int
    basis: tuple[tuple[float, ...], ...]
    approximation: tuple[tuple[float, ...], ...]
    frobenius_error: float


def _validate(matrix, rank, oversampling, power_iterations, seed):
    if not isinstance(matrix, (list, tuple)) or not matrix or not isinstance(matrix[0], (list, tuple)) or not matrix[0]:
        raise ValueError("matrix must be non-empty and rectangular")
    rows, columns = len(matrix), len(matrix[0])
    if any(not isinstance(row, (list, tuple)) or len(row) != columns for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    for row in matrix:
        for value in row:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
                raise ValueError("matrix entries must be finite numbers")
    if not isinstance(rank, int) or isinstance(rank, bool) or not 0 < rank <= min(rows, columns):
        raise ValueError("rank must be a positive integer no larger than the smaller dimension")
    if not isinstance(oversampling, int) or isinstance(oversampling, bool) or oversampling < 0:
        raise ValueError("oversampling must be a non-negative integer")
    if not isinstance(power_iterations, int) or isinstance(power_iterations, bool) or power_iterations < 0:
        raise ValueError("power_iterations must be a non-negative integer")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")


def _matmul(left, right):
    return [[sum(left[row][pivot] * right[pivot][column] for pivot in range(len(right)))
             for column in range(len(right[0]))]
            for row in range(len(left))]


def _transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def _orthonormal_columns(matrix, tolerance=1e-12):
    basis = []
    for column in _transpose(matrix):
        residual = [float(value) for value in column]
        for direction in basis:
            projection = sum(value * direction[index] for index, value in enumerate(residual))
            residual = [value - projection * direction[index] for index, value in enumerate(residual)]
        length = sqrt(sum(value * value for value in residual))
        if length > tolerance:
            basis.append([value / length for value in residual])
    return basis


def _approximation(matrix, basis):
    rows, columns = len(matrix), len(matrix[0])
    return [[sum(direction[row] * sum(direction[source] * matrix[source][column] for source in range(rows))
                 for direction in basis)
             for column in range(columns)]
            for row in range(rows)]


def _frobenius_error(matrix, approximation):
    return sqrt(sum((float(value) - approximation[row][column]) ** 2
                    for row, values in enumerate(matrix)
                    for column, value in enumerate(values)))


def randomized_range_report(matrix, rank, oversampling=2, power_iterations=0, seed=0):
    """Sample an approximate column range of ``matrix`` with a recorded seed.

    This is a range finder, not a production randomized SVD: it returns the
    projection ``QQ^T A``.  Power iterations amplify spectral separation but
    also increase matrix passes and floating-point sensitivity.
    """
    _validate(matrix, rank, oversampling, power_iterations, seed)
    rows, columns = len(matrix), len(matrix[0])
    sample_columns = min(columns, rank + oversampling)
    rng = Random(seed)
    omega = [[rng.uniform(-1.0, 1.0) for _ in range(sample_columns)] for _ in range(columns)]
    sketch = _matmul(matrix, omega)
    transpose = _transpose(matrix)
    for _ in range(power_iterations):
        sketch = _matmul(matrix, _matmul(transpose, sketch))
    basis = _orthonormal_columns(sketch)
    if not basis:
        raise ValueError("matrix has no non-zero sampled range")
    approximation = _approximation(matrix, basis)
    return RandomizedRangeReport(
        seed=seed,
        requested_rank=rank,
        sample_columns=sample_columns,
        basis_columns=len(basis),
        power_iterations=power_iterations,
        basis=tuple(tuple(column) for column in basis),
        approximation=tuple(tuple(row) for row in approximation),
        frobenius_error=_frobenius_error(matrix, approximation),
    )


def randomized_range_certificate(matrix, report, oversampling=2, tolerance=1e-12):
    """Replay the seeded sketch and reject altered report fields."""
    if not isinstance(report, RandomizedRangeReport):
        return False
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or tolerance < 0:
        return False
    try:
        expected = randomized_range_report(
            matrix,
            rank=report.requested_rank,
            oversampling=oversampling,
            power_iterations=report.power_iterations,
            seed=report.seed,
        )
    except ValueError:
        return False
    if (report.seed, report.requested_rank, report.sample_columns, report.basis_columns, report.power_iterations) != (
        expected.seed, expected.requested_rank, expected.sample_columns, expected.basis_columns, expected.power_iterations):
        return False
    if len(report.basis) != len(expected.basis) or len(report.approximation) != len(expected.approximation):
        return False
    for actual_column, expected_column in zip(report.basis, expected.basis):
        if len(actual_column) != len(expected_column) or any(
                not isclose(actual, target, rel_tol=tolerance, abs_tol=tolerance)
                for actual, target in zip(actual_column, expected_column)):
            return False
    for actual_row, expected_row in zip(report.approximation, expected.approximation):
        if len(actual_row) != len(expected_row) or any(
                not isclose(actual, target, rel_tol=tolerance, abs_tol=tolerance)
                for actual, target in zip(actual_row, expected_row)):
            return False
    return isclose(report.frobenius_error, expected.frobenius_error, rel_tol=tolerance, abs_tol=tolerance)
