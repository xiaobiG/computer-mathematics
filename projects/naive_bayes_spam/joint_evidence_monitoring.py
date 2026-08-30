"""Join categorical input drift and delayed-label evidence without causal claims."""

from __future__ import annotations

from projects.naive_bayes_spam.drift_monitoring import categorical_drift_report
from projects.naive_bayes_spam.labeled_window_monitoring import (
    LABELED_WINDOW_CONTRACT_VERSION,
    labeled_window_degradation_report,
    normalize_labeled_window,
)


JOINT_EVIDENCE_CONTRACT_VERSION = "joint-evidence-monitoring/v1"


def _snapshot(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"contract_version", "categories", "labeled_window"}:
        raise ValueError("snapshot must contain exactly contract_version, categories and labeled_window")
    if value["contract_version"] != JOINT_EVIDENCE_CONTRACT_VERSION:
        raise ValueError(f"contract_version must be {JOINT_EVIDENCE_CONTRACT_VERSION!r}")
    categories = value["categories"]
    if not isinstance(categories, list) or not categories or any(not isinstance(item, str) or not item for item in categories):
        raise ValueError("categories must be a non-empty list of non-empty strings")
    window = normalize_labeled_window(value["labeled_window"])
    if len(categories) != len(window["labels"]):
        raise ValueError("categories and labeled_window must have equal length")
    return {
        "contract_version": JOINT_EVIDENCE_CONTRACT_VERSION,
        "categories": list(categories),
        "labeled_window": window,
    }


def joint_evidence_report(
    reference_snapshot: object,
    current_snapshot: object,
    *,
    psi_threshold: float = 0.1,
    accuracy_drop_threshold: float = 0.1,
    log_loss_increase_threshold: float = 0.1,
) -> dict[str, object]:
    """Return co-located evidence, never an explanation or automated action.

    Input categories and delayed labels are indexed to the same snapshot.  A
    simultaneous input and outcome signal can motivate review, but it does not
    establish that category drift caused performance or calibration change.
    """
    reference = _snapshot(reference_snapshot)
    current = _snapshot(current_snapshot)
    input_evidence = categorical_drift_report(
        reference["categories"], current["categories"], psi_threshold=psi_threshold  # type: ignore[arg-type]
    )
    outcome_evidence = labeled_window_degradation_report(
        reference["labeled_window"],  # type: ignore[arg-type]
        current["labeled_window"],  # type: ignore[arg-type]
        accuracy_drop_threshold,
        log_loss_increase_threshold,
    )
    signals = {
        "input_distribution": input_evidence["needs_review"],
        "labeled_performance": outcome_evidence["needs_review"],
    }
    return {
        "contract_version": JOINT_EVIDENCE_CONTRACT_VERSION,
        "reference_snapshot": reference,
        "current_snapshot": current,
        "policy": {
            "psi_threshold": input_evidence["psi_threshold"],
            "accuracy_drop_threshold": outcome_evidence["policy"]["accuracy_drop_threshold"],  # type: ignore[index]
            "log_loss_increase_threshold": outcome_evidence["policy"]["log_loss_increase_threshold"],  # type: ignore[index]
            "automatic_action": "none",
        },
        "input_evidence": input_evidence,
        "outcome_evidence": outcome_evidence,
        "signals": signals,
        "needs_review": any(signals.values()),
        "causal_interpretation": "not_established",
        "interpretation": "review_joint_evidence" if any(signals.values()) else "no_policy_signal",
    }


def joint_evidence_certificate(reference_snapshot: object, current_snapshot: object, report: object) -> bool:
    """Rebuild the joined report and reject altered thresholds or conclusions."""
    if not isinstance(report, dict):
        return False
    try:
        policy = report["policy"]
        expected = joint_evidence_report(
            reference_snapshot,
            current_snapshot,
            psi_threshold=policy["psi_threshold"],
            accuracy_drop_threshold=policy["accuracy_drop_threshold"],
            log_loss_increase_threshold=policy["log_loss_increase_threshold"],
        )
    except (KeyError, TypeError, ValueError):
        return False
    return report == expected
