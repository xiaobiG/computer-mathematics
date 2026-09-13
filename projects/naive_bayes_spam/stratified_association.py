"""Finite count-table reports for the joint/conditional probability lesson.

The report is deliberately descriptive: it makes an aggregate and every
declared stratum visible on the same finite input, but never identifies a
causal effect or selects an action.
"""

from __future__ import annotations

from typing import Final


CONTRACT: Final = "stratified-association-report/v1"
_COUNT_KEYS: Final = frozenset({
    "exposed_success", "exposed_failure", "unexposed_success", "unexposed_failure",
})


def _direction(difference: float) -> str:
    if difference > 0.0:
        return "exposed_higher"
    if difference < 0.0:
        return "exposed_lower"
    return "equal"


def _validated_counts(strata: object) -> dict[str, dict[str, int]]:
    if not isinstance(strata, dict) or not strata:
        raise ValueError("strata must be a non-empty dictionary")
    validated: dict[str, dict[str, int]] = {}
    for name, counts in strata.items():
        if not isinstance(name, str) or not name:
            raise ValueError("each stratum name must be a non-empty string")
        if not isinstance(counts, dict) or set(counts) != _COUNT_KEYS:
            raise ValueError("each stratum must supply exactly the four declared counts")
        normalized: dict[str, int] = {}
        for key in _COUNT_KEYS:
            value = counts[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("all counts must be non-negative integers")
            normalized[key] = value
        if normalized["exposed_success"] + normalized["exposed_failure"] == 0:
            raise ValueError("each stratum needs at least one exposed observation")
        if normalized["unexposed_success"] + normalized["unexposed_failure"] == 0:
            raise ValueError("each stratum needs at least one unexposed observation")
        validated[name] = normalized
    return validated


def _rate(successes: int, failures: int) -> float:
    return successes / (successes + failures)


def stratified_association_report(strata: object) -> dict[str, object]:
    """Compare pooled and per-stratum success-rate differences from one table.

    ``reversal.detected`` is true exactly when exposure has the same non-zero
    direction in every supplied stratum and the pooled direction is opposite.
    It is a finite descriptive fact about these counts, not evidence that
    exposure caused any outcome or that the declared strata remove confounding.
    """
    validated = _validated_counts(strata)
    stratum_reports: dict[str, dict[str, object]] = {}
    totals = {key: 0 for key in _COUNT_KEYS}
    directions: list[str] = []
    for name, counts in validated.items():
        exposed_rate = _rate(counts["exposed_success"], counts["exposed_failure"])
        unexposed_rate = _rate(counts["unexposed_success"], counts["unexposed_failure"])
        difference = exposed_rate - unexposed_rate
        direction = _direction(difference)
        directions.append(direction)
        stratum_reports[name] = {
            "counts": counts,
            "exposed_success_rate": exposed_rate,
            "unexposed_success_rate": unexposed_rate,
            "success_rate_difference": difference,
            "direction": direction,
        }
        for key, value in counts.items():
            totals[key] += value

    pooled_exposed_rate = _rate(totals["exposed_success"], totals["exposed_failure"])
    pooled_unexposed_rate = _rate(totals["unexposed_success"], totals["unexposed_failure"])
    pooled_difference = pooled_exposed_rate - pooled_unexposed_rate
    pooled_direction = _direction(pooled_difference)
    all_strata_same_nonzero_direction = (
        len(set(directions)) == 1 and directions[0] != "equal"
    )
    pooled_opposes_all_strata = (
        all_strata_same_nonzero_direction and pooled_direction != directions[0]
    )
    return {
        "contract": CONTRACT,
        "strata": stratum_reports,
        "pooled": {
            "counts": totals,
            "exposed_success_rate": pooled_exposed_rate,
            "unexposed_success_rate": pooled_unexposed_rate,
            "success_rate_difference": pooled_difference,
            "direction": pooled_direction,
        },
        "reversal": {
            "all_strata_same_nonzero_direction": all_strata_same_nonzero_direction,
            "pooled_opposes_all_strata": pooled_opposes_all_strata,
            "detected": pooled_opposes_all_strata,
        },
        "interpretation": "descriptive_association_only",
        "automatic_action": "none",
    }


def stratified_association_certificate(strata: object, report: object) -> bool:
    """Rebuild every aggregate and stratum quantity, rejecting changed claims."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        return report == stratified_association_report(strata)
    except (KeyError, TypeError, ValueError):
        return False
