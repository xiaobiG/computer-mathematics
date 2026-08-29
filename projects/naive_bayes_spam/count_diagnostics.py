"""Small count-data diagnostics for checking, not proving, a Poisson model."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from statistics import fmean


@dataclass(frozen=True)
class CountDiagnostics:
    mean: float
    sample_variance: float
    variance_to_mean: float
    zero_fraction: float
    poisson_zero_fraction_at_mean: float


def count_diagnostics(counts: list[int]) -> CountDiagnostics:
    """Report inexpensive Poisson-model diagnostics for nonnegative integer counts."""
    if len(counts) < 2 or any(type(value) is not int or value < 0 for value in counts):
        raise ValueError("counts must contain at least two nonnegative integers")
    mean = fmean(counts)
    variance = sum((value - mean) ** 2 for value in counts) / (len(counts) - 1)
    return CountDiagnostics(
        mean=mean,
        sample_variance=variance,
        variance_to_mean=variance / mean if mean else 0.0,
        zero_fraction=sum(value == 0 for value in counts) / len(counts),
        poisson_zero_fraction_at_mean=exp(-mean),
    )
