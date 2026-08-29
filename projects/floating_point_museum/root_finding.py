"""教学用割线法：无需导数，但保留有限迭代和分母保护。"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable


def secant_root(
    function: Callable[[float], float], left: float, right: float, *,
    residual_tol: float = 1e-12, step_tol: float = 1e-12, max_steps: int = 80,
) -> float:
    """Find a root from two distinct function values, or report a failed contract."""
    if max_steps <= 0 or residual_tol <= 0 or step_tol <= 0:
        raise ValueError("tolerances and max_steps must be positive")
    f_left, f_right = function(left), function(right)
    if not isfinite(f_left) or not isfinite(f_right):
        raise ValueError("initial function values must be finite")
    for _ in range(max_steps):
        if abs(f_right) <= residual_tol:
            return right
        denominator = f_right - f_left
        if denominator == 0:
            raise RuntimeError("secant slope vanished")
        candidate = right - f_right * (right - left) / denominator
        if not isfinite(candidate):
            raise RuntimeError("secant step became non-finite")
        if abs(candidate - right) <= step_tol * max(1.0, abs(candidate)):
            if abs(function(candidate)) <= residual_tol:
                return candidate
            raise RuntimeError("secant iteration stagnated away from a root")
        left, f_left = right, f_right
        right, f_right = candidate, function(candidate)
        if not isfinite(f_right):
            raise RuntimeError("function became non-finite during iteration")
    raise RuntimeError("secant method did not converge within max_steps")


@dataclass(frozen=True)
class NewtonEvent:
    """One accepted hybrid step and the bracket retained after that step."""

    iteration: int
    method: str
    candidate: float
    residual: float
    left: float
    right: float
    left_value: float
    right_value: float


def safeguarded_newton_trace(
    function: Callable[[float], float], derivative: Callable[[float], float],
    left: float, right: float, initial: float, *, residual_tol: float = 1e-12,
    step_tol: float = 1e-12, derivative_tol: float = 1e-14, max_steps: int = 80,
) -> tuple[float, list[NewtonEvent]]:
    """Find a bracketed root, recording Newton steps and bisection fallbacks.

    The returned trace is a certificate: each event stores a bracket whose
    endpoint values have opposite signs (or one is exactly zero).  A Newton
    proposal outside that bracket, or with an unusably small derivative, is
    replaced by bisection.
    """
    if (not all(isfinite(value) for value in (left, right, initial, residual_tol, step_tol, derivative_tol))
            or left >= right or not left <= initial <= right
            or residual_tol <= 0 or step_tol <= 0 or derivative_tol <= 0
            or not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps <= 0):
        raise ValueError("finite ordered bracket, initial point, positive tolerances and steps are required")
    left_value, right_value = function(left), function(right)
    if not isfinite(left_value) or not isfinite(right_value):
        raise ValueError("bracket endpoint values must be finite")
    if abs(left_value) <= residual_tol:
        return left, []
    if abs(right_value) <= residual_tol:
        return right, []
    if left_value * right_value >= 0:
        raise ValueError("bracket endpoints must have opposite signs")

    current = initial
    events: list[NewtonEvent] = []
    for iteration in range(1, max_steps + 1):
        current_value = function(current)
        if not isfinite(current_value):
            raise RuntimeError("function became non-finite during iteration")
        if abs(current_value) <= residual_tol:
            return current, events
        slope = derivative(current)
        candidate = float("nan")
        method = "bisection"
        if isfinite(slope) and abs(slope) > derivative_tol:
            proposal = current - current_value / slope
            if isfinite(proposal) and left < proposal < right:
                candidate = proposal
                method = "newton"
        if method == "bisection":
            candidate = (left + right) / 2.0
        candidate_value = function(candidate)
        if not isfinite(candidate_value):
            raise RuntimeError("function became non-finite at candidate")
        if candidate_value == 0.0:
            left = right = candidate
            left_value = right_value = candidate_value
        elif (left_value < 0 < candidate_value) or (candidate_value < 0 < left_value):
            right, right_value = candidate, candidate_value
        else:
            left, left_value = candidate, candidate_value
        event = NewtonEvent(iteration, method, candidate, candidate_value,
                            left, right, left_value, right_value)
        events.append(event)
        if abs(candidate_value) <= residual_tol:
            return candidate, events
        if abs(candidate - current) <= step_tol * max(1.0, abs(candidate)):
            raise RuntimeError("hybrid Newton iteration stagnated away from a root")
        current = candidate
    raise RuntimeError("hybrid Newton iteration did not converge within max_steps")
