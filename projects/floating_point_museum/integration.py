"""Composite quadrature rules with small, inspectable convergence reports."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable


Function = Callable[[float], float]


def _validate_interval(a: float, b: float, segments: int) -> None:
    if not isfinite(a) or not isfinite(b) or segments <= 0:
        raise ValueError("endpoints must be finite and segments must be positive")


def _evaluate(function: Function, point: float) -> float:
    value = float(function(point))
    if not isfinite(value):
        raise ValueError("integrand must return finite values at sampled points")
    return value


def composite_trapezoid(function: Function, a: float, b: float, segments: int) -> float:
    """Approximate the integral using piecewise-linear interpolation."""
    _validate_interval(a, b, segments)
    width = (b - a) / segments
    total = 0.5 * (_evaluate(function, a) + _evaluate(function, b))
    for index in range(1, segments):
        total += _evaluate(function, a + index * width)
    return width * total


def composite_simpson(function: Function, a: float, b: float, segments: int) -> float:
    """Approximate the integral using quadratic interpolation over paired intervals."""
    _validate_interval(a, b, segments)
    if segments % 2:
        raise ValueError("Simpson's rule requires an even segment count")
    width = (b - a) / segments
    total = _evaluate(function, a) + _evaluate(function, b)
    for index in range(1, segments):
        total += (4 if index % 2 else 2) * _evaluate(function, a + index * width)
    return width * total / 3.0


@dataclass(frozen=True)
class RefinementReport:
    trapezoid_error_ratio: float
    simpson_error_ratio: float


def refinement_report(function: Function, a: float, b: float, exact: float, segments: int) -> RefinementReport:
    """Compare absolute-error reduction after doubling an even grid resolution."""
    if segments <= 0 or segments % 2 or not isfinite(exact):
        raise ValueError("exact must be finite and segments must be positive and even")
    trapezoid_error = abs(composite_trapezoid(function, a, b, segments) - exact)
    trapezoid_refined_error = abs(composite_trapezoid(function, a, b, 2 * segments) - exact)
    simpson_error = abs(composite_simpson(function, a, b, segments) - exact)
    simpson_refined_error = abs(composite_simpson(function, a, b, 2 * segments) - exact)
    if trapezoid_refined_error == 0.0 or simpson_refined_error == 0.0:
        raise ValueError("error ratio is undefined when a sampled rule is exact")
    return RefinementReport(trapezoid_error / trapezoid_refined_error, simpson_error / simpson_refined_error)
