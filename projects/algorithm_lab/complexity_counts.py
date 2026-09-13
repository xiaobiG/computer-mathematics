"""Operation-count experiments for asymptotic-complexity lessons."""

from __future__ import annotations

from math import isfinite


def operation_counts(size: int) -> dict[str, int]:
    """Return exact counts for representative linear, quadratic and exponential tasks."""
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError("size must be a non-negative integer")
    return {
        "linear_scan": size,
        "all_unordered_pairs": size * (size - 1) // 2,
        "all_subsets": 2 ** size,
    }


def _sorted_values_and_target(values: object, target: object) -> tuple[list[float], float]:
    if not isinstance(values, list):
        raise ValueError("values must be a sorted list of finite numbers")
    if (not isinstance(target, (int, float)) or isinstance(target, bool) or not isfinite(target)
            or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                   for value in values)):
        raise ValueError("target and values must be finite numbers")
    normalized = [float(value) for value in values]
    if any(normalized[index] > normalized[index + 1] for index in range(len(normalized) - 1)):
        raise ValueError("values must be sorted")
    return normalized, float(target)


def two_sum_sorted_report(values: list[float], target: float) -> dict[str, object]:
    """Record why each failed two-sum comparison safely shrinks its interval.

    Each failed event records the discarded endpoint.  In a nondecreasing
    array, a sum below target rules out the left endpoint with every remaining
    right endpoint; a sum above target similarly rules out the right endpoint.
    This is a finite replay of that invariant, not a benchmark.
    """
    normalized, numeric_target = _sorted_values_and_target(values, target)
    left, right, events = 0, len(normalized) - 1, []
    while left < right:
        total = normalized[left] + normalized[right]
        event = {
            "interval_before": [left, right],
            "sum": total,
        }
        if total == numeric_target:
            event.update({"action": "found", "discarded_index": None, "discard_is_sound": True})
            events.append(event)
            return {
                "values": normalized,
                "target": numeric_target,
                "events": events,
                "pair": [left, right],
                "comparisons": len(events),
                "maximum_comparisons": max(0, len(normalized) - 1),
                "within_linear_comparison_bound": len(events) <= max(0, len(normalized) - 1),
                "model": "one_sum_comparison_per_event; no_wall_clock_claim",
            }
        if total < numeric_target:
            event.update({"action": "discard_left", "discarded_index": left, "discard_is_sound": True})
            events.append(event)
            left += 1
        else:
            event.update({"action": "discard_right", "discarded_index": right, "discard_is_sound": True})
            events.append(event)
            right -= 1
    return {
        "values": normalized,
        "target": numeric_target,
        "events": events,
        "pair": None,
        "comparisons": len(events),
        "maximum_comparisons": max(0, len(normalized) - 1),
        "within_linear_comparison_bound": len(events) <= max(0, len(normalized) - 1),
        "model": "one_sum_comparison_per_event; no_wall_clock_claim",
    }


def two_sum_sorted_certificate(values: object, target: object, report: object) -> bool:
    """Rebuild the finite interval trace, bound, and operation-model label."""
    if not isinstance(report, dict):
        return False
    try:
        return report == two_sum_sorted_report(values, target)
    except (KeyError, TypeError, ValueError):
        return False


def two_sum_sorted_trace(values: list[float], target: float) -> tuple[tuple[int, int] | None, int]:
    """Return the historical pair/count API from the replayable report."""
    report = two_sum_sorted_report(values, target)
    pair = report["pair"]
    return (tuple(pair) if pair is not None else None), report["comparisons"]
