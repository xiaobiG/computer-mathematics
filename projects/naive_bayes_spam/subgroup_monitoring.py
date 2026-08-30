"""Auditable subgroup metrics with an explicit small-sample refusal boundary."""

from __future__ import annotations

from math import isfinite

from projects.naive_bayes_spam.labeled_window_monitoring import _window_metrics, normalize_labeled_window


SUBGROUP_CONTRACT_VERSION = "subgroup-monitoring/v1"


def subgroup_report(window: object, groups: object, minimum_group_size: int = 20) -> dict[str, object]:
    """Report only sufficiently sized subgroups; never rank people or automate action."""
    normalized = normalize_labeled_window(window)
    if not isinstance(groups, list) or len(groups) != len(normalized["labels"]):
        raise ValueError("groups and labeled_window must have equal length")
    if any(not isinstance(group, str) or not group for group in groups):
        raise ValueError("groups must be non-empty strings")
    if isinstance(minimum_group_size, bool) or not isinstance(minimum_group_size, int) or minimum_group_size < 2:
        raise ValueError("minimum_group_size must be an integer at least 2")
    rows = []
    for group in sorted(set(groups)):
        indexes = [index for index, value in enumerate(groups) if value == group]
        subgroup = {"contract_version": normalized["contract_version"], "probabilities": [normalized["probabilities"][i] for i in indexes], "labels": [normalized["labels"][i] for i in indexes]}
        row = {"group": group, "count": len(indexes), "sufficient_sample": len(indexes) >= minimum_group_size}
        if row["sufficient_sample"]:
            row["metrics"] = _window_metrics(subgroup)
        else:
            row["metrics"] = None
            row["interpretation"] = "insufficient_sample_for_group_conclusion"
        rows.append(row)
    return {"contract_version": SUBGROUP_CONTRACT_VERSION, "window": normalized, "groups": list(groups), "policy": {"minimum_group_size": minimum_group_size, "automatic_action": "none"}, "subgroups": rows, "interpretation": "review_sufficient_subgroups_only"}


def subgroup_certificate(window: object, groups: object, report: object) -> bool:
    if not isinstance(report, dict):
        return False
    try:
        return report == subgroup_report(window, groups, report["policy"]["minimum_group_size"])
    except (KeyError, TypeError, ValueError):
        return False
