"""Turn calibrated binary probabilities into explicitly costed teaching choices."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class CostSensitiveDecision:
    """Expected losses for one probability forecast under one declared policy."""

    probability: float
    positive_threshold: float
    cost_if_positive: float
    cost_if_negative: float
    recommended_label: bool | None


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _policy(false_positive_cost: object, false_negative_cost: object) -> tuple[float, float, float]:
    false_positive_cost = _finite_number(false_positive_cost, "false_positive_cost")
    false_negative_cost = _finite_number(false_negative_cost, "false_negative_cost")
    if false_positive_cost <= 0.0 or false_negative_cost <= 0.0:
        raise ValueError("false-positive and false-negative costs must be positive")
    return (
        false_positive_cost,
        false_negative_cost,
        false_positive_cost / (false_positive_cost + false_negative_cost),
    )


def cost_sensitive_decision(
    probability: object, false_positive_cost: object, false_negative_cost: object,
) -> CostSensitiveDecision:
    """Compare the two expected action costs for a calibrated probability.

    A positive action costs ``false_positive_cost * (1 - p)`` in expectation;
    a negative action costs ``false_negative_cost * p``.  An exact tie remains
    undecided rather than silently becoming a threshold convention.

    This is a decision-theory teaching primitive, not an authorization to
    automate medical, financial, employment, or access-control outcomes.
    """
    probability = _finite_number(probability, "probability")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    false_positive_cost, false_negative_cost, threshold = _policy(false_positive_cost, false_negative_cost)
    cost_if_positive = false_positive_cost * (1.0 - probability)
    cost_if_negative = false_negative_cost * probability
    if cost_if_positive < cost_if_negative:
        recommendation: bool | None = True
    elif cost_if_positive > cost_if_negative:
        recommendation = False
    else:
        recommendation = None
    return CostSensitiveDecision(
        probability=probability,
        positive_threshold=threshold,
        cost_if_positive=cost_if_positive,
        cost_if_negative=cost_if_negative,
        recommended_label=recommendation,
    )


def cost_sensitive_decision_table(
    probabilities: Iterable[object], false_positive_cost: object, false_negative_cost: object,
) -> tuple[CostSensitiveDecision, ...]:
    """Apply one declared cost policy to a non-empty collection of forecasts."""
    probabilities = tuple(probabilities) if not isinstance(probabilities, (str, bytes)) else ()
    if not probabilities:
        raise ValueError("probabilities must be a non-empty iterable")
    return tuple(
        cost_sensitive_decision(probability, false_positive_cost, false_negative_cost)
        for probability in probabilities
    )
