"""Replay coverage loss when a correlated AR(1) series is treated as i.i.d."""

from __future__ import annotations

from math import isfinite, sqrt
from random import Random


CONTRACT = "stationary-ar1-mean-interval-coverage/v1"


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _positive_integer(value: object, name: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")
    return value


def _exact_mean_variance(phi: float, innovation_variance: float, length: int) -> float:
    marginal_variance = innovation_variance / (1 - phi ** 2)
    paired_covariances = sum((length - lag) * (phi ** lag) for lag in range(1, length))
    return marginal_variance * (length + 2 * paired_covariances) / (length ** 2)


def ar1_mean_interval_coverage_report(
    phi: object,
    innovation_variance: object,
    window_length: object,
    replications: object = 2000,
    seed: object = 0,
    z_value: object = 1.96,
) -> dict[str, object]:
    """Compare known-variance 95% intervals under a declared stationary AR(1).

    The report is a deterministic simulation audit, not a data-fitting method.
    Its naive interval deliberately uses the correct marginal variance but drops
    every lag covariance; the exact interval retains all finite-window lags.
    """
    ar = _finite_number(phi, "phi")
    if not -1 < ar < 1:
        raise ValueError("phi must be strictly between -1 and 1 for stationarity")
    innovation = _finite_number(innovation_variance, "innovation_variance")
    if innovation <= 0:
        raise ValueError("innovation_variance must be positive")
    length = _positive_integer(window_length, "window_length", 2)
    repeats = _positive_integer(replications, "replications", 200)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    z = _finite_number(z_value, "z_value")
    if z <= 0:
        raise ValueError("z_value must be positive")

    marginal_variance = innovation / (1 - ar ** 2)
    exact_variance = _exact_mean_variance(ar, innovation, length)
    iid_variance = marginal_variance / length
    long_run_variance = marginal_variance * (1 + ar) / (1 - ar)
    rng = Random(seed)
    naive_hits = exact_hits = 0
    for _ in range(repeats):
        state = rng.gauss(0.0, sqrt(marginal_variance))
        total = state
        for _ in range(1, length):
            state = ar * state + rng.gauss(0.0, sqrt(innovation))
            total += state
        mean = total / length
        naive_hits += abs(mean) <= z * sqrt(iid_variance)
        exact_hits += abs(mean) <= z * sqrt(exact_variance)

    naive_coverage = naive_hits / repeats
    exact_coverage = exact_hits / repeats
    return {
        "contract": CONTRACT,
        "declared_model": {
            "type": "stationary_ar1", "phi": ar,
            "innovation_variance": innovation, "stationary_mean": 0.0,
        },
        "window_length": length,
        "replications": repeats,
        "seed": seed,
        "z_value": z,
        "marginal_variance": marginal_variance,
        "exact_finite_window_mean_variance": exact_variance,
        "naive_iid_same_marginal_mean_variance": iid_variance,
        "asymptotic_long_run_variance": long_run_variance,
        "effective_independent_sample_size": marginal_variance / exact_variance,
        "naive_iid_interval_coverage": naive_coverage,
        "exact_finite_window_interval_coverage": exact_coverage,
        "coverage_gap_exact_minus_naive": exact_coverage - naive_coverage,
        "interpretation": "known_variance_interval_coverage_under_declared_stationary_ar1",
        "boundary": (
            "does not estimate autocorrelation or long-run variance from data, establish stationarity, "
            "choose a HAC bandwidth, or justify a real-world time-series model"
        ),
    }


def ar1_mean_interval_coverage_certificate(
    phi: object, innovation_variance: object, window_length: object, replications: object,
    seed: object, z_value: object, report: object,
) -> bool:
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        expected = ar1_mean_interval_coverage_report(
            phi, innovation_variance, window_length, replications, seed, z_value,
        )
    except (TypeError, ValueError):
        return False
    return report == expected
