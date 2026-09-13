"""Auditable subgroup metrics with an explicit small-sample refusal boundary."""

from __future__ import annotations

from math import isfinite, sqrt
from statistics import NormalDist

from projects.naive_bayes_spam.labeled_window_monitoring import _window_metrics, normalize_labeled_window


SUBGROUP_CONTRACT_VERSION = "subgroup-monitoring/v2"
FAMILY_CONFIDENCE_LEVEL = 0.95


def _declared_groups(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("declared_groups must be a non-empty list of group names")
    if any(not isinstance(group, str) or not group for group in value) or len(set(value)) != len(value):
        raise ValueError("declared_groups must contain unique non-empty strings")
    return list(value)


def _comparison_pairs(value: object, declared_groups: list[str]) -> list[list[str]]:
    """Validate an ordered, predeclared family of pairwise comparisons."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("comparison_pairs must be a list of two-group lists")
    pairs: list[list[str]] = []
    seen: set[frozenset[str]] = set()
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(group, str) for group in pair):
            raise ValueError("each comparison pair must contain two group names")
        left, right = pair
        if left == right or left not in declared_groups or right not in declared_groups:
            raise ValueError("comparison pairs must name two distinct declared groups")
        key = frozenset((left, right))
        if key in seen:
            raise ValueError("comparison_pairs must not repeat an unordered pair")
        seen.add(key)
        pairs.append([left, right])
    return pairs


def _accuracy_comparison(left: dict[str, object], right: dict[str, object], pair_count: int) -> dict[str, object]:
    """Give a Bonferroni normal interval for one frozen accuracy difference."""
    if not left["sufficient_sample"] or not right["sufficient_sample"]:
        return {"groups": [left["group"], right["group"]], "status": "insufficient_sample_for_pairwise_comparison", "accuracy_difference_left_minus_right": None, "interval": None}
    left_accuracy = left["metrics"]["accuracy"]  # type: ignore[index]
    right_accuracy = right["metrics"]["accuracy"]  # type: ignore[index]
    left_count, right_count = left["count"], right["count"]
    difference = left_accuracy - right_accuracy  # type: ignore[operator]
    standard_error = sqrt(left_accuracy * (1.0 - left_accuracy) / left_count + right_accuracy * (1.0 - right_accuracy) / right_count)  # type: ignore[operator]
    alpha_per_comparison = (1.0 - FAMILY_CONFIDENCE_LEVEL) / pair_count
    critical_value = NormalDist().inv_cdf(1.0 - alpha_per_comparison / 2.0)
    low, high = difference - critical_value * standard_error, difference + critical_value * standard_error
    return {"groups": [left["group"], right["group"]], "status": "difference_interval_excludes_zero" if low > 0.0 or high < 0.0 else "difference_interval_contains_zero", "accuracy_difference_left_minus_right": difference, "interval": [low, high], "standard_error_normal_approximation": standard_error}


def subgroup_report(
    window: object,
    groups: object,
    minimum_group_size: int = 20,
    declared_groups: object = None,
    comparison_pairs: object = None,
) -> dict[str, object]:
    """Report a frozen subgroup universe, including groups with zero samples.

    The declared group list is a governance input: deriving it from observed
    data lets a report quietly omit a pre-specified group that happens to have
    no labels in this window.  This function reports every declared group but
    still refuses metrics whenever its count is below the minimum.
    """
    normalized = normalize_labeled_window(window)
    if not isinstance(groups, list) or len(groups) != len(normalized["labels"]):
        raise ValueError("groups and labeled_window must have equal length")
    if any(not isinstance(group, str) or not group for group in groups):
        raise ValueError("groups must be non-empty strings")
    if isinstance(minimum_group_size, bool) or not isinstance(minimum_group_size, int) or minimum_group_size < 2:
        raise ValueError("minimum_group_size must be an integer at least 2")
    declared = _declared_groups(declared_groups)
    pairs = _comparison_pairs(comparison_pairs, declared)
    if any(group not in declared for group in groups):
        raise ValueError("every observed group must belong to declared_groups")
    indexes_by_group = {group: [] for group in declared}
    for index, group in enumerate(groups):
        indexes_by_group[group].append(index)
    rows = []
    for group in declared:
        indexes = indexes_by_group[group]
        subgroup = {"contract_version": normalized["contract_version"], "probabilities": [normalized["probabilities"][i] for i in indexes], "labels": [normalized["labels"][i] for i in indexes]}
        row = {"group": group, "count": len(indexes), "sufficient_sample": len(indexes) >= minimum_group_size}
        if row["sufficient_sample"]:
            row["metrics"] = _window_metrics(subgroup)
        else:
            row["metrics"] = None
            row["interpretation"] = "insufficient_sample_for_group_conclusion"
        rows.append(row)
    by_group = {row["group"]: row for row in rows}
    comparisons = [_accuracy_comparison(by_group[left], by_group[right], len(pairs)) for left, right in pairs]
    return {
        "contract_version": SUBGROUP_CONTRACT_VERSION,
        "window": normalized,
        "groups": list(groups),
        "policy": {
            "declared_groups": declared,
            "minimum_group_size": minimum_group_size,
            "comparison_pairs": pairs,
            "family_confidence_level": FAMILY_CONFIDENCE_LEVEL,
            "multiplicity_adjustment": "bonferroni_over_predeclared_pairs",
            "automatic_action": "none",
        },
        "subgroups": rows,
        "comparisons": comparisons,
        "interpretation": "review_sufficient_subgroups_and_predeclared_pairwise_differences_only",
    }


def subgroup_certificate(window: object, groups: object, report: object) -> bool:
    if not isinstance(report, dict):
        return False
    try:
        policy = report["policy"]
        return report == subgroup_report(
            window, groups, policy["minimum_group_size"], policy["declared_groups"], policy["comparison_pairs"]
        )
    except (KeyError, TypeError, ValueError):
        return False
