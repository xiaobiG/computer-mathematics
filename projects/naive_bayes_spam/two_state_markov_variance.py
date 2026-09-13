"""Exact finite-window variance for a declared stationary two-state Markov chain."""

from __future__ import annotations

from math import isfinite


CONTRACT = "stationary-two-state-markov-mean-variance/v1"


def _probability(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not 0 < value < 1:
        raise ValueError(f"{name} must be a finite probability strictly between zero and one")
    return float(value)


def _positive_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def stationary_two_state_markov_mean_variance_report(
    p01: object, p10: object, window_length: object,
) -> dict[str, object]:
    """Return the exact variance under X_1 drawn from the stationary law.

    p01 and p10 are the 0->1 and 1->0 transition probabilities.  The binary
    autocorrelation is rho^k, where rho = 1 - p01 - p10.  No data fitting or
    convergence diagnosis is performed.
    """
    up, down = _probability(p01, "p01"), _probability(p10, "p10")
    length = _positive_integer(window_length, "window_length")
    stationary_success = up / (up + down)
    rho = 1 - up - down
    marginal_variance = stationary_success * (1 - stationary_success)
    covariance_terms = [
        {"lag": lag, "covariance": marginal_variance * (rho ** lag), "multiplicity": length - lag}
        for lag in range(1, length)
    ]
    numerator = length * marginal_variance + 2 * sum(
        row["multiplicity"] * row["covariance"] for row in covariance_terms
    )
    mean_variance = numerator / (length ** 2)
    iid_variance = marginal_variance / length
    effective_sample_size = marginal_variance / mean_variance
    return {
        "contract": CONTRACT,
        "declared_chain": {
            "states": [0, 1], "p01": up, "p10": down,
            "stationary_probability_of_one": stationary_success,
            "second_eigenvalue_rho": rho,
            "initial_distribution": "stationary",
        },
        "window_length": length,
        "marginal_variance": marginal_variance,
        "lag_covariances": covariance_terms,
        "mean_variance": mean_variance,
        "iid_same_marginal_variance": iid_variance,
        "variance_inflation_relative_to_iid": mean_variance / iid_variance,
        "effective_independent_sample_size": effective_sample_size,
        "interpretation": "exact_finite_window_variance_under_declared_stationary_two_state_chain",
        "boundary": (
            "does not fit a chain from observed logs, verify stationarity, establish mixing, handle non-binary outcomes, "
            "or replace block/cluster/time-series inference for real data"
        ),
    }


def stationary_two_state_markov_mean_variance_certificate(
    p01: object, p10: object, window_length: object, report: object,
) -> bool:
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        return report == stationary_two_state_markov_mean_variance_report(p01, p10, window_length)
    except (TypeError, ValueError):
        return False
