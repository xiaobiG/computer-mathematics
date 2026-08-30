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


@dataclass(frozen=True)
class AdaptiveSimpsonReport:
    """Inspectable outcome of an adaptive Simpson run.

    ``estimated_error`` is Richardson's smooth-function estimate, not an
    absolute guarantee for a discontinuous or noisy integrand.  Callers must
    therefore inspect ``converged`` before treating the tolerance as met.
    """

    estimate: float
    estimated_error: float
    tolerance: float
    accepted_intervals: int
    evaluations: int
    converged: bool
    certificate: dict[str, bool]


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


def adaptive_simpson(
    function: Function,
    a: float,
    b: float,
    absolute_tolerance: float = 1e-8,
    max_depth: int = 20,
) -> AdaptiveSimpsonReport:
    """Adapt Simpson's rule, returning an explicit certificate of its budget.

    A parent interval and its two children differ by roughly a factor of 15
    in the leading fourth-order error term.  The routine accepts a leaf only
    when ``abs(children - parent) / 15`` fits its share of the global absolute
    error budget.  Reaching ``max_depth`` returns a non-converged report rather
    than silently claiming that the requested tolerance was achieved.
    """
    _validate_interval(a, b, 1)
    if not isfinite(absolute_tolerance) or absolute_tolerance <= 0:
        raise ValueError("absolute_tolerance must be positive and finite")
    if not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth < 0:
        raise ValueError("max_depth must be a non-negative integer")

    evaluations = 0

    def evaluate(point: float) -> float:
        nonlocal evaluations
        evaluations += 1
        return _evaluate(function, point)

    def simpson_width(left: float, middle: float, right: float, f_left: float, f_middle: float, f_right: float) -> float:
        return (right - left) * (f_left + 4.0 * f_middle + f_right) / 6.0

    def refine(
        left: float,
        middle: float,
        right: float,
        f_left: float,
        f_middle: float,
        f_right: float,
        parent: float,
        budget: float,
        depth: int,
    ) -> tuple[float, float, int, bool]:
        left_middle = (left + middle) / 2.0
        right_middle = (middle + right) / 2.0
        f_left_middle = evaluate(left_middle)
        f_right_middle = evaluate(right_middle)
        left_rule = simpson_width(left, left_middle, middle, f_left, f_left_middle, f_middle)
        right_rule = simpson_width(middle, right_middle, right, f_middle, f_right_middle, f_right)
        children = left_rule + right_rule
        correction = children - parent
        estimated_error = abs(correction) / 15.0
        if estimated_error <= budget:
            return children + correction / 15.0, estimated_error, 1, True
        if depth >= max_depth:
            return children, estimated_error, 1, False
        left_result = refine(
            left, left_middle, middle, f_left, f_left_middle, f_middle, left_rule, budget / 2.0, depth + 1
        )
        right_result = refine(
            middle, right_middle, right, f_middle, f_right_middle, f_right, right_rule, budget / 2.0, depth + 1
        )
        return (
            left_result[0] + right_result[0],
            left_result[1] + right_result[1],
            left_result[2] + right_result[2],
            left_result[3] and right_result[3],
        )

    midpoint = (a + b) / 2.0
    f_a, f_midpoint, f_b = evaluate(a), evaluate(midpoint), evaluate(b)
    parent = simpson_width(a, midpoint, b, f_a, f_midpoint, f_b)
    estimate, estimated_error, accepted_intervals, converged = refine(
        a, midpoint, b, f_a, f_midpoint, f_b, parent, absolute_tolerance, 0
    )
    certificate = {
        "finite_estimate": isfinite(estimate),
        "estimated_error_within_tolerance": estimated_error <= absolute_tolerance,
        "stopped_without_depth_limit": converged,
    }
    certificate["valid"] = all(certificate.values())
    return AdaptiveSimpsonReport(
        estimate,
        estimated_error,
        absolute_tolerance,
        accepted_intervals,
        evaluations,
        converged,
        certificate,
    )
