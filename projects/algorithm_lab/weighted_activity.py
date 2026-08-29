"""Weighted activity selection with a brute-force oracle for tiny test cases."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from itertools import combinations
from math import isfinite


Activity = tuple[float, float, float, str]


@dataclass(frozen=True)
class WeightedActivityEvent:
    """One prefix-DAG relaxation for a sorted activity."""

    prefix_size: int
    activity: Activity
    compatible_prefix_size: int
    skip_value: float
    take_value: float
    best_value: float
    chose_activity: bool


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
    value, chosen, _ = weighted_activity_trace(activities)
    return value, chosen


def weighted_activity_trace(activities: list[Activity]) -> tuple[float, list[Activity], list[WeightedActivityEvent]]:
    """Return an optimal schedule together with every ``OPT(j)`` transition."""
    _validate(activities)
    ordered = sorted(activities, key=lambda item: (item[1], item[0], item[3]))
    finishes = [activity[1] for activity in ordered]
    previous = [bisect_right(finishes, activity[0], hi=index) - 1 for index, activity in enumerate(ordered)]
    best = [0.0] * (len(ordered) + 1)
    events: list[WeightedActivityEvent] = []
    for index, (_, _, value, _) in enumerate(ordered, start=1):
        compatible_prefix_size = previous[index - 1] + 1
        skip_value = best[index - 1]
        take_value = value + best[compatible_prefix_size]
        chose_activity = take_value > skip_value
        best[index] = take_value if chose_activity else skip_value
        events.append(WeightedActivityEvent(
            index, ordered[index - 1], compatible_prefix_size,
            skip_value, take_value, best[index], chose_activity,
        ))

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
    return best[-1], list(reversed(chosen)), events


def weighted_activity_trace_certificate(
    activities: list[Activity],
    value: float,
    chosen: list[Activity],
    events: list[WeightedActivityEvent],
) -> bool:
    """Replay each prefix-DAG edge and verify a reconstructed optimum.

    This certifies one execution of the recurrence and traceback.  The proof
    that the two incoming edges cover every feasible schedule remains the
    mathematical optimal-substructure argument in the accompanying lesson.
    """
    try:
        _validate(activities)
    except ValueError:
        return False
    ordered = sorted(activities, key=lambda item: (item[1], item[0], item[3]))
    if len(events) != len(ordered):
        return False
    finishes = [activity[1] for activity in ordered]
    best = [0.0]
    for prefix_size, (activity, event) in enumerate(zip(ordered, events), start=1):
        compatible_prefix_size = bisect_right(finishes, activity[0], hi=prefix_size - 1)
        skip_value = best[-1]
        take_value = activity[2] + best[compatible_prefix_size]
        chose_activity = take_value > skip_value
        expected = take_value if chose_activity else skip_value
        if event != WeightedActivityEvent(
            prefix_size, activity, compatible_prefix_size,
            skip_value, take_value, expected, chose_activity,
        ):
            return False
        best.append(expected)
    return (
        value == best[-1]
        and compatible_schedule(chosen)
        and sum(activity[2] for activity in chosen) == value
        and all(activity in ordered for activity in chosen)
    )


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
