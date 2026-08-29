"""Small, explicit error-analysis formulas for numerical-computing lessons."""

from __future__ import annotations

from math import inf, isfinite


def _finite(value: float, name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError(f"{name} must be finite")


def absolute_error(reference: float, approximation: float) -> float:
    """Return |approximation - reference| after rejecting non-finite inputs."""
    _finite(reference, "reference")
    _finite(approximation, "approximation")
    return abs(approximation - reference)


def relative_error(reference: float, approximation: float) -> float:
    """Return relative error; it is undefined when the reference is zero."""
    _finite(reference, "reference")
    _finite(approximation, "approximation")
    if reference == 0.0:
        raise ValueError("relative error is undefined for a zero reference")
    return absolute_error(reference, approximation) / abs(reference)


def product_relative_error_bound(left_relative: float, right_relative: float) -> float:
    """Return (1+e_left)(1+e_right)-1 for non-negative relative bounds."""
    _finite(left_relative, "left_relative")
    _finite(right_relative, "right_relative")
    if left_relative < 0.0 or right_relative < 0.0:
        raise ValueError("relative error bounds must be non-negative")
    return (1.0 + left_relative) * (1.0 + right_relative) - 1.0


def subtraction_condition_number(left: float, right: float) -> float:
    """Return (|a|+|b|)/|a-b|, exposing cancellation sensitivity."""
    _finite(left, "left")
    _finite(right, "right")
    difference = left - right
    return inf if difference == 0.0 else (abs(left) + abs(right)) / abs(difference)
