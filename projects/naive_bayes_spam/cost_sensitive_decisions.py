"""Turn calibrated binary probabilities into explicitly costed teaching choices."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

from projects.naive_bayes_spam.recalibration import (
    PlattCalibrationReport,
    calibrated_probability_from_report,
)


@dataclass(frozen=True)
class CostSensitiveDecision:
    """Expected losses for one probability forecast under one declared policy."""

    probability: float
    positive_threshold: float
    cost_if_positive: float
    cost_if_negative: float
    recommended_label: bool | None


@dataclass(frozen=True)
class CalibratedCostSensitiveDecision:
    """A cost comparison bound to the calibration artifact that produced p."""

    raw_probability: float
    calibrated_probability: float
    validation_examples: int
    calibration_slope: float
    calibration_intercept: float
    decision: CostSensitiveDecision
    automatic_action: str


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


def calibrated_cost_sensitive_decision(
    raw_probability: object, calibration_report: object,
    false_positive_cost: object, false_negative_cost: object,
) -> CalibratedCostSensitiveDecision:
    """Apply a declared cost policy to a held-out score via verified calibration.

    This preserves the fitted validation artifact in the decision path instead
    of treating a manually copied calibrated number as self-authenticating.
    It remains a teaching calculation and always declines automatic action.
    """
    raw = _finite_number(raw_probability, "raw_probability")
    if not 0.0 <= raw <= 1.0:
        raise ValueError("raw_probability must lie in [0, 1]")
    if not isinstance(calibration_report, PlattCalibrationReport):
        raise ValueError("calibration_report must be a Platt calibration artifact")
    calibrated = calibrated_probability_from_report(calibration_report, raw)
    decision = cost_sensitive_decision(calibrated, false_positive_cost, false_negative_cost)
    return CalibratedCostSensitiveDecision(
        raw_probability=raw,
        calibrated_probability=calibrated,
        validation_examples=len(calibration_report.validation_labels),
        calibration_slope=calibration_report.slope,
        calibration_intercept=calibration_report.intercept,
        decision=decision,
        automatic_action="none",
    )


def calibrated_cost_sensitive_decision_certificate(
    raw_probability: object, calibration_report: object,
    false_positive_cost: object, false_negative_cost: object, decision: object,
) -> bool:
    """Rebuild a source-bound cost decision and reject altered recommendations."""
    if not isinstance(decision, CalibratedCostSensitiveDecision):
        return False
    try:
        expected = calibrated_cost_sensitive_decision(
            raw_probability, calibration_report, false_positive_cost, false_negative_cost,
        )
    except ValueError:
        return False
    return decision == expected
