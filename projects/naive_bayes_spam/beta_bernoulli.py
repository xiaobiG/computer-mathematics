"""Beta–Bernoulli 共轭更新的可审计教学实现。"""

from __future__ import annotations

from math import exp, isclose, isfinite, lgamma


BETA_BINOMIAL_PREDICTIVE_CONTRACT = "beta-binomial-posterior-predictive/v1"


def _validate_prior(alpha: float, beta: float) -> None:
    if (not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not isfinite(alpha)
            or not isinstance(beta, (int, float)) or isinstance(beta, bool) or not isfinite(beta)
            or alpha <= 0 or beta <= 0):
        raise ValueError("alpha and beta must be finite positive numbers")


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


def beta_binomial_predictive_report(
    observations: list[int], future_trials: int, alpha: float = 1.0, beta: float = 1.0,
) -> dict[str, object]:
    """Predict a future success *count* while retaining parameter uncertainty.

    Conditional on ``p``, future trials are Bernoulli.  Marginalising the
    posterior Beta distribution instead yields the Beta--Binomial law, whose
    variance is larger than the plug-in Binomial variance unless the posterior
    is infinitely concentrated.
    """
    report = beta_binomial_predictive_report_no_certificate(observations, future_trials, alpha, beta)
    report["certificate"] = beta_binomial_predictive_certificate(observations, future_trials, alpha, beta, report)
    return report


def beta_binomial_predictive_certificate(
    observations: list[int], future_trials: int, alpha: float, beta: float, report: dict[str, object],
) -> dict[str, bool]:
    """Recompute the finite predictive mass and moment identities."""
    empty = {
        "posterior_matches_observations": False,
        "probabilities_sum_to_one": False,
        "probabilities_match_beta_binomial": False,
        "moments_match_beta_binomial": False,
        "variance_exceeds_plugin_binomial": False,
        "valid": False,
    }
    if not isinstance(report, dict) or report.get("contract") != BETA_BINOMIAL_PREDICTIVE_CONTRACT:
        return empty
    try:
        expected = beta_binomial_predictive_report_no_certificate(observations, future_trials, alpha, beta)
    except (TypeError, ValueError):
        return empty
    probabilities = report.get("success_count_probabilities")
    if not isinstance(probabilities, tuple) or len(probabilities) != future_trials + 1:
        return empty
    input_matches = (
        report.get("prior") == expected["prior"]
        and report.get("observations") == expected["observations"]
        and report.get("future_trials") == expected["future_trials"]
    )
    posterior_matches = input_matches and report.get("posterior") == expected["posterior"]
    probabilities_match = all(
        isclose(actual, wanted, rel_tol=0.0, abs_tol=1e-15)
        for actual, wanted in zip(probabilities, expected["success_count_probabilities"])
    )
    sums_to_one = isclose(sum(probabilities), 1.0, rel_tol=0.0, abs_tol=1e-12)
    moments_match = all(
        isinstance(report.get(field), (int, float)) and isclose(
            report[field], expected[field], rel_tol=0.0, abs_tol=1e-12,
        )
        for field in ("predictive_mean", "predictive_variance", "plugin_binomial_variance", "variance_increase_from_parameter_uncertainty")
    )
    variance_exceeds = expected["predictive_variance"] >= expected["plugin_binomial_variance"]
    return {
        "posterior_matches_observations": posterior_matches,
        "probabilities_sum_to_one": sums_to_one,
        "probabilities_match_beta_binomial": probabilities_match,
        "moments_match_beta_binomial": moments_match,
        "variance_exceeds_plugin_binomial": variance_exceeds,
        "valid": posterior_matches and sums_to_one and probabilities_match and moments_match and variance_exceeds,
    }


def beta_binomial_predictive_report_no_certificate(
    observations: list[int], future_trials: int, alpha: float, beta: float,
) -> dict[str, object]:
    """Build the deterministic report fields used by the self-contained certificate."""
    if (not isinstance(future_trials, int) or isinstance(future_trials, bool) or future_trials < 0):
        raise ValueError("future_trials must be a non-negative integer")
    updated_alpha, updated_beta = posterior_parameters(observations, alpha, beta)
    total = updated_alpha + updated_beta
    log_beta_denominator = lgamma(updated_alpha) + lgamma(updated_beta) - lgamma(total)
    probabilities = tuple(
        exp(lgamma(future_trials + 1) - lgamma(successes + 1) - lgamma(future_trials - successes + 1)
            + lgamma(updated_alpha + successes) + lgamma(updated_beta + future_trials - successes)
            - lgamma(total + future_trials) - log_beta_denominator)
        for successes in range(future_trials + 1)
    )
    predictive_mean = future_trials * updated_alpha / total
    predictive_variance = future_trials * updated_alpha * updated_beta * (total + future_trials) / (total * total * (total + 1.0))
    plugin_binomial_variance = future_trials * updated_alpha / total * updated_beta / total
    return {
        "contract": BETA_BINOMIAL_PREDICTIVE_CONTRACT, "prior": (alpha, beta), "observations": tuple(observations),
        "posterior": (updated_alpha, updated_beta), "future_trials": future_trials,
        "success_count_probabilities": probabilities, "predictive_mean": predictive_mean,
        "predictive_variance": predictive_variance, "plugin_binomial_variance": plugin_binomial_variance,
        "variance_increase_from_parameter_uncertainty": predictive_variance - plugin_binomial_variance,
    }


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
