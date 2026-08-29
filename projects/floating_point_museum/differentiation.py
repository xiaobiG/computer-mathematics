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


def _finite_real(value: float, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


def central_difference(function: Function, point: float, step: float) -> float:
    """Approximate f'(x) by the second-order symmetric finite difference."""
    point = _finite_real(point, "point")
    step = _finite_real(step, "step")
    if step <= 0:
        raise ValueError("step must be positive")
    left, right = float(function(point - step)), float(function(point + step))
    if not isfinite(left) or not isfinite(right):
        raise ValueError("function must be finite on both sides of the point")
    return (right - left) / (2.0 * step)


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
