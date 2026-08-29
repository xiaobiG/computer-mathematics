"""Operation-count experiments for asymptotic-complexity lessons."""

from __future__ import annotations


def operation_counts(size: int) -> dict[str, int]:
    """Return exact counts for representative linear, quadratic and exponential tasks."""
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError("size must be a non-negative integer")
    return {
        "linear_scan": size,
        "all_unordered_pairs": size * (size - 1) // 2,
        "all_subsets": 2 ** size,
    }


def two_sum_sorted_trace(values: list[float], target: float) -> tuple[tuple[int, int] | None, int]:
    """Find a sorted-array pair and count each sum comparison.

    On every failed comparison, one pointer moves inward.  Thus no index is
    revisited and the trace contains at most len(values)-1 comparisons.
    """
    if not isinstance(values, list) or any(values[index] > values[index + 1]
                                           for index in range(len(values) - 1)):
        raise ValueError("values must be a sorted list")
    left, right, comparisons = 0, len(values) - 1, 0
    while left < right:
        comparisons += 1
        total = values[left] + values[right]
        if total == target:
            return (left, right), comparisons
        if total < target:
            left += 1
        else:
            right -= 1
    return None, comparisons
