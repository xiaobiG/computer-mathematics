"""Bounded counterexample searches used by the logic-and-proof lesson."""

from __future__ import annotations

from itertools import combinations_with_replacement


CONTRACT = "bounded-binary-search-counterexample/v1"


def _require_nonnegative_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _faulty_run(values: tuple[int, ...], target: int, fault: str) -> dict[str, object] | None:
    """Run one deliberately faulty half-open binary-search update.

    The state trace stops as soon as the faulty update either loses a present
    target or fails to reduce its candidate interval.  It is a counterexample
    finder, never a replacement implementation for binary search.
    """
    left, right = 0, len(values)
    trace: list[dict[str, int | str]] = []
    while left < right:
        middle = left + (right - left) // 2
        value = values[middle]
        if value == target:
            return None
        if value < target:
            next_left, next_right = (middle, right) if fault == "nonprogress_left" else (middle + 1, right)
            relation = "less"
        else:
            next_left, next_right = (left, middle - 1) if fault == "drops_left_boundary" else (left, middle)
            relation = "greater"
        trace.append({
            "left": left, "right": right, "middle": middle, "relation": relation,
            "next_left": next_left, "next_right": next_right,
        })
        if target in values and target not in values[next_left:next_right]:
            return {"failure": "present_target_lost", "trace": trace}
        if next_right - next_left >= right - left:
            return {"failure": "interval_did_not_strictly_shrink", "trace": trace}
        left, right = next_left, next_right
    return {"failure": "present_target_lost", "trace": trace} if target in values else None


def bounded_binary_search_counterexample(
    fault: str, *, max_length: int = 4, max_value: int = 3,
) -> dict[str, object]:
    """Find the first counterexample in a declared finite sorted-array domain."""
    if fault not in {"nonprogress_left", "drops_left_boundary"}:
        raise ValueError("fault must be nonprogress_left or drops_left_boundary")
    max_length = _require_nonnegative_int(max_length, "max_length")
    max_value = _require_nonnegative_int(max_value, "max_value")
    for length in range(max_length + 1):
        for values in combinations_with_replacement(range(max_value + 1), length):
            for target in range(-1, max_value + 2):
                failure = _faulty_run(values, target, fault)
                if failure is not None:
                    return {
                        "contract": CONTRACT,
                        "fault": fault,
                        "search_domain": {"max_length": max_length, "max_value": max_value},
                        "values": list(values),
                        "target": target,
                        **failure,
                        "interpretation": "finite counterexample found; this search does not prove claims beyond its declared domain",
                    }
    raise ValueError("no counterexample exists in the declared finite domain")


def bounded_binary_search_counterexample_certificate(
    fault: str, *, max_length: int, max_value: int, report: object,
) -> bool:
    """Re-enumerate the declared domain so changed witnesses cannot pass."""
    if not isinstance(report, dict):
        return False
    try:
        return report == bounded_binary_search_counterexample(
            fault, max_length=max_length, max_value=max_value,
        )
    except (TypeError, ValueError):
        return False
