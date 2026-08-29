"""Beta–Bernoulli 共轭更新的可审计教学实现。"""

from __future__ import annotations


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
