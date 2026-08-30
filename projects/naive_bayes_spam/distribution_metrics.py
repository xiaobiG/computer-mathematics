"""Entropy, cross-entropy and KL divergence for finite teaching distributions."""

from __future__ import annotations

from math import exp, inf, isclose, isfinite, log
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


def information_report_certificate(
    actual: Distribution, predicted: Distribution, report: dict[str, float], *, tolerance: float = 1e-12
) -> dict[str, bool]:
    """Recompute the entropy decomposition without trusting a stored report."""
    empty = {
        "fields_match_recomputed_metrics": False,
        "finite_decomposition_is_exact_within_tolerance": False,
        "infinite_loss_is_classified_consistently": False,
        "valid": False,
    }
    try:
        if tolerance < 0.0 or not isfinite(tolerance) or not isinstance(report, dict):
            return empty
        expected = information_report(actual, predicted)
        required = set(expected)
        if set(report) != required or any(not isinstance(report[name], (int, float)) for name in required):
            return empty
        fields_match = all(
            (report[name] == expected[name] if not isfinite(expected[name])
             else abs(report[name] - expected[name]) <= tolerance)
            for name in required
        )
        infinite = not isfinite(expected["cross_entropy"])
        finite_decomposition = (not infinite and abs(report["decomposition_residual"]) <= tolerance)
        infinite_classification = (infinite and report["cross_entropy"] == inf
                                   and report["kl_divergence"] == inf
                                   and report["decomposition_residual"] == 0.0)
        return {
            "fields_match_recomputed_metrics": fields_match,
            "finite_decomposition_is_exact_within_tolerance": finite_decomposition,
            "infinite_loss_is_classified_consistently": infinite_classification,
            "valid": fields_match and (finite_decomposition or infinite_classification),
        }
    except (TypeError, ValueError):
        return empty


def _validate_logits(logits: list[float], target_index: int) -> None:
    if not isinstance(logits, list) or not logits:
        raise ValueError("logits must be a non-empty list")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
           for value in logits):
        raise ValueError("logits must be finite numbers")
    if (not isinstance(target_index, int) or isinstance(target_index, bool)
            or not 0 <= target_index < len(logits)):
        raise ValueError("target_index must select one logit")


def log_softmax(logits: list[float]) -> tuple[float, ...]:
    """Return stable log probabilities without materialising enormous exp(logit).

    Subtracting the largest logit leaves the softmax probabilities unchanged:
    ``log(sum(exp(z))) = maximum + log(sum(exp(z - maximum)))``.  Every
    exponent is then at most one, so the normalising sum cannot overflow.
    """
    if not isinstance(logits, list) or not logits:
        raise ValueError("logits must be a non-empty list")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
           for value in logits):
        raise ValueError("logits must be finite numbers")
    maximum = max(logits)
    log_normalizer = maximum + log(sum(exp(value - maximum) for value in logits))
    return tuple(float(value - log_normalizer) for value in logits)


def categorical_cross_entropy_from_logits(logits: list[float], target_index: int) -> float:
    """Return ``-log softmax(logits)[target_index]`` under a strict contract."""
    _validate_logits(logits, target_index)
    return -log_softmax(logits)[target_index]


def logit_cross_entropy_report(logits: list[float], target_index: int) -> dict[str, object]:
    """Expose a stable logit loss and its normalisation witness for one label."""
    _validate_logits(logits, target_index)
    log_probabilities = log_softmax(logits)
    return {
        "target_index": target_index,
        "log_probabilities": log_probabilities,
        "loss": -log_probabilities[target_index],
        "log_probability_normalizer": log(sum(exp(value) for value in log_probabilities)),
    }


def logit_cross_entropy_certificate(
    logits: list[float], target_index: int, report: dict[str, object], *, tolerance: float = 1e-12,
) -> dict[str, bool]:
    """Recompute a log-sum-exp loss report instead of trusting a displayed loss."""
    empty = {
        "target_matches": False,
        "log_probabilities_match": False,
        "loss_matches_negative_target_log_probability": False,
        "normalizes_in_log_space": False,
        "valid": False,
    }
    try:
        if tolerance < 0.0 or not isfinite(tolerance) or not isinstance(report, dict):
            return empty
        expected = logit_cross_entropy_report(logits, target_index)
        if set(report) != set(expected) or report.get("target_index") != target_index:
            return empty
        observed_logs = report.get("log_probabilities")
        if not isinstance(observed_logs, tuple) or len(observed_logs) != len(expected["log_probabilities"]):
            return empty
        logs_match = all(isinstance(value, (int, float)) and isfinite(value)
                         and abs(value - expected_value) <= tolerance
                         for value, expected_value in zip(observed_logs, expected["log_probabilities"]))
        loss = report.get("loss")
        normalizer = report.get("log_probability_normalizer")
        loss_matches = (isinstance(loss, (int, float)) and isfinite(loss)
                        and abs(loss - expected["loss"]) <= tolerance)
        normalizes = (isinstance(normalizer, (int, float)) and isfinite(normalizer)
                      and abs(normalizer) <= tolerance)
        return {
            "target_matches": True,
            "log_probabilities_match": logs_match,
            "loss_matches_negative_target_log_probability": loss_matches,
            "normalizes_in_log_space": normalizes,
            "valid": logs_match and loss_matches and normalizes,
        }
    except (TypeError, ValueError):
        return empty
