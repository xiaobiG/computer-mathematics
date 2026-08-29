"""Entropy, cross-entropy and KL divergence for finite teaching distributions."""

from __future__ import annotations

from math import inf, isclose, isfinite, log
from typing import Hashable


Outcome = Hashable
Distribution = dict[Outcome, float]


def _validate(distribution: Distribution, name: str) -> None:
    if not isinstance(distribution, dict) or not distribution:
        raise ValueError(f"{name} must be a non-empty dictionary")
    for probability in distribution.values():
        if (not isinstance(probability, (int, float)) or isinstance(probability, bool)
                or not isfinite(probability) or probability < 0.0):
            raise ValueError(f"{name} probabilities must be finite and non-negative")
    if not isclose(sum(distribution.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{name} probabilities must sum to one")


def _validate_pair(actual: Distribution, predicted: Distribution) -> None:
    _validate(actual, "actual")
    _validate(predicted, "predicted")
    if actual.keys() != predicted.keys():
        raise ValueError("actual and predicted distributions must share the same outcomes")


def entropy(distribution: Distribution) -> float:
    """Return H(P) in nats, treating 0 log 0 as its limiting value zero."""
    _validate(distribution, "distribution")
    return -sum(probability * log(probability) for probability in distribution.values() if probability > 0.0)


def cross_entropy(actual: Distribution, predicted: Distribution) -> float:
    """Return H(P, Q); a positive actual event assigned Q=0 has infinite loss."""
    _validate_pair(actual, predicted)
    if any(actual[outcome] > 0.0 and predicted[outcome] == 0.0 for outcome in actual):
        return inf
    return -sum(actual[outcome] * log(predicted[outcome])
                for outcome in actual if actual[outcome] > 0.0)


def kl_divergence(actual: Distribution, predicted: Distribution) -> float:
    """Return D_KL(P || Q), including its mathematically meaningful infinity case."""
    _validate_pair(actual, predicted)
    if any(actual[outcome] > 0.0 and predicted[outcome] == 0.0 for outcome in actual):
        return inf
    return sum(actual[outcome] * log(actual[outcome] / predicted[outcome])
               for outcome in actual if actual[outcome] > 0.0)


def information_report(actual: Distribution, predicted: Distribution) -> dict[str, float]:
    """Return the entropy decomposition used to audit a predicted distribution."""
    actual_entropy = entropy(actual)
    divergence = kl_divergence(actual, predicted)
    return {
        "entropy": actual_entropy,
        "cross_entropy": cross_entropy(actual, predicted),
        "kl_divergence": divergence,
        "decomposition_residual": (cross_entropy(actual, predicted) - actual_entropy - divergence
                                   if isfinite(divergence) else 0.0),
    }
