"""Exact small-matrix determinant traces for the linear-algebra lesson."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DeterminantEvent:
    column: int
    pivot_row: int | None
    swapped: bool
    pivot: Fraction | None
    upper: tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class SquareMatrixClassification:
    """Exact consequences of elimination for one small square matrix."""

    determinant: Fraction
    rank: int
    nullity: int
    invertible: bool
    unique_solution_for_every_rhs: bool
    events: tuple[DeterminantEvent, ...]


def _validate(matrix: object) -> list[list[int]]:
    if (not isinstance(matrix, list) or not 1 <= len(matrix) <= 6
            or any(not isinstance(row, list) or len(row) != len(matrix) for row in matrix)
            or any(not isinstance(value, int) or isinstance(value, bool) for row in matrix for value in row)):
        raise ValueError("matrix must be a 1-to-6 square list of non-boolean integers")
    return matrix


def determinant_trace(matrix: object) -> tuple[Fraction, tuple[DeterminantEvent, ...]]:
    """Compute det(A) by row replacement, recording swaps and upper forms exactly."""
    source = _validate(matrix)
    size = len(source)
    upper = [[Fraction(value) for value in row] for row in source]
    sign, diagonal, events = 1, Fraction(1), []
    for column in range(size):
        pivot_row = next((row for row in range(column, size) if upper[row][column] != 0), None)
        if pivot_row is None:
            events.append(DeterminantEvent(column, None, False, None, tuple(tuple(row) for row in upper)))
            return Fraction(0), tuple(events)
        swapped = pivot_row != column
        if swapped:
            upper[column], upper[pivot_row] = upper[pivot_row], upper[column]
            sign *= -1
        pivot = upper[column][column]
        diagonal *= pivot
        for row in range(column + 1, size):
            factor = upper[row][column] / pivot
            upper[row] = [value - factor * base for value, base in zip(upper[row], upper[column])]
        events.append(DeterminantEvent(column, pivot_row, swapped, pivot, tuple(tuple(row) for row in upper)))
    return sign * diagonal, tuple(events)


def _exact_rank(matrix: list[list[int]]) -> int:
    """Return rank by exact row reduction, skipping non-pivot columns.

    A determinant trace may stop at the first missing diagonal pivot because
    the determinant is already zero.  Rank cannot: ``[[0, 1], [0, 0]]`` has
    a missing first-column pivot but still has rank one.
    """
    upper = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(matrix)):
        candidate = next((row for row in range(pivot_row, len(matrix))
                          if upper[row][column] != 0), None)
        if candidate is None:
            continue
        upper[pivot_row], upper[candidate] = upper[candidate], upper[pivot_row]
        pivot = upper[pivot_row][column]
        for row in range(pivot_row + 1, len(matrix)):
            factor = upper[row][column] / pivot
            upper[row] = [value - factor * base for value, base in zip(upper[row], upper[pivot_row])]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def classify_square_matrix(matrix: object) -> SquareMatrixClassification:
    """Connect exact elimination to rank, nullity, and the square-system claim.

    The determinant trace can stop at its first missing *diagonal* pivot: that
    already proves its determinant is zero.  Rank needs a separate exact
    reducer which also skips non-pivot columns, so an independent direction in
    a later column is not discarded.  This deliberately reports the *universal* claim
    about ``Ax=b`` rather than pretending every individual right-hand side is
    inconsistent when ``A`` is singular.
    """
    source = _validate(matrix)
    determinant, events = determinant_trace(source)
    rank = _exact_rank(source)
    invertible = rank == len(source)
    return SquareMatrixClassification(
        determinant=determinant,
        rank=rank,
        nullity=len(source) - rank,
        invertible=invertible,
        unique_solution_for_every_rhs=invertible,
        events=events,
    )


def determinant_trace_certificate(matrix: object, determinant: object, events: object) -> bool:
    if not isinstance(determinant, Fraction) or not isinstance(events, tuple):
        return False
    try:
        return (determinant, events) == determinant_trace(matrix)
    except (TypeError, ValueError):
        return False


def square_matrix_classification_certificate(matrix: object, report: object) -> bool:
    """Replay all displayed equivalence fields instead of trusting a flag."""
    if not isinstance(report, SquareMatrixClassification):
        return False
    try:
        return report == classify_square_matrix(matrix)
    except (TypeError, ValueError):
        return False
