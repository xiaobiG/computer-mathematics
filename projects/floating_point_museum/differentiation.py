"""Finite-difference step scans that expose truncation and rounding tradeoffs."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Iterable


Function = Callable[[float], float]


@dataclass(frozen=True)
class DifferenceSample:
    exponent: int
    step: float
    estimate: float
    absolute_error: float


@dataclass(frozen=True)
class DifferenceEstimate:
    """One finite-difference estimate and its error against a supplied oracle."""

    method: str
    estimate: float
    absolute_error: float


def _finite_real(value: float, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


def _function_value(function: Function, point: float) -> float:
    try:
        value = float(function(point))
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("function is not evaluable at the required stencil point") from error
    if not isfinite(value):
        raise ValueError("function must be finite at every required stencil point")
    return value


def central_difference(function: Function, point: float, step: float) -> float:
    """Approximate f'(x) by the second-order symmetric finite difference."""
    point = _finite_real(point, "point")
    step = _finite_real(step, "step")
    if step <= 0:
        raise ValueError("step must be positive")
    left, right = _function_value(function, point - step), _function_value(function, point + step)
    return (right - left) / (2.0 * step)


def forward_difference(function: Function, point: float, step: float) -> float:
    """Approximate f'(x) using the first-order one-sided forward difference."""
    point = _finite_real(point, "point")
    step = _finite_real(step, "step")
    if step <= 0:
        raise ValueError("step must be positive")
    return (_function_value(function, point + step) - _function_value(function, point)) / step


def finite_difference_stencil_comparison(
    function: Function, exact_derivative: Function, point: float, step: float,
) -> dict[str, object]:
    """Expose the domain tradeoff between forward and centered stencils.

    A centered stencil is retained when both sides are evaluable; otherwise the
    report makes its absence explicit and leaves the one-sided approximation
    visible.  It does not claim that either stencil is universally optimal:
    roundoff, noise, scaling, and the selected step remain separate choices.
    """
    point = _finite_real(point, "point")
    step = _finite_real(step, "step")
    if step <= 0:
        raise ValueError("step must be positive")
    exact = _function_value(exact_derivative, point)
    forward = forward_difference(function, point, step)
    forward_estimate = DifferenceEstimate("forward", forward, abs(forward - exact))
    try:
        central = central_difference(function, point, step)
    except ValueError:
        central_estimate = None
    else:
        central_estimate = DifferenceEstimate("central", central, abs(central - exact))
    return {
        "exact_derivative": exact,
        "forward": forward_estimate,
        "central": central_estimate,
        "central_available": central_estimate is not None,
        "choice_boundary": (
            "central_is_available_when_both_sides_of_the_stencil_are_finite; "
            "otherwise_use_a_one_sided_or_reparameterized_method"
        ),
    }


def central_difference_report(
    function: Function, exact_derivative: Function, point: float, exponents: Iterable[int] = range(1, 17),
) -> dict[str, object]:
    """Scan decimal steps and report observed second-order and rebound evidence."""
    point = _finite_real(point, "point")
    powers = list(exponents)
    if len(powers) < 3 or any(not isinstance(power, int) or isinstance(power, bool) or power <= 0 for power in powers):
        raise ValueError("at least three positive integer exponents are required")
    exact = _finite_real(exact_derivative(point), "exact derivative")
    samples = tuple(
        DifferenceSample(power, 10.0 ** (-power), central_difference(function, point, 10.0 ** (-power)), 0.0)
        for power in powers
    )
    samples = tuple(
        DifferenceSample(sample.exponent, sample.step, sample.estimate, abs(sample.estimate - exact))
        for sample in samples
    )
    best = min(samples, key=lambda sample: sample.absolute_error)
    first, second = samples[0], samples[1]
    coarse_error_ratio = first.absolute_error / second.absolute_error if second.absolute_error else float("inf")
    certificate = {
        "coarse_steps_show_second_order_trend": 25.0 <= coarse_error_ratio <= 400.0,
        "small_steps_rebound_after_best": samples[-1].absolute_error > best.absolute_error,
        "best_step_is_in_scan": best in samples,
    }
    certificate["valid"] = all(certificate.values())
    return {
        "exact_derivative": exact,
        "samples": samples,
        "best": best,
        "coarse_error_ratio": coarse_error_ratio,
        "certificate": certificate,
    }
