"""Composite quadrature rules with small, inspectable convergence reports."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Callable


Function = Callable[[float], float]
ENDPOINT_POWER_CONTRACT = "endpoint-power-improper-integral/v1"
UNBOUNDED_POWER_TAIL_CONTRACT = "unbounded-power-tail-integral/v1"


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
class AdaptiveSimpsonLeaf:
    """One terminal interval and the reason the adaptive search stopped."""

    left: float
    right: float
    estimate: float
    estimated_error: float | None
    tolerance_budget: float
    depth: int
    status: str


@dataclass(frozen=True)
class AdaptiveSimpsonReport:
    """Inspectable outcome of an adaptive Simpson run.

    ``estimated_error`` is Richardson's smooth-function estimate, not an
    absolute guarantee for a discontinuous or noisy integrand.  Callers must
    therefore inspect ``converged`` before treating the tolerance as met.
    """

    estimate: float
    estimated_error: float | None
    tolerance: float
    max_depth: int
    accepted_intervals: int
    evaluations: int
    max_evaluations: int | None
    evaluation_budget_exhausted: bool
    leaves: tuple[AdaptiveSimpsonLeaf, ...]
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
    max_evaluations: int | None = None,
) -> AdaptiveSimpsonReport:
    """Adapt Simpson's rule, returning an explicit certificate of its budget.

    A parent interval and its two children differ by roughly a factor of 15
    in the leading fourth-order error term.  The routine accepts a leaf only
    when ``abs(children - parent) / 15`` fits its share of the global absolute
    error budget.  Reaching ``max_depth`` or ``max_evaluations`` returns a
    non-converged report rather than silently claiming tolerance was achieved.
    Terminal leaves record which boundary accepted or stopped each interval.
    """
    _validate_interval(a, b, 1)
    if not isfinite(absolute_tolerance) or absolute_tolerance <= 0:
        raise ValueError("absolute_tolerance must be positive and finite")
    if not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth < 0:
        raise ValueError("max_depth must be a non-negative integer")
    if max_evaluations is not None and (
        not isinstance(max_evaluations, int) or isinstance(max_evaluations, bool) or max_evaluations < 3
    ):
        raise ValueError("max_evaluations must be None or an integer at least 3")

    evaluations = 0

    def evaluate(point: float) -> float:
        nonlocal evaluations
        if max_evaluations is not None and evaluations >= max_evaluations:
            raise RuntimeError("evaluation budget exhausted")
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
    ) -> tuple[float, float | None, list[AdaptiveSimpsonLeaf], bool, bool]:
        # A Simpson refinement needs two previously unseen quarter points.
        # Check both before evaluating so a capped run never has a half-made
        # refinement hidden from its trace.
        if max_evaluations is not None and evaluations + 2 > max_evaluations:
            return (
                parent,
                None,
                [AdaptiveSimpsonLeaf(left, right, parent, None, budget, depth, "evaluation_budget_exhausted")],
                False,
                True,
            )
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
            estimate = children + correction / 15.0
            return (
                estimate,
                estimated_error,
                [AdaptiveSimpsonLeaf(left, right, estimate, estimated_error, budget, depth, "accepted")],
                True,
                False,
            )
        if depth >= max_depth:
            return (
                children,
                estimated_error,
                [AdaptiveSimpsonLeaf(left, right, children, estimated_error, budget, depth, "max_depth_exhausted")],
                False,
                False,
            )
        left_result = refine(
            left, left_middle, middle, f_left, f_left_middle, f_middle, left_rule, budget / 2.0, depth + 1
        )
        right_result = refine(
            middle, right_middle, right, f_middle, f_right_middle, f_right, right_rule, budget / 2.0, depth + 1
        )
        combined_error = (
            None if left_result[1] is None or right_result[1] is None else left_result[1] + right_result[1]
        )
        return (
            left_result[0] + right_result[0],
            combined_error,
            left_result[2] + right_result[2],
            left_result[3] and right_result[3],
            left_result[4] or right_result[4],
        )

    midpoint = (a + b) / 2.0
    f_a, f_midpoint, f_b = evaluate(a), evaluate(midpoint), evaluate(b)
    parent = simpson_width(a, midpoint, b, f_a, f_midpoint, f_b)
    estimate, estimated_error, leaves, converged, evaluation_budget_exhausted = refine(
        a, midpoint, b, f_a, f_midpoint, f_b, parent, absolute_tolerance, 0
    )
    certificate = {
        "finite_estimate": isfinite(estimate),
        "estimated_error_within_tolerance": estimated_error is not None and estimated_error <= absolute_tolerance,
        "stopped_without_depth_limit": converged,
        "evaluation_budget_not_exhausted": not evaluation_budget_exhausted,
    }
    certificate["valid"] = all(certificate.values())
    return AdaptiveSimpsonReport(
        estimate,
        estimated_error,
        absolute_tolerance,
        max_depth,
        len(leaves),
        evaluations,
        max_evaluations,
        evaluation_budget_exhausted,
        tuple(leaves),
        converged,
        certificate,
    )


def adaptive_simpson_certificate(function: Function, a: float, b: float, report: object) -> bool:
    """Replay all policy parameters and reject altered adaptive traces."""
    if not isinstance(report, AdaptiveSimpsonReport):
        return False
    try:
        expected = adaptive_simpson(
            function,
            a,
            b,
            absolute_tolerance=report.tolerance,
            max_depth=report.max_depth,
            max_evaluations=report.max_evaluations,
        )
    except (TypeError, ValueError):
        return False
    return report == expected


def endpoint_power_integral_report(exponent: float, cutoffs: list[float]) -> dict[str, object]:
    """Expose the cutoff limit for ``integral_0^1 x**(-exponent) dx``.

    Generic quadrature cannot infer whether an arbitrary non-finite endpoint
    hides an integrable singularity.  This deliberately analytic family makes
    that distinction checkable: its antiderivative proves convergence exactly
    when ``exponent < 1``.
    """
    if (isinstance(exponent, bool) or not isinstance(exponent, (int, float))
            or not isfinite(exponent)):
        raise ValueError("exponent must be finite")
    if (not isinstance(cutoffs, list) or len(cutoffs) < 2
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not isfinite(value) or not 0.0 < value < 1.0 for value in cutoffs)):
        raise ValueError("cutoffs must contain at least two finite values in (0, 1)")
    normalized = tuple(float(value) for value in cutoffs)
    if any(left <= right for left, right in zip(normalized, normalized[1:])):
        raise ValueError("cutoffs must be strictly decreasing toward the singular endpoint")
    exponent = float(exponent)
    if exponent == 1.0:
        truncated = tuple(log(1.0 / cutoff) for cutoff in normalized)
    else:
        truncated = tuple((1.0 - cutoff ** (1.0 - exponent)) / (1.0 - exponent)
                          for cutoff in normalized)
    converges = exponent < 1.0
    return {
        "contract": ENDPOINT_POWER_CONTRACT,
        "integrand": "x**(-p) on (0, 1]",
        "exponent": exponent,
        "cutoffs": normalized,
        "truncated_integrals": truncated,
        "converges": converges,
        "limit": 1.0 / (1.0 - exponent) if converges else None,
        "tail_bounds": (tuple(cutoff ** (1.0 - exponent) / (1.0 - exponent) for cutoff in normalized)
                        if converges else None),
        "interpretation": ("integrable_endpoint_singularity_with_analytic_tail_bound"
                           if converges else "divergent_endpoint_singularity"),
    }


def endpoint_power_integral_certificate(exponent: float, cutoffs: list[float], report: object) -> bool:
    """Recompute the analytic cutoff report and reject changed limits or tails."""
    if not isinstance(report, dict) or report.get("contract") != ENDPOINT_POWER_CONTRACT:
        return False
    try:
        return report == endpoint_power_integral_report(exponent, cutoffs)
    except (TypeError, ValueError):
        return False


def unbounded_power_tail_report(exponent: float, cutoffs: list[float]) -> dict[str, object]:
    """Classify ``integral_0^infinity (1+x)**(-p) dx`` with analytic tails.

    A finite cutoff is not evidence that an unbounded integral converges.  This
    restricted family exposes the missing tail argument exactly: p > 1 has a
    finite limit and known omitted tail, while p <= 1 diverges as the cutoff
    increases.
    """
    if (isinstance(exponent, bool) or not isinstance(exponent, (int, float))
            or not isfinite(exponent)):
        raise ValueError("exponent must be finite")
    if (not isinstance(cutoffs, list) or len(cutoffs) < 2
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not isfinite(value) or value < 0.0 for value in cutoffs)):
        raise ValueError("cutoffs must contain at least two finite non-negative values")
    normalized = tuple(float(value) for value in cutoffs)
    if any(left >= right for left, right in zip(normalized, normalized[1:])):
        raise ValueError("cutoffs must be strictly increasing toward infinity")
    exponent = float(exponent)
    if exponent == 1.0:
        truncated = tuple(log(1.0 + cutoff) for cutoff in normalized)
    else:
        truncated = tuple(((1.0 + cutoff) ** (1.0 - exponent) - 1.0) / (1.0 - exponent)
                          for cutoff in normalized)
    converges = exponent > 1.0
    return {
        "contract": UNBOUNDED_POWER_TAIL_CONTRACT,
        "integrand": "(1+x)**(-p) on [0, infinity)",
        "exponent": exponent,
        "cutoffs": normalized,
        "truncated_integrals": truncated,
        "converges": converges,
        "limit": 1.0 / (exponent - 1.0) if converges else None,
        "tail_bounds": (tuple((1.0 + cutoff) ** (1.0 - exponent) / (exponent - 1.0)
                              for cutoff in normalized) if converges else None),
        "interpretation": ("unbounded_integral_with_analytic_tail_bound"
                           if converges else "divergent_unbounded_power_tail"),
    }


def unbounded_power_tail_certificate(exponent: float, cutoffs: list[float], report: object) -> bool:
    """Recompute the finite-cutoff and tail classification report."""
    if not isinstance(report, dict) or report.get("contract") != UNBOUNDED_POWER_TAIL_CONTRACT:
        return False
    try:
        return report == unbounded_power_tail_report(exponent, cutoffs)
    except (TypeError, ValueError):
        return False
