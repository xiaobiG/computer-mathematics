"""Auditable binary search over a sorted integer sequence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BinarySearchStep:
    """One iteration, including the half-open interval before and after it."""

    left: int
    right: int
    middle: int
    relation: str
    next_left: int
    next_right: int


@dataclass(frozen=True)
class LowerBoundStep:
    """One interval reduction while locating the first value >= target."""

    left: int
    right: int
    middle: int
    relation: str
    next_left: int
    next_right: int


def _require_sorted(values: list[int]) -> None:
    if any(left > right for left, right in zip(values, values[1:])):
        raise ValueError("binary search requires nondecreasing values")


def binary_search_trace(values: list[int], target: int) -> tuple[int, list[BinarySearchStep]]:
    """Return an occurrence of target (or -1) together with its interval trace."""
    _require_sorted(values)
    left, right = 0, len(values)
    steps: list[BinarySearchStep] = []
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] == target:
            steps.append(BinarySearchStep(left, right, middle, "equal", left, right))
            return middle, steps
        if values[middle] < target:
            next_left, next_right, relation = middle + 1, right, "less"
        else:
            next_left, next_right, relation = left, middle, "greater"
        steps.append(BinarySearchStep(left, right, middle, relation, next_left, next_right))
        left, right = next_left, next_right
    return -1, steps


def lower_bound_trace(values: list[int], target: int) -> tuple[int, list[LowerBoundStep]]:
    """Return the insertion point before the first value not smaller than target.

    The returned index is in ``[0, len(values)]``.  It therefore represents a
    valid insertion point even when the target is absent or larger than every
    element, unlike an ordinary successful-search index.
    """
    _require_sorted(values)
    left, right = 0, len(values)
    steps: list[LowerBoundStep] = []
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] < target:
            next_left, next_right, relation = middle + 1, right, "less"
        else:
            next_left, next_right, relation = left, middle, "not_less"
        steps.append(LowerBoundStep(left, right, middle, relation, next_left, next_right))
        left, right = next_left, next_right
    return left, steps


def trace_respects_invariant(values: list[int], target: int, result: int, steps: list[BinarySearchStep]) -> bool:
    """Check the candidate-interval invariant and strict progress of a trace."""
    _require_sorted(values)
    left, right = 0, len(values)
    target_exists = target in values
    for step in steps:
        if (step.left, step.right) != (left, right) or not left <= step.middle < right:
            return False
        if target_exists and target not in values[left:right]:
            return False
        if step.relation == "equal":
            return (step.middle == result and values[step.middle] == target
                    and (step.next_left, step.next_right) == (left, right))
        if step.relation == "less":
            expected = (step.middle + 1, right)
        elif step.relation == "greater":
            expected = (left, step.middle)
        else:
            return False
        if (step.next_left, step.next_right) != expected or step.next_right - step.next_left >= right - left:
            return False
        left, right = expected
    return result == -1 and left == right and not target_exists


def lower_bound_trace_respects_invariant(
    values: list[int], target: int, result: int, steps: list[LowerBoundStep]
) -> bool:
    """Replay the boundary invariant instead of trusting the returned index."""
    _require_sorted(values)
    left, right = 0, len(values)
    for step in steps:
        if (step.left, step.right) != (left, right) or not left <= step.middle < right:
            return False
        if any(value >= target for value in values[:left]):
            return False
        if any(value < target for value in values[right:]):
            return False
        if step.relation == "less":
            expected = (step.middle + 1, right)
        elif step.relation == "not_less":
            expected = (left, step.middle)
        else:
            return False
        if (step.next_left, step.next_right) != expected or step.next_right - step.next_left >= right - left:
            return False
        left, right = expected
    return result == left == right and all(value < target for value in values[:result]) and all(
        value >= target for value in values[result:]
    )
