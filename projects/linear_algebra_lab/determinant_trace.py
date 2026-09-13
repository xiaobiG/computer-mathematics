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


def determinant_trace_certificate(matrix: object, determinant: object, events: object) -> bool:
    if not isinstance(determinant, Fraction) or not isinstance(events, tuple):
        return False
    try:
        return (determinant, events) == determinant_trace(matrix)
    except (TypeError, ValueError):
        return False
