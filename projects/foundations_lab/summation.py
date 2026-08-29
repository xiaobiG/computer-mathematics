"""Finite-sum experiments that connect sigma notation to executable loops."""

from __future__ import annotations

from math import isfinite
from typing import Callable


def finite_sum(term: Callable[[int], float], start: int, stop: int) -> float:
    """Return sum(term(i) for i in [start, stop)); reject non-finite terms."""
    if not callable(term):
        raise ValueError("term must be callable")
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (start, stop)):
        raise ValueError("start and stop must be integers")
    if stop < start:
        raise ValueError("stop must be at least start")
    total = 0.0
    for index in range(start, stop):
        value = term(index)
        if not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError("every term must be finite")
        total += value
    return total


def sum_of_squares_report(count: int) -> dict[str, float | int | dict[str, bool]]:
    """Compare an explicit finite sum with its closed form for 1^2+...+n^2."""
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("count must be a non-negative integer")
    enumerated = finite_sum(lambda index: index * index, 1, count + 1)
    closed_form = count * (count + 1) * (2 * count + 1) / 6
    return {
        "count": count,
        "enumerated_sum": enumerated,
        "closed_form": closed_form,
        "certificate": {
            "enumeration_matches_closed_form": enumerated == closed_form,
            "empty_sum_is_zero": count != 0 or enumerated == 0.0,
        },
    }
