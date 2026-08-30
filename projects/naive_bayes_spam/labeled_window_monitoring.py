"""Auditable performance-degradation reports for delayed labeled windows."""

from __future__ import annotations

from math import isfinite

from projects.naive_bayes_spam.main import wilson_interval
from projects.naive_bayes_spam.recalibration import brier_score, log_loss


LABELED_WINDOW_CONTRACT_VERSION = "labeled-window-monitoring/v1"


def _probability(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("probabilities must be finite numbers")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError("probabilities must lie in [0, 1]")
    return value


def _label(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int) and value in (0, 1):
        return value
    if isinstance(value, float) and value in (0.0, 1.0):
        return int(value)
    raise ValueError("labels must be booleans or 0/1 values")


def normalize_labeled_window(window: object) -> dict[str, object]:
    """Validate a fully labeled evaluation window and return JSON-safe values."""
    if not isinstance(window, dict) or set(window) != {"contract_version", "probabilities", "labels"}:
        raise ValueError("window must contain exactly contract_version, probabilities and labels")
    if window["contract_version"] != LABELED_WINDOW_CONTRACT_VERSION:
        raise ValueError(f"contract_version must be {LABELED_WINDOW_CONTRACT_VERSION!r}")
    raw_probabilities, raw_labels = window["probabilities"], window["labels"]
    if not isinstance(raw_probabilities, list) or not isinstance(raw_labels, list) or not raw_probabilities:
        raise ValueError("probabilities and labels must be non-empty lists")
    if len(raw_probabilities) != len(raw_labels):
        raise ValueError("probabilities and labels must have equal length")
    return {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": [_probability(value) for value in raw_probabilities],
        "labels": [_label(value) for value in raw_labels],
    }


def _threshold(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a non-negative finite number")
    return float(value)


def _window_metrics(window: dict[str, object]) -> dict[str, object]:
    probabilities = window["probabilities"]  # type: ignore[assignment]
    labels = window["labels"]  # type: ignore[assignment]
    predictions = [int(probability >= 0.5) for probability in probabilities]
    tp = sum(prediction == 1 and label == 1 for prediction, label in zip(predictions, labels))
    fp = sum(prediction == 1 and label == 0 for prediction, label in zip(predictions, labels))
    tn = sum(prediction == 0 and label == 0 for prediction, label in zip(predictions, labels))
    fn = sum(prediction == 0 and label == 1 for prediction, label in zip(predictions, labels))
    count = len(labels)
    correct = tp + tn
    accuracy = correct / count
    interval_low, interval_high = wilson_interval(correct, count)
    mean_probability = sum(probabilities) / count
    positive_rate = sum(labels) / count
    return {
        "count": count,
        "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "accuracy": accuracy,
        "accuracy_wilson_low": interval_low,
        "accuracy_wilson_high": interval_high,
        "brier": brier_score(probabilities, labels),
        "log_loss": log_loss(probabilities, labels),
        "mean_probability": mean_probability,
        "positive_rate": positive_rate,
        "mean_probability_gap": abs(mean_probability - positive_rate),
    }


def labeled_window_degradation_report(
    reference_window: object,
    current_window: object,
    accuracy_drop_threshold: float = 0.1,
    log_loss_increase_threshold: float = 0.1,
) -> dict[str, object]:
    """Compare two fixed labeled windows and emit review signals, never model actions.

    The Wilson intervals describe uncertainty in each accuracy estimate but do
    not establish a causal explanation.  A signal says the specified window
    and policy threshold deserve human review; it does not prescribe retraining,
    blocking traffic, or changing a decision threshold.
    """
    reference = normalize_labeled_window(reference_window)
    current = normalize_labeled_window(current_window)
    accuracy_drop_threshold = _threshold(accuracy_drop_threshold, "accuracy_drop_threshold")
    log_loss_increase_threshold = _threshold(log_loss_increase_threshold, "log_loss_increase_threshold")
    reference_metrics = _window_metrics(reference)
    current_metrics = _window_metrics(current)
    accuracy_drop = reference_metrics["accuracy"] - current_metrics["accuracy"]  # type: ignore[operator]
    log_loss_increase = current_metrics["log_loss"] - reference_metrics["log_loss"]  # type: ignore[operator]
    signals = {
        "accuracy_drop": accuracy_drop >= accuracy_drop_threshold,
        "log_loss_increase": log_loss_increase >= log_loss_increase_threshold,
    }
    return {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "reference_window": reference,
        "current_window": current,
        "policy": {
            "accuracy_drop_threshold": accuracy_drop_threshold,
            "log_loss_increase_threshold": log_loss_increase_threshold,
            "automatic_action": "none",
        },
        "reference_metrics": reference_metrics,
        "current_metrics": current_metrics,
        "deltas": {
            "accuracy_drop": accuracy_drop,
            "brier_increase": current_metrics["brier"] - reference_metrics["brier"],  # type: ignore[operator]
            "log_loss_increase": log_loss_increase,
            "mean_probability_gap_change": current_metrics["mean_probability_gap"] - reference_metrics["mean_probability_gap"],  # type: ignore[operator]
        },
        "signals": signals,
        "needs_review": any(signals.values()),
        "interpretation": "review_labeled_window" if any(signals.values()) else "no_policy_signal",
    }


def labeled_window_degradation_certificate(
    reference_window: object, current_window: object, report: object
) -> bool:
    """Rebuild a report and reject changed metrics, thresholds, or action claims."""
    if not isinstance(report, dict):
        return False
    try:
        policy = report["policy"]
        expected = labeled_window_degradation_report(
            reference_window,
            current_window,
            policy["accuracy_drop_threshold"],
            policy["log_loss_increase_threshold"],
        )
    except (KeyError, TypeError, ValueError):
        return False
    return report == expected
