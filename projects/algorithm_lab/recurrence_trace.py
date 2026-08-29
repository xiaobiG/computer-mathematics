"""Audit recursion-tree work for binary search and merge sort teaching examples."""

from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import TypeVar


Item = TypeVar("Item")


@dataclass(frozen=True)
class MergeLevel:
    """The merge work contributed by one recursion-tree depth."""

    depth: int
    subproblems: int
    items_per_subproblem: int
    total_merge_items: int


def binary_search_worst_case_steps(size: int) -> int:
    """Count interval halvings until an empty/singleton search interval remains."""
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise ValueError("size must be a positive integer")
    steps = 0
    while size > 1:
        size = (size + 1) // 2
        steps += 1
    return steps


def merge_sort_levels(size: int) -> list[MergeLevel]:
    """Return a power-of-two merge-sort recursion-tree certificate.

    At each internal depth, all subproblems together contain ``size`` items,
    so merging that level has linear aggregate work.  Restricting this helper
    to powers of two keeps the level identity exact and visible.
    """
    if not isinstance(size, int) or isinstance(size, bool) or size < 1 or size & (size - 1):
        raise ValueError("size must be a positive power of two")
    levels = []
    for depth in range(int(log2(size))):
        subproblems = 2 ** depth
        items_per_subproblem = size // subproblems
        levels.append(MergeLevel(depth, subproblems, items_per_subproblem, size))
    return levels


def merge_sort_with_comparisons(values: list[Item]) -> tuple[list[Item], int]:
    """Sort a tiny list and count element comparisons used by merge operations."""
    if not isinstance(values, list):
        raise ValueError("values must be a list")

    def sort(items: list[Item]) -> tuple[list[Item], int]:
        if len(items) <= 1:
            return items, 0
        middle = len(items) // 2
        left, left_comparisons = sort(items[:middle])
        right, right_comparisons = sort(items[middle:])
        merged: list[Item] = []
        left_index = right_index = comparisons = 0
        while left_index < len(left) and right_index < len(right):
            comparisons += 1
            if left[left_index] <= right[right_index]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1
        merged.extend(left[left_index:])
        merged.extend(right[right_index:])
        return merged, left_comparisons + right_comparisons + comparisons

    return sort(values.copy())
