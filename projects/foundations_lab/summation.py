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


def sum_of_squares_report(count: int) -> dict[str, object]:
    """Compare an explicit finite sum with its closed form for 1^2+...+n^2."""
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("count must be a non-negative integer")
    enumerated = finite_sum(lambda index: index * index, 1, count + 1)
    closed_form = count * (count + 1) * (2 * count + 1) / 6
    if count == 0:
        induction = {
            "case": "base",
            "previous_count": None,
            "previous_closed_form": None,
            "added_square": None,
            "recursive_sum": 0.0,
            "closed_form_increment": None,
            "step_preserves_closed_form": True,
        }
    else:
        previous_closed_form = (count - 1) * count * (2 * count - 1) / 6
        added_square = float(count * count)
        recursive_sum = previous_closed_form + added_square
        closed_form_increment = closed_form - previous_closed_form
        induction = {
            "case": "step",
            "previous_count": count - 1,
            "previous_closed_form": previous_closed_form,
            "added_square": added_square,
            "recursive_sum": recursive_sum,
            "closed_form_increment": closed_form_increment,
            "step_preserves_closed_form": (
                recursive_sum == closed_form and closed_form_increment == added_square
            ),
        }
    return {
        "count": count,
        "enumerated_sum": enumerated,
        "closed_form": closed_form,
        "certificate": {
            "enumeration_matches_closed_form": enumerated == closed_form,
            "empty_sum_is_zero": count != 0 or enumerated == 0.0,
        },
        "induction": induction,
    }


def sum_of_squares_certificate(
    count: int, report: dict[str, object]
) -> dict[str, bool]:
    """Recompute the sigma loop and closed form without trusting a report."""
    empty = {
        "count_matches": False,
        "enumeration_matches_half_open_sum": False,
        "closed_form_matches": False,
        "empty_sum_boundary_matches": False,
        "induction_trace_matches": False,
        "valid": False,
    }
    try:
        expected = sum_of_squares_report(count)
        if not isinstance(report, dict):
            return empty
        fields_match = report.get("count") == expected["count"]
        enumeration_matches = report.get("enumerated_sum") == expected["enumerated_sum"]
        closed_form_matches = report.get("closed_form") == expected["closed_form"]
        empty_boundary = count != 0 or report.get("enumerated_sum") == 0.0
        induction_trace_matches = report.get("induction") == expected["induction"]
        return {
            "count_matches": fields_match,
            "enumeration_matches_half_open_sum": enumeration_matches,
            "closed_form_matches": closed_form_matches,
            "empty_sum_boundary_matches": empty_boundary,
            "induction_trace_matches": induction_trace_matches,
            "valid": (
                fields_match
                and enumeration_matches
                and closed_form_matches
                and empty_boundary
                and induction_trace_matches
            ),
        }
    except (TypeError, ValueError):
        return empty
