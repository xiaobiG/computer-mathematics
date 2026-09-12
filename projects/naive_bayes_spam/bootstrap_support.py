"""Metric-neutral primitives shared by teaching bootstrap reports.

Sampling-unit semantics remain owned by each report module; these helpers only
validate common controls and reproduce the repository's percentile convention.
"""

from __future__ import annotations


def require_integer(value: object, field: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field} must be an integer at least {minimum}")
    return value


def percentile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if isinstance(probability, bool) or not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
        raise ValueError("probability must be in [0, 1]")
    return sorted(values)[round((len(values) - 1) * probability)]
