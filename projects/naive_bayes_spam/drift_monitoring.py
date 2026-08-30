"""Auditable categorical input-drift reports for teaching.

The report detects a change in the observed feature-category distribution.  It
does not identify its cause, detect an unobserved label change, or prescribe a
model action; an alert means that a person should review the data contract.
"""

from __future__ import annotations

from collections import Counter
from math import isfinite, log


def _categories(values: list[str], name: str) -> list[str]:
    if not values:
        raise ValueError(f"{name} must not be empty")
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{name} categories must be non-empty strings")
    return values


def _positive_finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite number")
    return float(value)


def categorical_drift_report(
    reference: list[str],
    current: list[str],
    smoothing: float = 1e-6,
    psi_threshold: float = 0.1,
) -> dict[str, object]:
    """Compare reference and current category frequencies.

    Additive smoothing gives every category in the union positive mass, so a
    new category is reported instead of causing an infinite logarithm.  The
    Population Stability Index (PSI) is ``sum((q-p) log(q/p))``; total
    variation is half the L1 distance.  ``needs_review`` is a policy trigger,
    not a claim that the model has become wrong.
    """
    reference = _categories(reference, "reference")
    current = _categories(current, "current")
    smoothing = _positive_finite(smoothing, "smoothing")
    psi_threshold = _positive_finite(psi_threshold, "psi_threshold")
    reference_counts = Counter(reference)
    current_counts = Counter(current)
    categories = sorted(set(reference_counts) | set(current_counts))
    category_count = len(categories)
    reference_denominator = len(reference) + smoothing * category_count
    current_denominator = len(current) + smoothing * category_count
    rows = []
    psi = 0.0
    total_variation = 0.0
    for category in categories:
        reference_share = (reference_counts[category] + smoothing) / reference_denominator
        current_share = (current_counts[category] + smoothing) / current_denominator
        psi_component = (current_share - reference_share) * log(current_share / reference_share)
        psi += psi_component
        total_variation += abs(current_share - reference_share)
        rows.append({
            "category": category,
            "reference_count": reference_counts[category],
            "current_count": current_counts[category],
            "reference_share": reference_share,
            "current_share": current_share,
            "psi_component": psi_component,
        })
    return {
        "reference_count": len(reference),
        "current_count": len(current),
        "smoothing": smoothing,
        "psi_threshold": psi_threshold,
        "psi": psi,
        "total_variation": total_variation / 2.0,
        "needs_review": psi >= psi_threshold,
        "categories": rows,
    }


def categorical_drift_certificate(
    reference: list[str], current: list[str], report: dict[str, object]
) -> bool:
    """Independently rebuild a report and reject any changed field or policy."""
    if not isinstance(report, dict):
        return False
    try:
        smoothing = report["smoothing"]
        psi_threshold = report["psi_threshold"]
        expected = categorical_drift_report(reference, current, smoothing, psi_threshold)
    except (KeyError, TypeError, ValueError):
        return False
    return report == expected
