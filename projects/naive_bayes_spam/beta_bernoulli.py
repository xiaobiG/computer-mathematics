"""Beta–Bernoulli 共轭更新的可审计教学实现。"""

from __future__ import annotations

from math import isclose


def _validate_prior(alpha: float, beta: float) -> None:
    if alpha <= 0 or beta <= 0:
        raise ValueError("alpha and beta must be positive")


def posterior_parameters(observations: list[int], alpha: float = 1.0, beta: float = 1.0) -> tuple[float, float]:
    """Return Beta(alpha + successes, beta + failures)."""
    _validate_prior(alpha, beta)
    if any(value not in (0, 1) for value in observations):
        raise ValueError("observations must contain only zeros and ones")
    successes = sum(observations)
    return alpha + successes, beta + len(observations) - successes


def posterior_predictive_success(observations: list[int], alpha: float = 1.0, beta: float = 1.0) -> float:
    """Return P(next observation = 1 | data), the posterior mean."""
    updated_alpha, updated_beta = posterior_parameters(observations, alpha, beta)
    return updated_alpha / (updated_alpha + updated_beta)


def map_estimate(observations: list[int], alpha: float = 2.0, beta: float = 2.0) -> float:
    """Return the interior Beta posterior mode; reject priors without one."""
    updated_alpha, updated_beta = posterior_parameters(observations, alpha, beta)
    if updated_alpha <= 1 or updated_beta <= 1:
        raise ValueError("posterior has no interior MAP estimate")
    return (updated_alpha - 1) / (updated_alpha + updated_beta - 2)


def beta_bernoulli_report(
    observations: list[int], alpha: float = 1.0, beta: float = 1.0
) -> dict[str, object]:
    """Return a teaching report for one Beta--Bernoulli update.

    ``interior_map`` is deliberately ``None`` when the posterior mode is at
    an endpoint.  This keeps "no interior stationary point" distinct from a
    numerical failure or from the posterior predictive probability.
    """
    updated_alpha, updated_beta = posterior_parameters(observations, alpha, beta)
    predictive = updated_alpha / (updated_alpha + updated_beta)
    interior_map = None
    if updated_alpha > 1 and updated_beta > 1:
        interior_map = (updated_alpha - 1) / (updated_alpha + updated_beta - 2)

    report: dict[str, object] = {
        "prior": (alpha, beta),
        "successes": sum(observations),
        "failures": len(observations) - sum(observations),
        "posterior": (updated_alpha, updated_beta),
        "posterior_predictive_success": predictive,
        "interior_map": interior_map,
    }
    report["certificate"] = beta_bernoulli_certificate(observations, alpha, beta, report)
    return report


def beta_bernoulli_certificate(
    observations: list[int], alpha: float, beta: float, report: dict[str, object]
) -> dict[str, bool]:
    """Independently recompute the finite update and audit a supplied report."""
    _validate_prior(alpha, beta)
    if any(value not in (0, 1) for value in observations):
        raise ValueError("observations must contain only zeros and ones")

    successes = sum(observations)
    failures = len(observations) - successes
    expected_posterior = (alpha + successes, beta + failures)
    expected_predictive = expected_posterior[0] / sum(expected_posterior)
    has_interior_map = expected_posterior[0] > 1 and expected_posterior[1] > 1
    expected_map = None
    if has_interior_map:
        expected_map = (expected_posterior[0] - 1) / (sum(expected_posterior) - 2)

    reported_posterior = report.get("posterior")
    reported_predictive = report.get("posterior_predictive_success")
    reported_map = report.get("interior_map")
    counts_match = report.get("successes") == successes and report.get("failures") == failures
    posterior_matches_counts = reported_posterior == expected_posterior
    predictive_matches_posterior = isinstance(reported_predictive, (int, float)) and isclose(
        reported_predictive, expected_predictive, rel_tol=0.0, abs_tol=1e-15
    )
    map_matches_posterior = (
        isinstance(reported_map, (int, float))
        and expected_map is not None
        and isclose(reported_map, expected_map, rel_tol=0.0, abs_tol=1e-15)
    ) or (reported_map is None and expected_map is None)
    return {
        "counts_match_observations": counts_match,
        "posterior_matches_counts": posterior_matches_counts,
        "predictive_matches_posterior": predictive_matches_posterior,
        "map_boundary_is_explicit": map_matches_posterior,
        "valid": counts_match
        and posterior_matches_counts
        and predictive_matches_posterior
        and map_matches_posterior,
    }
