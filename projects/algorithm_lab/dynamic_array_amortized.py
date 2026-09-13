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


def _normalize_operations(operations: object) -> list[dict[str, object]]:
    if not isinstance(operations, list):
        raise ValueError("operations must be a list")
    normalized: list[dict[str, object]] = []
    for operation in operations:
        if not isinstance(operation, dict) or "op" not in operation:
            raise ValueError("each operation must declare op")
        if operation.get("op") == "push" and set(operation) == {"op", "value"}:
            value = operation["value"]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError("push value must be finite numeric")
            normalized.append({"op": "push", "value": float(value)})
        elif operation.get("op") == "pop" and set(operation) == {"op"}:
            normalized.append({"op": "pop"})
        else:
            raise ValueError("operations are exactly push with value, or pop")
    return normalized


def _hysteresis_potential(size: int, capacity: int) -> float:
    """Potential for grow-at-full, shrink-at-quarter dynamic arrays."""
    return 2 * size - capacity if 2 * size >= capacity else capacity / 2 - size


def dynamic_array_hysteresis_report(operations: object) -> dict[str, object]:
    """Trace a stack-like array with doubling and quarter-full shrinking.

    The potential is piecewise: 2n-c at least half full and c/2-n below
    half full.  Each valid push/pop has amortized cost at most 3.  Shrinking
    at one quarter rather than one half leaves slack after a resize, avoiding
    repeated grow/shrink copies at the same boundary.
    """
    actions = _normalize_operations(operations)
    capacity, items = 1, []
    potential = _hysteresis_potential(0, capacity)
    trace: list[dict[str, object]] = []
    total_actual = 0
    for index, action in enumerate(actions):
        size_before, capacity_before, potential_before = len(items), capacity, potential
        copied = 0
        if action["op"] == "push":
            if len(items) == capacity:
                copied = capacity
                capacity *= 2
            items.append(action["value"])
        else:
            if not items:
                raise ValueError("pop cannot be applied to an empty array")
            items.pop()
            if capacity > 1 and len(items) <= capacity // 4:
                copied = len(items)
                capacity //= 2
        potential = _hysteresis_potential(len(items), capacity)
        actual_cost = copied + 1
        amortized_cost = actual_cost + potential - potential_before
        if amortized_cost > 3:
            raise AssertionError("hysteresis potential invariant violated")
        total_actual += actual_cost
        trace.append({
            "operation_index": index, "operation": action,
            "size_before": size_before, "size_after": len(items),
            "capacity_before": capacity_before, "capacity_after": capacity,
            "copied_cells": copied, "actual_cost": actual_cost,
            "potential_before": potential_before, "potential_after": potential,
            "amortized_cost": amortized_cost,
        })
    return {
        "contract": "dynamic-array-hysteresis-amortized/v1",
        "operations": actions,
        "resize_policy": {"grow_when": "size_equals_capacity", "shrink_when": "size_at_most_quarter_capacity"},
        "initial_state": {"size": 0, "capacity": 1, "potential": .5},
        "operation_trace": trace,
        "final_state": {"size": len(items), "capacity": capacity, "potential": potential},
        "cost_summary": {
            "actual_total_cost": total_actual,
            "amortized_charge_total": 3 * len(actions),
            "actual_total_within_amortized_charge": total_actual <= 3 * len(actions),
            "maximum_single_amortized_cost": max((row["amortized_cost"] for row in trace), default=0),
        },
        "bound": "every valid prefix has actual work at most three times its push/pop operation count",
        "boundary": "single-threaded stack-like operations; excludes arbitrary deletion, allocation failure, object copy semantics, and wall-clock claims",
    }


def dynamic_array_hysteresis_certificate(operations: object, report: object) -> bool:
    if not isinstance(report, dict) or report.get("contract") != "dynamic-array-hysteresis-amortized/v1":
        return False
    try:
        return report == dynamic_array_hysteresis_report(operations)
    except (TypeError, ValueError):
        return False
