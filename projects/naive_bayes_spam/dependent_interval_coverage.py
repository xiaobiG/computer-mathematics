"""Replay coverage loss when a correlated AR(1) series is treated as i.i.d."""

from __future__ import annotations

from math import isfinite, sqrt
from random import Random


CONTRACT = "stationary-ar1-mean-interval-coverage/v1"
HAC_CONTRACT = "stationary-ar1-bartlett-hac-interval-coverage/v1"


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


def _stationary_ar1_draw(rng: Random, phi: float, innovation_variance: float, length: int) -> list[float]:
    marginal_variance = innovation_variance / (1 - phi ** 2)
    values = [rng.gauss(0.0, sqrt(marginal_variance))]
    for _ in range(1, length):
        values.append(phi * values[-1] + rng.gauss(0.0, sqrt(innovation_variance)))
    return values


def _sample_variance(values: list[float]) -> float:
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _bartlett_hac_long_run_variance(values: list[float], bandwidth: int) -> float:
    """Use the declared Bartlett window and the usual 1/n autocovariance scale."""
    mean = sum(values) / len(values)
    centered = [value - mean for value in values]
    length = len(values)
    estimate = sum(value ** 2 for value in centered) / length
    for lag in range(1, bandwidth + 1):
        autocovariance = sum(centered[index] * centered[index - lag] for index in range(lag, length)) / length
        estimate += 2 * (1 - lag / (bandwidth + 1)) * autocovariance
    return estimate


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


def ar1_bartlett_hac_interval_coverage_report(
    phi: object, innovation_variance: object, window_length: object, bandwidth: object,
    replications: object = 2000, seed: object = 0, z_value: object = 1.96,
) -> dict[str, object]:
    """Replay data-estimated naive, HAC, and oracle intervals under stationary AR(1).

    The bandwidth is deliberately an input rather than a hidden data-dependent
    choice.  A nonpositive HAC estimate is reported and rejected as an interval
    rather than silently replaced by a positive number.
    """
    ar = _finite_number(phi, "phi")
    if not -1 < ar < 1:
        raise ValueError("phi must be strictly between -1 and 1 for stationarity")
    innovation = _finite_number(innovation_variance, "innovation_variance")
    if innovation <= 0:
        raise ValueError("innovation_variance must be positive")
    length = _positive_integer(window_length, "window_length", 3)
    width = _positive_integer(bandwidth, "bandwidth", 0)
    if width >= length:
        raise ValueError("bandwidth must be smaller than window_length")
    repeats = _positive_integer(replications, "replications", 200)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    z = _finite_number(z_value, "z_value")
    if z <= 0:
        raise ValueError("z_value must be positive")

    exact_variance = _exact_mean_variance(ar, innovation, length)
    rng = Random(seed)
    naive_hits = hac_hits = oracle_hits = 0
    nonpositive_hac = 0
    hac_estimates = []
    for _ in range(repeats):
        values = _stationary_ar1_draw(rng, ar, innovation, length)
        mean = sum(values) / length
        naive_variance = _sample_variance(values) / length
        hac_long_run_variance = _bartlett_hac_long_run_variance(values, width)
        hac_estimates.append(hac_long_run_variance)
        naive_hits += abs(mean) <= z * sqrt(naive_variance)
        oracle_hits += abs(mean) <= z * sqrt(exact_variance)
        if hac_long_run_variance > 0:
            hac_hits += abs(mean) <= z * sqrt(hac_long_run_variance / length)
        else:
            nonpositive_hac += 1

    return {
        "contract": HAC_CONTRACT,
        "declared_model": {
            "type": "stationary_ar1", "phi": ar,
            "innovation_variance": innovation, "stationary_mean": 0.0,
        },
        "window_length": length,
        "bartlett_bandwidth": width,
        "replications": repeats,
        "seed": seed,
        "z_value": z,
        "oracle_exact_mean_variance": exact_variance,
        "naive_sample_variance_interval_coverage": naive_hits / repeats,
        "bartlett_hac_interval_coverage": hac_hits / repeats,
        "oracle_exact_interval_coverage": oracle_hits / repeats,
        "nonpositive_bartlett_estimate_count": nonpositive_hac,
        "mean_bartlett_long_run_variance": sum(hac_estimates) / repeats,
        "coverage_gain_hac_minus_naive": (hac_hits - naive_hits) / repeats,
        "interpretation": "data_estimated_bartlett_hac_interval_coverage_under_declared_stationary_ar1",
        "boundary": (
            "does not select a bandwidth, prove stationarity, handle heteroskedasticity, trends, breaks, clusters, "
            "or validate a HAC approximation for a real data-generating process"
        ),
    }


def ar1_bartlett_hac_interval_coverage_certificate(
    phi: object, innovation_variance: object, window_length: object, bandwidth: object,
    replications: object, seed: object, z_value: object, report: object,
) -> bool:
    if not isinstance(report, dict) or report.get("contract") != HAC_CONTRACT:
        return False
    try:
        expected = ar1_bartlett_hac_interval_coverage_report(
            phi, innovation_variance, window_length, bandwidth, replications, seed, z_value,
        )
    except (TypeError, ValueError):
        return False
    return report == expected
