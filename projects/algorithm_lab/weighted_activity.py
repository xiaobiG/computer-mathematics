"""Weighted activity selection with a brute-force oracle for tiny test cases."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import Any


Activity = tuple[float, float, float, str]
UnweightedActivity = tuple[float, float, str]


def _finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


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


@dataclass(frozen=True)
class ActivitySelectionEvent:
    """One earliest-finish decision in the unweighted greedy scan."""

    activity: UnweightedActivity
    selected: bool
    current_end: float


def _validate(activities: list[Activity]) -> None:
    for start, finish, value, _ in activities:
        if not all(isfinite(number) for number in (start, finish, value)) or start > finish or value < 0:
            raise ValueError("activities require finite start/finish/value, start <= finish, and nonnegative value")


def _parse_reader_task(task: object) -> tuple[str, list[UnweightedActivity] | list[Activity]]:
    """Validate a reader-authored interval-scheduling task contract.

    A solver cannot infer whether "best schedule" means most appointments or
    most value.  Requiring that choice, the half-open endpoint convention, and
    an objective-specific acceptance invariant makes this distinction explicit
    before an algorithm is selected.
    """
    if not isinstance(task, dict) or set(task) != {
        "interval_semantics", "objective", "acceptance_invariant", "activities",
    }:
        raise ValueError("task must declare interval_semantics, objective, acceptance_invariant, and activities")
    if task["interval_semantics"] != "half_open":
        raise ValueError("this lesson accepts only the declared half_open interval semantics")
    objective = task["objective"]
    expected_invariant = {
        "maximize_count": "compatible_schedule_and_maximum_cardinality",
        "maximize_value": "compatible_schedule_and_maximum_total_value",
    }
    if objective not in expected_invariant:
        raise ValueError("objective must be maximize_count or maximize_value")
    if task["acceptance_invariant"] != expected_invariant[objective]:
        raise ValueError("acceptance_invariant does not measure the declared objective")
    raw_activities = task["activities"]
    if not isinstance(raw_activities, list):
        raise ValueError("activities must be a list of reader-authored activity records")

    names: set[str] = set()
    parsed: list[Any] = []
    expected_keys = {"start", "finish", "name"}
    if objective == "maximize_value":
        expected_keys.add("value")
    for raw in raw_activities:
        if not isinstance(raw, dict) or set(raw) != expected_keys:
            raise ValueError("activity fields do not match the declared objective")
        start, finish, name = raw["start"], raw["finish"], raw["name"]
        if not (_finite_number(start) and _finite_number(finish) and isinstance(name, str) and name):
            raise ValueError("each activity needs finite endpoints and a nonempty string name")
        if start > finish or name in names:
            raise ValueError("activity endpoints must be ordered and names must be unique")
        names.add(name)
        if objective == "maximize_count":
            parsed.append((float(start), float(finish), name))
        else:
            value = raw["value"]
            if not _finite_number(value) or value < 0:
                raise ValueError("a value objective needs a finite nonnegative value for every activity")
            parsed.append((float(start), float(finish), float(value), name))
    return objective, parsed


def diagnose_activity_task(task: object, *, oracle_limit: int = 18) -> dict[str, object]:
    """Choose a scheduling method from a reader-authored task and its invariant.

    This is deliberately a modelling diagnostic, not a natural-language parser:
    the reader supplies the mathematical contract.  Tiny inputs are checked
    against exhaustive search; larger inputs keep the semantic invariant but
    report that the exponential oracle was intentionally not run.
    """
    if not isinstance(oracle_limit, int) or isinstance(oracle_limit, bool) or oracle_limit < 0:
        raise ValueError("oracle_limit must be a nonnegative integer")
    objective, activities = _parse_reader_task(task)
    oracle_checked = len(activities) <= oracle_limit
    if objective == "maximize_count":
        unweighted = activities  # Narrowed by the task contract above.
        chosen, trace = activity_selection_trace(unweighted)
        cardinality = len(chosen)
        return {
            "objective": objective,
            "recommended_method": "earliest_finish_greedy",
            "state_meaning": "current_end is the finish time of the latest selected activity",
            "chosen_names": [activity[2] for activity in chosen],
            "objective_value": cardinality,
            "reader_invariant": "chosen intervals are compatible and have maximum cardinality",
            "oracle_checked": oracle_checked,
            "oracle_value": brute_force_max_cardinality(unweighted, max_activities=oracle_limit)
            if oracle_checked else None,
            "trace_steps": len(trace),
            "first_broken_greedy_premise": None,
        }

    weighted = activities  # Narrowed by the task contract above.
    value, chosen, trace = weighted_activity_trace(weighted)
    greedy_chosen, _ = activity_selection_trace([(start, finish, name) for start, finish, _, name in weighted])
    value_by_name = {name: activity_value for _, _, activity_value, name in weighted}
    greedy_value = sum(value_by_name[activity[2]] for activity in greedy_chosen)
    return {
        "objective": objective,
        "recommended_method": "prefix_dag_dynamic_programming",
        "state_meaning": "OPT(j) is the maximum total value among the first j activities sorted by finish time",
        "chosen_names": [activity[3] for activity in chosen],
        "objective_value": value,
        "reader_invariant": "chosen intervals are compatible and have maximum total value",
        "oracle_checked": oracle_checked,
        "oracle_value": brute_force_best_value(weighted, max_activities=oracle_limit) if oracle_checked else None,
        "trace_steps": len(trace),
        "earliest_finish_value": greedy_value,
        "earliest_finish_is_optimal_on_this_input": greedy_value == value,
        "first_broken_greedy_premise": "exchanging an activity must preserve the declared total-value objective",
    }


def _validate_unweighted(activities: list[UnweightedActivity]) -> None:
    for activity in activities:
        if not isinstance(activity, tuple) or len(activity) != 3:
            raise ValueError("activities must be (start, finish, name) tuples")
        start, finish, _ = activity
        if not all(isinstance(number, (int, float)) and not isinstance(number, bool) and isfinite(number)
                   for number in (start, finish)) or start > finish:
            raise ValueError("activities require finite start/finish values with start <= finish")


def activity_selection_trace(
    activities: list[UnweightedActivity],
) -> tuple[list[UnweightedActivity], list[ActivitySelectionEvent]]:
    """Select a maximum-cardinality compatible subset by earliest finish time."""
    _validate_unweighted(activities)
    chosen: list[UnweightedActivity] = []
    events: list[ActivitySelectionEvent] = []
    current_end = float("-inf")
    for activity in sorted(activities, key=lambda item: (item[1], item[0], item[2])):
        selected = activity[0] >= current_end
        if selected:
            chosen.append(activity)
            current_end = activity[1]
        events.append(ActivitySelectionEvent(activity, selected, current_end))
    return chosen, events


def activity_selection_certificate(
    activities: list[UnweightedActivity],
    chosen: list[UnweightedActivity],
    events: list[ActivitySelectionEvent],
) -> bool:
    """Replay the greedy scan and cross-check it against a tiny exhaustive oracle.

    The oracle is deliberately bounded: it is a test oracle for the exchange
    proof, not the production algorithm nor a replacement for that proof.
    """
    try:
        expected_chosen, expected_events = activity_selection_trace(activities)
        return (
            chosen == expected_chosen
            and events == expected_events
            and unweighted_compatible_schedule(chosen)
            and len(chosen) == brute_force_max_cardinality(activities)
        )
    except (TypeError, ValueError):
        return False


def unweighted_compatible_schedule(activities: list[UnweightedActivity]) -> bool:
    """Return whether half-open unweighted intervals can coexist."""
    _validate_unweighted(activities)
    ordered = sorted(activities, key=lambda item: (item[0], item[1], item[2]))
    return all(left[1] <= right[0] for left, right in zip(ordered, ordered[1:]))


def brute_force_max_cardinality(
    activities: list[UnweightedActivity], *, max_activities: int = 18,
) -> int:
    """Return an exhaustive cardinality oracle for deliberately tiny instances."""
    _validate_unweighted(activities)
    if len(activities) > max_activities:
        raise ValueError("brute-force oracle is limited to small teaching inputs")
    return max(
        (count for count in range(len(activities) + 1)
         if any(unweighted_compatible_schedule(list(candidate))
                for candidate in combinations(activities, count))),
        default=0,
    )


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
