"""Finite-distribution moments and total-variance certificates for lessons."""

from __future__ import annotations

from math import isclose, isfinite
from typing import Hashable


def _validate_distribution(distribution: dict[float, float], name: str) -> None:
    if not isinstance(distribution, dict) or not distribution:
        raise ValueError(f"{name} must be a non-empty outcome-probability dictionary")
    for outcome, probability in distribution.items():
        if (not isinstance(outcome, (int, float)) or isinstance(outcome, bool) or not isfinite(outcome)
                or not isinstance(probability, (int, float)) or isinstance(probability, bool)
                or not isfinite(probability) or probability < 0.0):
            raise ValueError(f"{name} outcomes must be finite and probabilities non-negative")
    if not isclose(sum(distribution.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{name} probabilities must sum to one")


def finite_expectation(distribution: dict[float, float]) -> float:
    """Return E[X] for a finite numeric distribution."""
    _validate_distribution(distribution, "distribution")
    return sum(outcome * probability for outcome, probability in distribution.items())


def finite_variance(distribution: dict[float, float]) -> float:
    """Return population variance E[(X-E[X])^2] for a finite distribution."""
    mean = finite_expectation(distribution)
    return sum((outcome - mean) ** 2 * probability for outcome, probability in distribution.items())


def welford_population(values: list[float]) -> tuple[float, float]:
    """Return sample mean and population variance with an online update."""
    if not isinstance(values, list) or not values or any(not isinstance(value, (int, float))
                                                         or isinstance(value, bool) or not isfinite(value)
                                                         for value in values):
        raise ValueError("values must be a non-empty finite numeric list")
    count = 0
    mean = 0.0
    squared_deviation_sum = 0.0
    for value in values:
        count += 1
        delta = value - mean
        mean += delta / count
        squared_deviation_sum += delta * (value - mean)
    return mean, squared_deviation_sum / count


def total_variance_report(
    group_probabilities: dict[Hashable, float], groups: dict[Hashable, dict[float, float]],
) -> dict[str, float]:
    """Certify Var(X)=E[Var(X|Y)]+Var(E[X|Y]) for finite groups."""
    if not isinstance(group_probabilities, dict) or not group_probabilities or group_probabilities.keys() != groups.keys():
        raise ValueError("groups and group probabilities must be non-empty and share keys")
    if any(not isinstance(probability, (int, float)) or isinstance(probability, bool)
           or not isfinite(probability) or probability < 0.0 for probability in group_probabilities.values()):
        raise ValueError("group probabilities must be finite and non-negative")
    if not isclose(sum(group_probabilities.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("group probabilities must sum to one")
    means = {group: finite_expectation(distribution) for group, distribution in groups.items()}
    within = sum(group_probabilities[group] * finite_variance(distribution)
                 for group, distribution in groups.items())
    overall_mean = sum(group_probabilities[group] * means[group] for group in groups)
    between = sum(group_probabilities[group] * (means[group] - overall_mean) ** 2 for group in groups)
    return {"overall_mean": overall_mean, "within_variance": within,
            "between_variance": between, "total_variance": within + between}
