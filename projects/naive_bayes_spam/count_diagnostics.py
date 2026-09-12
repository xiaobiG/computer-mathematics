"""Small count-data diagnostics for checking, not proving, a Poisson model."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
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


def count_diagnostics_certificate(
    counts: list[int], report: CountDiagnostics, *, tolerance: float = 1e-12,
) -> dict[str, bool]:
    """Recompute a count diagnostic so displayed evidence cannot be hand-edited.

    This certifies arithmetic for a finite sample only. It deliberately does
    not turn a mean/variance match into a proof that observations are Poisson.
    """
    empty = {
        "mean_matches": False,
        "sample_variance_matches": False,
        "dispersion_ratio_matches": False,
        "zero_frequency_and_poisson_baseline_match": False,
        "valid": False,
    }
    try:
        if tolerance <= 0.0 or not isfinite(tolerance) or not isinstance(report, CountDiagnostics):
            return empty
        expected = count_diagnostics(counts)
        close = lambda observed, value: abs(observed - value) <= tolerance * max(1.0, abs(value))
        mean_matches = close(report.mean, expected.mean)
        variance_matches = close(report.sample_variance, expected.sample_variance)
        ratio_matches = close(report.variance_to_mean, expected.variance_to_mean)
        zero_matches = (close(report.zero_fraction, expected.zero_fraction)
                        and close(report.poisson_zero_fraction_at_mean, expected.poisson_zero_fraction_at_mean))
        return {
            "mean_matches": mean_matches,
            "sample_variance_matches": variance_matches,
            "dispersion_ratio_matches": ratio_matches,
            "zero_frequency_and_poisson_baseline_match": zero_matches,
            "valid": mean_matches and variance_matches and ratio_matches and zero_matches,
        }
    except (TypeError, ValueError):
        return empty
