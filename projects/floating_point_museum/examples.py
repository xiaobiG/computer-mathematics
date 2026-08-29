"""可复现的浮点数错误案例及其较稳定的改写。"""

from __future__ import annotations

from math import sqrt
from typing import Iterable


def nearly_equal(left: float, right: float, tolerance: float = 1e-12) -> bool:
    """结合相对与绝对尺度的近似比较。"""
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def kahan_sum(values: Iterable[float]) -> float:
    """使用补偿变量降低连续相加带来的累计舍入误差。"""
    total = 0.0
    compensation = 0.0
    for value in values:
        corrected = value - compensation
        next_total = total + corrected
        compensation = (next_total - total) - corrected
        total = next_total
    return total


def naive_sum(values: Iterable[float]) -> float:
    """明确的从左到右逐项累加，用于展示累计误差。"""
    total = 0.0
    for value in values:
        total += value
    return total


def pairwise_sum(values: Iterable[float]) -> float:
    """Sum a fixed balanced tree without allocating recursive slices."""
    items = list(values)

    def total_between(start: int, end: int) -> float:
        if start == end:
            return 0.0
        if end - start == 1:
            return items[start]
        middle = start + (end - start) // 2
        return total_between(start, middle) + total_between(middle, end)

    return total_between(0, len(items))


def naive_root_difference(x: float) -> float:
    return sqrt(x + 1.0) - sqrt(x)


def stable_root_difference(x: float) -> float:
    """有理化：sqrt(x + 1) - sqrt(x) = 1 / (sqrt(x + 1) + sqrt(x))。"""
    return 1.0 / (sqrt(x + 1.0) + sqrt(x))


if __name__ == "__main__":
    values = [1e16, 1.0, 1.0, -1e16]
    print(f"0.1 + 0.2 == 0.3: {0.1 + 0.2 == 0.3}")
    print(f"接近比较: {nearly_equal(0.1 + 0.2, 0.3)}")
    print(f"朴素逐项求和: {naive_sum(values)}")
    print(f"Kahan 求和: {kahan_sum(values)}")
    print(f"Pairwise 求和: {pairwise_sum(values)}")
    x = 1e16
    print(f"直接相减: {naive_root_difference(x)}")
    print(f"有理化后: {stable_root_difference(x)}")
