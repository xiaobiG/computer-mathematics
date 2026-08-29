"""Weighted activity selection with a brute-force oracle for tiny test cases."""

from __future__ import annotations

from bisect import bisect_right
from itertools import combinations
from math import isfinite


Activity = tuple[float, float, float, str]


def _validate(activities: list[Activity]) -> None:
    for start, finish, value, _ in activities:
        if not all(isfinite(number) for number in (start, finish, value)) or start > finish or value < 0:
            raise ValueError("activities require finite start/finish/value, start <= finish, and nonnegative value")


def compatible_schedule(activities: list[Activity]) -> bool:
    """Return whether every pair can coexist when touching endpoints is allowed."""
    _validate(activities)
    ordered = sorted(activities, key=lambda item: (item[0], item[1], item[3]))
    return all(left[1] <= right[0] for left, right in zip(ordered, ordered[1:]))


def weighted_activity_selection(activities: list[Activity]) -> tuple[float, list[Activity]]:
    """Return an optimal compatible schedule using the prefix-DAG recurrence."""
    _validate(activities)
    ordered = sorted(activities, key=lambda item: (item[1], item[0], item[3]))
    finishes = [activity[1] for activity in ordered]
    previous = [bisect_right(finishes, activity[0], hi=index) - 1 for index, activity in enumerate(ordered)]
    best = [0.0] * (len(ordered) + 1)
    for index, (_, _, value, _) in enumerate(ordered, start=1):
        best[index] = max(best[index - 1], value + best[previous[index - 1] + 1])

    chosen: list[Activity] = []
    index = len(ordered)
    while index:
        activity = ordered[index - 1]
        include = activity[2] + best[previous[index - 1] + 1]
        if include > best[index - 1]:
            chosen.append(activity)
            index = previous[index - 1] + 1
        else:
            index -= 1
    return best[-1], list(reversed(chosen))


def brute_force_best_value(activities: list[Activity], *, max_activities: int = 18) -> float:
    """Enumerate small inputs as an oracle; intentionally reject large instances."""
    _validate(activities)
    if len(activities) > max_activities:
        raise ValueError("brute-force oracle is limited to small teaching inputs")
    best = 0.0
    for count in range(len(activities) + 1):
        for candidate in combinations(activities, count):
            if compatible_schedule(list(candidate)):
                best = max(best, sum(activity[2] for activity in candidate))
    return best
