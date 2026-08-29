"""Bernoulli MLE/MAP primitives used by the probability lessons."""

from __future__ import annotations

from math import inf, log


def _validate_observations(observations: list[int]) -> None:
    if not observations or any(value not in (0, 1) for value in observations):
        raise ValueError("observations must be a nonempty list of zeros and ones")


def bernoulli_mle(observations: list[int]) -> float:
    """Return the Bernoulli maximum-likelihood estimate: sample mean."""
    _validate_observations(observations)
    return sum(observations) / len(observations)


def bernoulli_log_likelihood(observations: list[int], probability: float) -> float:
    """Return log P(data | p), including mathematically valid endpoint cases."""
    _validate_observations(observations)
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    successes = sum(observations)
    failures = len(observations) - successes
    if probability == 0.0:
        return 0.0 if successes == 0 else -inf
    if probability == 1.0:
        return 0.0 if failures == 0 else -inf
    return successes * log(probability) + failures * log(1.0 - probability)


def bernoulli_map(observations: list[int], alpha: float, beta: float) -> float:
    """Return the interior Beta(alpha, beta) posterior mode for Bernoulli data."""
    _validate_observations(observations)
    if alpha <= 0 or beta <= 0:
        raise ValueError("alpha and beta must be positive")
    successes = sum(observations)
    updated_alpha, updated_beta = alpha + successes, beta + len(observations) - successes
    if updated_alpha <= 1 or updated_beta <= 1:
        raise ValueError("posterior mode is on a boundary; no unique interior MAP")
    return (updated_alpha - 1) / (updated_alpha + updated_beta - 2)
