"""Explicit floating-point comparison contracts for teaching experiments."""

from __future__ import annotations

from math import isfinite, isinf, isnan


def close_enough(
    left: float, right: float, *, abs_tol: float = 1e-12, rel_tol: float = 1e-9
) -> bool:
    """Compare two values under an explicit absolute-and-relative contract.

    NaN is never close to anything.  Equal infinities are considered equal;
    opposite infinities are not.  Finite values use the larger of the absolute
    and scale-dependent relative tolerances.
    """
    if abs_tol < 0 or rel_tol < 0:
        raise ValueError("tolerances must be non-negative")
    if isnan(left) or isnan(right):
        return False
    if isinf(left) or isinf(right):
        return left == right
    return abs(left - right) <= max(abs_tol, rel_tol * max(abs(left), abs(right)))


def comparison_report(
    left: float, right: float, *, abs_tol: float = 1e-12, rel_tol: float = 1e-9
) -> dict[str, object]:
    """Expose the comparison's branch, scale and threshold as audit data."""
    decision = close_enough(left, right, abs_tol=abs_tol, rel_tol=rel_tol)
    finite_pair = isfinite(left) and isfinite(right)
    report: dict[str, object] = {
        "left": left,
        "right": right,
        "abs_tol": abs_tol,
        "rel_tol": rel_tol,
        "finite_pair": finite_pair,
        "difference": abs(left - right) if finite_pair else None,
        "threshold": max(abs_tol, rel_tol * max(abs(left), abs(right))) if finite_pair else None,
        "close": decision,
    }
    report["certificate"] = comparison_certificate(report)
    return report


def comparison_certificate(report: dict[str, object]) -> dict[str, bool]:
    """Recompute a report without trusting its displayed decision or threshold."""
    required = ("left", "right", "abs_tol", "rel_tol")
    if any(key not in report for key in required):
        return {"has_required_fields": False, "matches_contract": False, "valid": False}
    left = report["left"]
    right = report["right"]
    abs_tol = report["abs_tol"]
    rel_tol = report["rel_tol"]
    if not all(isinstance(value, (int, float)) for value in (left, right, abs_tol, rel_tol)):
        return {"has_required_fields": True, "matches_contract": False, "valid": False}
    try:
        expected_close = close_enough(float(left), float(right), abs_tol=float(abs_tol), rel_tol=float(rel_tol))
    except ValueError:
        return {"has_required_fields": True, "matches_contract": False, "valid": False}

    finite_pair = isfinite(float(left)) and isfinite(float(right))
    expected_difference = abs(float(left) - float(right)) if finite_pair else None
    expected_threshold = (
        max(float(abs_tol), float(rel_tol) * max(abs(float(left)), abs(float(right))))
        if finite_pair
        else None
    )
    matches = (
        report.get("finite_pair") == finite_pair
        and report.get("difference") == expected_difference
        and report.get("threshold") == expected_threshold
        and report.get("close") == expected_close
    )
    return {"has_required_fields": True, "matches_contract": matches, "valid": matches}
