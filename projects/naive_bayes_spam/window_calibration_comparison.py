"""Frozen, descriptive comparison of calibration across two labeled windows."""

from __future__ import annotations

from math import isfinite

from projects.naive_bayes_spam.bootstrap_support import require_integer
from projects.naive_bayes_spam.labeled_window_monitoring import normalize_labeled_window
from projects.naive_bayes_spam.subgroup_calibration import _calibration_metrics


WINDOW_CALIBRATION_COMPARISON_CONTRACT_VERSION = "window-calibration-comparison/v1"


def _name(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty frozen window name")
    return value


def _unit(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{field} must be a finite number in [0, 1]")
    return float(value)


def window_calibration_comparison_report(
    reference_name: object,
    reference_window: object,
    current_name: object,
    current_window: object,
    *,
    bins: int = 5,
    minimum_window_size: int = 20,
    ece_delta_review_threshold: float = 0.05,
    confidence_z: float = 1.96,
) -> dict[str, object]:
    """Compare pre-named windows under one frozen binning and review policy.

    The output is descriptive evidence. It deliberately contains no causal
    attribution, population ranking, recalibration, or automatic action.
    """
    reference_label = _name(reference_name, "reference_name")
    current_label = _name(current_name, "current_name")
    if reference_label == current_label:
        raise ValueError("reference_name and current_name must differ")
    reference = normalize_labeled_window(reference_window)
    current = normalize_labeled_window(current_window)
    bins = require_integer(bins, "bins", 2)
    minimum_window_size = require_integer(minimum_window_size, "minimum_window_size", 2)
    threshold = _unit(ece_delta_review_threshold, "ece_delta_review_threshold")
    if isinstance(confidence_z, bool) or not isinstance(confidence_z, (int, float)) or not isfinite(confidence_z) or confidence_z <= 0:
        raise ValueError("confidence_z must be a positive finite number")
    if len(reference["labels"]) < minimum_window_size or len(current["labels"]) < minimum_window_size:
        raise ValueError("both frozen windows must meet minimum_window_size")
    reference_metrics = _calibration_metrics(reference["probabilities"], reference["labels"], bins, float(confidence_z))
    current_metrics = _calibration_metrics(current["probabilities"], current["labels"], bins, float(confidence_z))
    ece_delta = current_metrics["expected_calibration_error"] - reference_metrics["expected_calibration_error"]
    return {
        "contract_version": WINDOW_CALIBRATION_COMPARISON_CONTRACT_VERSION,
        "reference": {"name": reference_label, "window": reference, "metrics": reference_metrics},
        "current": {"name": current_label, "window": current, "metrics": current_metrics},
        "policy": {"bins": bins, "minimum_window_size": minimum_window_size, "ece_delta_review_threshold": threshold, "confidence_z": float(confidence_z), "automatic_action": "none"},
        "comparison": {
            "expected_calibration_error_delta": ece_delta,
            "brier_delta": current_metrics["brier"] - reference_metrics["brier"],
            "absolute_ece_delta": abs(ece_delta),
            "needs_review": abs(ece_delta) >= threshold,
        },
        "causal_interpretation": "not_established",
        "interpretation": "review_frozen_window_calibration_difference" if abs(ece_delta) >= threshold else "no_policy_signal",
    }


def window_calibration_comparison_certificate(
    reference_name: object, reference_window: object, current_name: object, current_window: object, report: object
) -> bool:
    """Rebuild a frozen-window comparison to reject altered windows or policy."""
    if not isinstance(report, dict):
        return False
    try:
        policy = report["policy"]
        expected = window_calibration_comparison_report(
            reference_name, reference_window, current_name, current_window,
            bins=policy["bins"], minimum_window_size=policy["minimum_window_size"],
            ece_delta_review_threshold=policy["ece_delta_review_threshold"], confidence_z=policy["confidence_z"],
        )
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
