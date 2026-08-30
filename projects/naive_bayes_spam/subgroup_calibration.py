"""Auditable calibration diagnostics for predefined, sufficiently sized groups.

This module deliberately reports descriptive evidence only.  A group label is
an externally governed input: it is not inferred, used for ranking people, or
turned into an automatic model or product action.
"""

from __future__ import annotations

from math import isfinite

from projects.naive_bayes_spam.labeled_window_monitoring import normalize_labeled_window
from projects.naive_bayes_spam.main import wilson_interval
from projects.naive_bayes_spam.recalibration import brier_score


SUBGROUP_CALIBRATION_CONTRACT_VERSION = "subgroup-calibration/v1"


def _positive_int(value: object, name: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")
    return value


def _threshold(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be a finite number in [0, 1]")
    return value


def _positive_finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite number")
    return float(value)


def _normalized_groups(groups: object, size: int) -> list[str]:
    if not isinstance(groups, list) or len(groups) != size:
        raise ValueError("groups and labeled_window must have equal length")
    if any(not isinstance(group, str) or not group for group in groups):
        raise ValueError("groups must be non-empty strings")
    return list(groups)


def calibration_bins(
    probabilities: list[float], labels: list[int], bins: int, confidence_z: float = 1.96
) -> list[dict[str, float | int]]:
    """Return non-empty bins, ECE terms, and Wilson bounds on observed rate.

    ECE is only a binned descriptive discrepancy.  Its value depends on the
    fixed bin policy, so callers record the bin count beside the result.  The
    Wilson interval conditions on the observations in one bin; it bounds the
    uncertain positive rate, not the model's future calibration or ECE itself.
    """
    grouped: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for probability, label in zip(probabilities, labels):
        grouped[min(int(probability * bins), bins - 1)].append((probability, label))
    rows: list[dict[str, float | int]] = []
    total = len(probabilities)
    for index, values in enumerate(grouped):
        if not values:
            continue
        count = len(values)
        mean_probability = sum(probability for probability, _ in values) / count
        positive_count = sum(label for _, label in values)
        positive_rate = positive_count / count
        positive_rate_wilson_low, positive_rate_wilson_high = wilson_interval(
            positive_count, count, confidence_z
        )
        gap = abs(mean_probability - positive_rate)
        # The prediction average is fixed for the observed bin.  Mapping the
        # Wilson endpoints through |p - y| yields a conservative interval for
        # the unknown absolute discrepancy under this reporting convention.
        if positive_rate_wilson_low <= mean_probability <= positive_rate_wilson_high:
            gap_wilson_low = 0.0
        else:
            gap_wilson_low = min(
                abs(mean_probability - positive_rate_wilson_low),
                abs(mean_probability - positive_rate_wilson_high),
            )
        gap_wilson_high = max(
            abs(mean_probability - positive_rate_wilson_low),
            abs(mean_probability - positive_rate_wilson_high),
        )
        rows.append({
            "lower": index / bins,
            "upper": (index + 1) / bins,
            "count": count,
            "mean_probability": mean_probability,
            "positive_count": positive_count,
            "positive_rate": positive_rate,
            "positive_rate_wilson_low": positive_rate_wilson_low,
            "positive_rate_wilson_high": positive_rate_wilson_high,
            "absolute_gap": gap,
            "absolute_gap_wilson_low": gap_wilson_low,
            "absolute_gap_wilson_high": gap_wilson_high,
            "ece_contribution": count / total * gap,
        })
    return rows


def _calibration_metrics(
    probabilities: list[float], labels: list[int], bins: int, confidence_z: float
) -> dict[str, object]:
    rows = calibration_bins(probabilities, labels, bins, confidence_z)
    return {
        "count": len(labels),
        "brier": brier_score(probabilities, labels),
        "expected_calibration_error": sum(row["ece_contribution"] for row in rows),
        "bins": rows,
    }


def subgroup_calibration_report(
    window: object,
    groups: object,
    *,
    bins: int = 5,
    minimum_group_size: int = 20,
    ece_review_threshold: float = 0.05,
    confidence_z: float = 1.96,
) -> dict[str, object]:
    """Report pooled and eligible-group calibration without causal claims.

    Groups below the declared size never receive calibration metrics.  Eligible
    groups crossing the fixed ECE policy receive a *review* signal only.  Each
    bin also receives a Wilson interval for its observed positive rate; neither
    ECE nor that interval proves bias, fairness, safety, or a causal reason.
    """
    normalized = normalize_labeled_window(window)
    probabilities = normalized["probabilities"]  # type: ignore[assignment]
    labels = normalized["labels"]  # type: ignore[assignment]
    group_values = _normalized_groups(groups, len(labels))
    bins = _positive_int(bins, "bins", 2)
    minimum_group_size = _positive_int(minimum_group_size, "minimum_group_size", 2)
    ece_review_threshold = _threshold(ece_review_threshold, "ece_review_threshold")
    confidence_z = _positive_finite(confidence_z, "confidence_z")
    rows: list[dict[str, object]] = []
    for group in sorted(set(group_values)):
        indexes = [index for index, value in enumerate(group_values) if value == group]
        subgroup_probabilities = [probabilities[index] for index in indexes]
        subgroup_labels = [labels[index] for index in indexes]
        sufficient_sample = len(indexes) >= minimum_group_size
        row: dict[str, object] = {"group": group, "count": len(indexes), "sufficient_sample": sufficient_sample}
        if sufficient_sample:
            metrics = _calibration_metrics(subgroup_probabilities, subgroup_labels, bins, confidence_z)
            row["metrics"] = metrics
            row["needs_review"] = metrics["expected_calibration_error"] >= ece_review_threshold
            row["interpretation"] = "review_group_calibration" if row["needs_review"] else "no_policy_signal"
        else:
            row["metrics"] = None
            row["needs_review"] = False
            row["interpretation"] = "insufficient_sample_for_group_calibration_conclusion"
        rows.append(row)
    overall = _calibration_metrics(probabilities, labels, bins, confidence_z)
    eligible_signals = [row["needs_review"] for row in rows if row["sufficient_sample"]]
    return {
        "contract_version": SUBGROUP_CALIBRATION_CONTRACT_VERSION,
        "window": normalized,
        "groups": group_values,
        "policy": {
            "bins": bins,
            "minimum_group_size": minimum_group_size,
            "ece_review_threshold": ece_review_threshold,
            "confidence_z": confidence_z,
            "automatic_action": "none",
        },
        "overall_metrics": overall,
        "subgroups": rows,
        "needs_review": any(eligible_signals),
        "causal_interpretation": "not_established",
        "interpretation": "review_eligible_group_calibration" if any(eligible_signals) else "no_policy_signal",
    }


def subgroup_calibration_certificate(window: object, groups: object, report: object) -> bool:
    """Rebuild the report so altered policies, bins, or conclusions are rejected."""
    if not isinstance(report, dict):
        return False
    try:
        policy = report["policy"]
        expected = subgroup_calibration_report(
            window,
            groups,
            bins=policy["bins"],
            minimum_group_size=policy["minimum_group_size"],
            ece_review_threshold=policy["ece_review_threshold"],
            confidence_z=policy["confidence_z"],
        )
    except (KeyError, TypeError, ValueError):
        return False
    return report == expected
