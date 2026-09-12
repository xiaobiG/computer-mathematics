"""Partial-pivot LU factorisation with auditable PA = LU reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class LUFactorization:
    permutation: list[int]
    lower: list[list[float]]
    upper: list[list[float]]


@dataclass(frozen=True)
class LUReuseWorkReport:
    """A counted-work comparison for one LU factorization versus repeated ones."""

    matrix_size: int
    right_side_count: int
    factorization_elimination_updates: int
    triangular_dot_terms_per_right_side: int
    reuse_work_units: int
    refactor_every_time_work_units: int
    saved_work_units: int
    reused_solutions: list[list[float]]
    refactored_solutions: list[list[float]]
    solutions_match: bool
    pa_equals_lu: bool
    automatic_action: str


def _validate_square(matrix: list[list[float]], epsilon: float) -> int:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be nonempty and square")
    if epsilon <= 0 or not isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    if any(not isfinite(value) for row in matrix for value in row):
        raise ValueError("matrix entries must be finite")
    return size


def lu_factorize(matrix: list[list[float]], epsilon: float = 1e-12) -> LUFactorization:
    """Factor a nonsingular dense matrix as PA=LU using partial pivoting."""
    size = _validate_square(matrix, epsilon)
    upper = [[float(value) for value in row] for row in matrix]
    lower = [[1.0 if row == column else 0.0 for column in range(size)] for row in range(size)]
    permutation = list(range(size))
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(upper[row][column]))
        if abs(upper[pivot][column]) <= epsilon:
            raise ValueError("matrix is singular at this tolerance")
        if pivot != column:
            upper[column], upper[pivot] = upper[pivot], upper[column]
            permutation[column], permutation[pivot] = permutation[pivot], permutation[column]
            for previous in range(column):
                lower[column][previous], lower[pivot][previous] = lower[pivot][previous], lower[column][previous]
        for row in range(column + 1, size):
            multiplier = upper[row][column] / upper[column][column]
            lower[row][column] = multiplier
            for item in range(column, size):
                upper[row][item] -= multiplier * upper[column][item]
    return LUFactorization(permutation, lower, upper)


def solve_lu(factorization: LUFactorization, right_side: list[float]) -> list[float]:
    """Solve Ax=b from a factorisation of PA=LU by forward/back substitution."""
    size = len(factorization.permutation)
    if len(right_side) != size or any(not isfinite(value) for value in right_side):
        raise ValueError("right_side must have matching finite entries")
    permuted = [float(right_side[index]) for index in factorization.permutation]
    intermediate = [0.0] * size
    for row in range(size):
        intermediate[row] = permuted[row] - sum(factorization.lower[row][column] * intermediate[column]
                                                 for column in range(row))
    result = [0.0] * size
    for row in range(size - 1, -1, -1):
        diagonal = factorization.upper[row][row]
        if diagonal == 0.0:
            raise ValueError("factorization has a zero upper diagonal")
        result[row] = (intermediate[row] - sum(factorization.upper[row][column] * result[column]
                                                for column in range(row + 1, size))) / diagonal
    return result


def solve_many_lu(factorization: LUFactorization, right_sides: list[list[float]]) -> list[list[float]]:
    """Reuse one factorisation for multiple right-side vectors."""
    return [solve_lu(factorization, right_side) for right_side in right_sides]


def permuted_rows(matrix: list[list[float]], permutation: list[int]) -> list[list[float]]:
    """Construct PA by selecting the original rows in permutation order."""
    if len(matrix) != len(permutation) or sorted(permutation) != list(range(len(matrix))):
        raise ValueError("permutation must select every matrix row exactly once")
    return [[float(value) for value in matrix[index]] for index in permutation]


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [[sum(left[row][inner] * right[inner][column] for inner in range(len(right)))
             for column in range(len(right[0]))] for row in range(len(left))]


def _close_matrices(left: list[list[float]], right: list[list[float]], tolerance: float = 1e-12) -> bool:
    return len(left) == len(right) and all(
        len(left_row) == len(right_row) and all(abs(a - b) <= tolerance for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def lu_reuse_work_report(matrix: list[list[float]], right_sides: list[list[float]], epsilon: float = 1e-12) -> LUReuseWorkReport:
    """Compare declared work after actually replaying both solve paths.

    Work units count only elimination multiply-subtract updates and triangular
    dot-product terms. They exclude pivot searches, divisions, allocation,
    caching, and hardware effects; this is not a performance benchmark.
    """
    size = _validate_square(matrix, epsilon)
    if not isinstance(right_sides, list) or len(right_sides) < 2:
        raise ValueError("right_sides must contain at least two vectors to compare reuse")
    factorization = lu_factorize(matrix, epsilon)
    reused = solve_many_lu(factorization, right_sides)
    refactored = [solve_lu(lu_factorize(matrix, epsilon), right_side) for right_side in right_sides]
    factor_updates = sum((size - column - 1) * (size - column) for column in range(size))
    triangular_terms = size * (size - 1)
    reuse_work = factor_updates + len(right_sides) * triangular_terms
    refactor_work = len(right_sides) * (factor_updates + triangular_terms)
    return LUReuseWorkReport(
        size, len(right_sides), factor_updates, triangular_terms, reuse_work, refactor_work,
        refactor_work - reuse_work, reused, refactored, _close_matrices(reused, refactored),
        _close_matrices(permuted_rows(matrix, factorization.permutation), _matmul(factorization.lower, factorization.upper)),
        "none",
    )


def lu_reuse_work_certificate(matrix: list[list[float]], right_sides: list[list[float]], report: LUReuseWorkReport, epsilon: float = 1e-12) -> bool:
    """Rebuild both solve paths and reject changed work claims."""
    if not isinstance(report, LUReuseWorkReport):
        return False
    try:
        return report == lu_reuse_work_report(matrix, right_sides, epsilon)
    except (TypeError, ValueError):
        return False
