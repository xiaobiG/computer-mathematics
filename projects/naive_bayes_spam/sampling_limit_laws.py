"""Reproducible diagnostics for sample-mean concentration and normal approximation."""

from __future__ import annotations

from math import isfinite, sqrt
from random import Random


def _validate(probability: float, sample_size: int, trials: int) -> None:
    if not isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError("probability must be finite and strictly between zero and one")
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 1 for value in (sample_size, trials)):
        raise ValueError("sample_size and trials must be integers greater than one")


def bernoulli_mean_report(
    probability: float, sample_size: int, trials: int = 3000, seed: int = 0,
) -> dict[str, float | int | dict[str, bool]]:
    """Simulate repeated Bernoulli sample means and compare their known scale.

    This is an empirical, seeded diagnostic.  It illustrates consequences of
    the LLN/CLT; it neither proves them nor licenses a normal approximation
    for arbitrary distributions or dependent samples.
    """
    _validate(probability, sample_size, trials)
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    rng = Random(seed)
    means = [sum(rng.random() < probability for _ in range(sample_size)) / sample_size for _ in range(trials)]
    empirical_mean = sum(means) / trials
    empirical_standard_error = sqrt(sum((mean - empirical_mean) ** 2 for mean in means) / (trials - 1))
    theoretical_standard_error = sqrt(probability * (1.0 - probability) / sample_size)
    interval_coverage = sum(
        abs(mean - probability) <= 1.96 * theoretical_standard_error for mean in means
    ) / trials
    relative_se_error = abs(empirical_standard_error - theoretical_standard_error) / theoretical_standard_error
    return {
        "probability": probability,
        "sample_size": sample_size,
        "trials": trials,
        "empirical_mean": empirical_mean,
        "empirical_standard_error": empirical_standard_error,
        "theoretical_standard_error": theoretical_standard_error,
        "normal_interval_coverage": interval_coverage,
        "certificate": {
            "mean_is_close_on_repeated_trials": abs(empirical_mean - probability) <= 5 * theoretical_standard_error / sqrt(trials),
            "empirical_standard_error_matches_theory": relative_se_error <= 0.15,
            "normal_coverage_is_plausible_for_this_bernoulli_setting": 0.90 <= interval_coverage <= 0.99,
        },
    }


def sample_size_scaling_report(
    probability: float, small_sample_size: int, large_sample_size: int, trials: int = 3000, seed: int = 0,
) -> dict[str, object]:
    """Compare two sample sizes against the 1/sqrt(n) standard-error law."""
    _validate(probability, small_sample_size, trials)
    _validate(probability, large_sample_size, trials)
    if large_sample_size <= small_sample_size:
        raise ValueError("large_sample_size must exceed small_sample_size")
    small = bernoulli_mean_report(probability, small_sample_size, trials, seed)
    large = bernoulli_mean_report(probability, large_sample_size, trials, seed + 1)
    observed_ratio = small["empirical_standard_error"] / large["empirical_standard_error"]
    expected_ratio = sqrt(large_sample_size / small_sample_size)
    return {
        "small": small,
        "large": large,
        "observed_standard_error_ratio": observed_ratio,
        "expected_standard_error_ratio": expected_ratio,
        "certificate": {
            "larger_sample_has_smaller_empirical_standard_error": observed_ratio > 1.0,
            "observed_ratio_matches_inverse_sqrt_scaling": abs(observed_ratio / expected_ratio - 1.0) <= 0.20,
        },
    }
