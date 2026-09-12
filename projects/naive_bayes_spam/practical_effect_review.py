"""Carry a two-sample confidence interval into a non-automated practical-effect review."""

from __future__ import annotations

from math import isfinite, sqrt


INTERVAL_CONTRACT = "two-sample-mean-interval/v1"
REVIEW_CONTRACT = "practical-effect-review/v1"


def _finite_values(values: object, field: str) -> tuple[float, ...]:
    if not isinstance(values, (list, tuple)) or len(values) < 2:
        raise ValueError(f"{field} must contain at least two observations")
    normalized: list[float] = []
    for value in values:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
            raise ValueError(f"{field} must contain only finite numeric observations")
        normalized.append(float(value))
    return tuple(normalized)


def _mean(values: tuple[float, ...]) -> float:
    return sum(values) / len(values)


def _sample_variance(values: tuple[float, ...], mean: float) -> float:
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def two_sample_mean_interval(
    treatment: object, control: object, *, confidence_z: object = 1.96,
) -> dict[str, object]:
    """Create an upstream normal-approximation interval artifact for a mean difference.

    The interval targets ``mean(treatment) - mean(control)``.  It records raw
    finite teaching data so a downstream lesson can recompute rather than trust
    a displayed interval.  It does not establish random assignment,
    independence, normal approximation quality, or causality.
    """
    treatment_values = _finite_values(treatment, "treatment")
    control_values = _finite_values(control, "control")
    if (not isinstance(confidence_z, (int, float)) or isinstance(confidence_z, bool)
            or not isfinite(confidence_z) or confidence_z <= 0):
        raise ValueError("confidence_z must be a positive finite number")
    treatment_mean, control_mean = _mean(treatment_values), _mean(control_values)
    treatment_variance = _sample_variance(treatment_values, treatment_mean)
    control_variance = _sample_variance(control_values, control_mean)
    difference = treatment_mean - control_mean
    standard_error = sqrt(treatment_variance / len(treatment_values) + control_variance / len(control_values))
    margin = float(confidence_z) * standard_error
    return {
        "contract": INTERVAL_CONTRACT,
        "estimand": "mean(treatment) - mean(control)",
        "treatment": treatment_values,
        "control": control_values,
        "confidence_z": float(confidence_z),
        "difference": difference,
        "standard_error": standard_error,
        "interval": (difference - margin, difference + margin),
        "assumptions_not_verified_by_this_artifact": (
            "sampling_or_assignment_supports_the_estimand",
            "independent_analysis_units_or_an_appropriate_dependence_model",
            "normal_approximation_is_adequate_for_the_declared_confidence_z",
        ),
    }


def _valid_interval_artifact(interval_artifact: object) -> bool:
    if not isinstance(interval_artifact, dict) or interval_artifact.get("contract") != INTERVAL_CONTRACT:
        return False
    try:
        expected = two_sample_mean_interval(
            interval_artifact["treatment"], interval_artifact["control"],
            confidence_z=interval_artifact["confidence_z"],
        )
        return interval_artifact == expected
    except (KeyError, TypeError, ValueError):
        return False


def practical_effect_review(interval_artifact: object, minimum_effect: object) -> dict[str, object]:
    """Interpret an upstream interval against a declared practical-effect boundary.

    This is deliberately a manual-review classifier, never an automated launch,
    denial, retraining, or causal decision.  The threshold is supplied by a
    responsible context owner; statistics alone cannot choose it.
    """
    if not _valid_interval_artifact(interval_artifact):
        raise ValueError("interval_artifact must be an untampered two-sample interval artifact")
    if (not isinstance(minimum_effect, (int, float)) or isinstance(minimum_effect, bool)
            or not isfinite(minimum_effect)):
        raise ValueError("minimum_effect must be finite")
    lower, upper = interval_artifact["interval"]
    threshold = float(minimum_effect)
    if lower >= threshold:
        interpretation = "interval_entirely_at_or_above_declared_minimum_effect"
    elif upper < threshold:
        interpretation = "interval_entirely_below_declared_minimum_effect"
    else:
        interpretation = "interval_crosses_declared_minimum_effect"
    return {
        "contract": REVIEW_CONTRACT,
        "interval_artifact": interval_artifact,
        "minimum_effect": threshold,
        "interpretation": interpretation,
        "automatic_action": "none",
        "manual_review_questions": (
            "Is the minimum effect appropriate for the decision context?",
            "Do sampling, assignment and analysis-unit assumptions support this interval?",
            "Are harms, costs, subgroup effects and operational constraints separately assessed?",
        ),
    }
