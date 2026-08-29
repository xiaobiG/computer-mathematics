"""Partial-pivot LU factorisation with auditable PA = LU reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class LUFactorization:
    permutation: list[int]
    lower: list[list[float]]
    upper: list[list[float]]


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
