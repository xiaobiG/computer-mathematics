"""A deliberately narrow inverse-probability weighting audit for attrition lessons."""

from __future__ import annotations

from math import isfinite


CONTRACT = "attrition-ipw-observation-audit/v1"


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _normalize_cohort(value: object) -> list[dict[str, object]]:
    """Keep every enrolled unit, including those whose outcome was not observed."""
    if not isinstance(value, list) or len(value) < 2:
        raise ValueError("cohort must contain at least two enrolled units")
    normalized: list[dict[str, object]] = []
    identifiers: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) not in (
            {"unit_id", "observed", "observation_probability"},
            {"unit_id", "observed", "observation_probability", "outcome"},
        ):
            raise ValueError("each unit has id, observed flag, observation probability, and outcome only when observed")
        unit_id = item["unit_id"]
        if not isinstance(unit_id, str) or not unit_id or unit_id in identifiers:
            raise ValueError("unit_id values must be unique non-empty strings")
        observed = item["observed"]
        if not isinstance(observed, bool):
            raise ValueError("observed must be boolean")
        probability = _number(item["observation_probability"], "observation_probability")
        if not 0 < probability <= 1:
            raise ValueError("observation_probability must be in (0, 1]")
        has_outcome = "outcome" in item
        if observed != has_outcome:
            raise ValueError("outcome must appear exactly when observed is true")
        row: dict[str, object] = {
            "unit_id": unit_id, "observed": observed, "observation_probability": probability,
        }
        if observed:
            row["outcome"] = _number(item["outcome"], "outcome")
        identifiers.add(unit_id)
        normalized.append(row)
    if not any(row["observed"] for row in normalized):
        raise ValueError("at least one outcome must be observed")
    return normalized


def attrition_ipw_observation_audit_report(
    cohort: object, *, positivity_floor: float = .05,
) -> dict[str, object]:
    """Audit declared observation probabilities; it does not fit them or infer causality."""
    floor = _number(positivity_floor, "positivity_floor")
    if not 0 < floor <= 1:
        raise ValueError("positivity_floor must be in (0, 1]")
    rows = _normalize_cohort(cohort)
    observed = [row for row in rows if row["observed"]]
    weights = [1 / float(row["observation_probability"]) for row in observed]
    weighted_outcomes = [weight * float(row["outcome"]) for row, weight in zip(observed, weights)]
    return {
        "contract": CONTRACT,
        "cohort_shape": {
            "enrolled_units": len(rows), "observed_outcomes": len(observed),
            "missing_outcomes": len(rows) - len(observed),
            "observed_fraction": len(observed) / len(rows),
        },
        "observation_policy": {
            "probabilities": [{"unit_id": row["unit_id"], "observation_probability": row["observation_probability"]} for row in rows],
            "positivity_floor": floor,
            "minimum_probability": min(float(row["observation_probability"]) for row in rows),
            "positivity_review_required": any(float(row["observation_probability"]) < floor for row in rows),
            "largest_observed_weight": max(weights),
        },
        "estimates": {
            "complete_case_mean": sum(float(row["outcome"]) for row in observed) / len(observed),
            "horvitz_thompson_mean": sum(weighted_outcomes) / len(rows),
            "hajek_mean": sum(weighted_outcomes) / sum(weights),
        },
        "target": "finite_enrolled_cohort_mean",
        "automatic_action": "none",
        "identification_boundary": (
            "Horvitz-Thompson is unbiased over the declared observation randomization only when every enrolled unit has "
            "positive, correctly supplied observation probability; Hájek is a normalized ratio estimate, not exactly unbiased."
        ),
    }


def attrition_ipw_observation_audit_certificate(cohort: object, report: object) -> bool:
    """Rebuild the report so a changed cohort, threshold, or estimate cannot pass."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        floor = report["observation_policy"]["positivity_floor"]
        return report == attrition_ipw_observation_audit_report(cohort, positivity_floor=floor)
    except (KeyError, TypeError, ValueError):
        return False
