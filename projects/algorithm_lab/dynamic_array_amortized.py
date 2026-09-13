"""A traceable doubling-array experiment with a potential-method certificate."""

from __future__ import annotations

from math import isfinite


CONTRACT = "dynamic-array-doubling-amortized/v1"


def _normalize_values(values: object) -> list[float]:
    if not isinstance(values, list):
        raise ValueError("values must be a list")
    normalized: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError("values must be finite numeric teaching payloads")
        normalized.append(float(value))
    return normalized


def dynamic_array_doubling_report(values: object) -> dict[str, object]:
    """Append values to a capacity-doubling array and charge every copied cell.

    Actual cost is one write plus the old capacity when a full buffer is
    copied.  Potential Phi(n, c) = 2n - c + 1 starts non-negative at an
    empty one-cell array and makes every append have amortized cost at most 3.
    """
    items = _normalize_values(values)
    capacity, size, potential = 1, 0, 0
    trace: list[dict[str, object]] = []
    total_actual = 0
    for index, value in enumerate(items):
        old_capacity, old_potential = capacity, potential
        copied = 0
        if size == capacity:
            copied = capacity
            capacity *= 2
        size += 1
        actual_cost = copied + 1
        potential = 2 * size - capacity + 1
        amortized_cost = actual_cost + potential - old_potential
        if amortized_cost > 3:
            raise AssertionError("doubling potential invariant violated")
        total_actual += actual_cost
        trace.append({
            "append_index": index, "value": value,
            "capacity_before": old_capacity, "capacity_after": capacity,
            "copied_cells": copied, "actual_cost": actual_cost,
            "potential_before": old_potential, "potential_after": potential,
            "amortized_cost": amortized_cost,
        })
    return {
        "contract": CONTRACT,
        "input_values": items,
        "initial_state": {"size": 0, "capacity": 1, "potential": 0},
        "append_trace": trace,
        "final_state": {"size": size, "capacity": capacity, "potential": potential},
        "cost_summary": {
            "actual_total_cost": total_actual,
            "amortized_charge_total": 3 * len(items),
            "actual_total_within_amortized_charge": total_actual <= 3 * len(items),
            "maximum_single_amortized_cost": max((row["amortized_cost"] for row in trace), default=0),
        },
        "bound": "for every prefix of m appends, actual writes plus copied cells are at most 3m",
        "boundary": "append-only doubling array; excludes shrinking, allocation failure, concurrency, and wall-clock claims",
    }


def dynamic_array_doubling_certificate(values: object, report: object) -> bool:
    """Replay every resize and potential value from the original append sequence."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        return report == dynamic_array_doubling_report(values)
    except (TypeError, ValueError):
        return False
