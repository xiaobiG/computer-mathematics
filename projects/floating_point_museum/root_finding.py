"""教学用割线法：无需导数，但保留有限迭代和分母保护。"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Callable


@dataclass(frozen=True)
class SecantEvent:
    """One secant update, with both inputs and the newly evaluated candidate."""

    iteration: int
    previous: float
    current: float
    previous_value: float
    current_value: float
    candidate: float
    candidate_value: float


def secant_trace(
    function: Callable[[float], float], left: float, right: float, *,
    residual_tol: float = 1e-12, step_tol: float = 1e-12, max_steps: int = 80,
) -> tuple[float, list[SecantEvent]]:
    """Find a root and record every finite-difference update for audit."""
    if max_steps <= 0 or residual_tol <= 0 or step_tol <= 0:
        raise ValueError("tolerances and max_steps must be positive")
    f_left, f_right = function(left), function(right)
    if not isfinite(f_left) or not isfinite(f_right):
        raise ValueError("initial function values must be finite")
    events: list[SecantEvent] = []
    for iteration in range(1, max_steps + 1):
        if abs(f_right) <= residual_tol:
            return right, events
        denominator = f_right - f_left
        if denominator == 0:
            raise RuntimeError("secant slope vanished")
        candidate = right - f_right * (right - left) / denominator
        if not isfinite(candidate):
            raise RuntimeError("secant step became non-finite")
        candidate_value = function(candidate)
        if not isfinite(candidate_value):
            raise RuntimeError("function became non-finite during iteration")
        events.append(SecantEvent(iteration, left, right, f_left, f_right, candidate, candidate_value))
        if abs(candidate_value) <= residual_tol:
            return candidate, events
        if abs(candidate - right) <= step_tol * max(1.0, abs(candidate)):
            raise RuntimeError("secant iteration stagnated away from a root")
        left, f_left = right, f_right
        right, f_right = candidate, candidate_value
    raise RuntimeError("secant method did not converge within max_steps")


def secant_trace_certificate(
    function: Callable[[float], float], events: list[SecantEvent], *, tolerance: float = 1e-12,
) -> bool:
    """Independently check secant interpolation and consecutive-event linkage."""
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    previous_event: SecantEvent | None = None
    for event in events:
        if not all(isfinite(value) for value in (
            event.previous, event.current, event.previous_value, event.current_value,
            event.candidate, event.candidate_value,
        )):
            return False
        denominator = event.current_value - event.previous_value
        if denominator == 0:
            return False
        expected = event.current - event.current_value * (event.current - event.previous) / denominator
        scale = max(1.0, abs(expected), abs(event.candidate))
        if abs(event.candidate - expected) > tolerance * scale:
            return False
        if (abs(function(event.previous) - event.previous_value) > tolerance
                or abs(function(event.current) - event.current_value) > tolerance
                or abs(function(event.candidate) - event.candidate_value) > tolerance):
            return False
        if previous_event and (event.previous != previous_event.current or event.current != previous_event.candidate):
            return False
        previous_event = event
    return True


def secant_solution_certificate(
    function: Callable[[float], float], left: float, right: float, root: float, events: list[SecantEvent], *,
    residual_tol: float = 1e-12, step_tol: float = 1e-12, max_steps: int = 80,
) -> bool:
    """Replay a full secant run, including its stopping condition and result.

    ``secant_trace_certificate`` checks algebraic consistency of event records.
    This stronger certificate also binds the first pair, tolerances, finite
    stopping rule and returned root to the supplied execution contract.
    """
    try:
        expected_root, expected_events = secant_trace(
            function, left, right,
            residual_tol=residual_tol,
            step_tol=step_tol,
            max_steps=max_steps,
        )
        return root == expected_root and events == expected_events
    except (ArithmeticError, TypeError, ValueError, ZeroDivisionError):
        return False


def secant_convergence_report(events: list[SecantEvent], reference_root: float) -> dict[str, object]:
    """Estimate local secant order from a known reference root for teaching.

    If errors follow ``e[k+1] ~= C e[k]**p``, three consecutive decreasing
    errors estimate ``p`` by ``log(e[k+1]/e[k]) / log(e[k]/e[k-1])``.  The
    reference root is deliberately an *external* benchmark: a production root
    finder normally does not know the exact root it seeks.
    """
    if not isinstance(reference_root, (int, float)) or isinstance(reference_root, bool) or not isfinite(reference_root):
        raise ValueError("reference_root must be finite")
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    errors: list[float] = []
    for event in events:
        if not isinstance(event, SecantEvent) or not isfinite(event.candidate):
            raise ValueError("events must contain finite SecantEvent candidates")
        errors.append(abs(event.candidate - reference_root))
    estimates: list[tuple[int, float]] = []
    for index in range(2, len(errors)):
        older, previous, current = errors[index - 2], errors[index - 1], errors[index]
        if 0.0 < current < previous < older:
            denominator = log(previous / older)
            if denominator != 0.0:
                estimates.append((events[index].iteration, log(current / previous) / denominator))
    return {
        "reference_root": float(reference_root),
        "candidate_errors": tuple(errors),
        "order_estimates": tuple(estimates),
    }


def secant_convergence_certificate(
    events: list[SecantEvent], reference_root: float, report: dict[str, object], *, tolerance: float = 1e-12,
) -> bool:
    """Recompute an observational convergence-order report without trusting it."""
    try:
        if tolerance <= 0.0 or not isfinite(tolerance) or not isinstance(report, dict):
            return False
        expected = secant_convergence_report(events, reference_root)
        if set(report) != set(expected):
            return False
        if abs(float(report["reference_root"]) - expected["reference_root"]) > tolerance:
            return False
        observed_errors = report["candidate_errors"]
        observed_orders = report["order_estimates"]
        if not isinstance(observed_errors, tuple) or not isinstance(observed_orders, tuple):
            return False
        if len(observed_errors) != len(expected["candidate_errors"]) or len(observed_orders) != len(expected["order_estimates"]):
            return False
        errors_match = all(isinstance(value, (int, float)) and isfinite(value)
                           and abs(value - expected_value) <= tolerance * max(1.0, abs(expected_value))
                           for value, expected_value in zip(observed_errors, expected["candidate_errors"]))
        orders_match = all(isinstance(value, tuple) and len(value) == 2
                           and value[0] == expected_value[0]
                           and isinstance(value[1], (int, float)) and isfinite(value[1])
                           and abs(value[1] - expected_value[1]) <= tolerance * max(1.0, abs(expected_value[1]))
                           for value, expected_value in zip(observed_orders, expected["order_estimates"]))
        return errors_match and orders_match
    except (TypeError, ValueError):
        return False


def secant_root(
    function: Callable[[float], float], left: float, right: float, *,
    residual_tol: float = 1e-12, step_tol: float = 1e-12, max_steps: int = 80,
) -> float:
    """Return only the root from :func:`secant_trace` for a compact API."""
    root, _ = secant_trace(function, left, right, residual_tol=residual_tol,
                           step_tol=step_tol, max_steps=max_steps)
    return root


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


def safeguarded_newton_trace_certificate(
    function: Callable[[float], float], derivative: Callable[[float], float],
    left: float, right: float, initial: float, root: float, events: list[NewtonEvent], *,
    residual_tol: float = 1e-12, derivative_tol: float = 1e-14,
) -> bool:
    """Replay a successful hybrid Newton trace without trusting its events.

    For each recorded round the verifier recomputes the Newton proposal, checks
    why bisection was selected when necessary, and re-applies the sign-change
    bracket update. It certifies this finite execution; continuity and the
    intermediate-value theorem are still the mathematical reason a bracketed
    sign change contains a root.
    """
    if (not all(isfinite(value) for value in (
        left, right, initial, root, residual_tol, derivative_tol,
    )) or left >= right or not left <= initial <= right
            or residual_tol <= 0 or derivative_tol <= 0):
        return False
    try:
        left_value, right_value = function(left), function(right)
        if not isfinite(left_value) or not isfinite(right_value):
            return False
        if abs(left_value) <= residual_tol:
            return not events and root == left
        if abs(right_value) <= residual_tol:
            return not events and root == right
        if left_value * right_value >= 0:
            return False

        current = initial
        for iteration, event in enumerate(events, start=1):
            current_value = function(current)
            if not isfinite(current_value) or abs(current_value) <= residual_tol:
                return False
            slope = derivative(current)
            expected_method = "bisection"
            candidate = (left + right) / 2.0
            if isfinite(slope) and abs(slope) > derivative_tol:
                proposal = current - current_value / slope
                if isfinite(proposal) and left < proposal < right:
                    candidate = proposal
                    expected_method = "newton"
            candidate_value = function(candidate)
            if not isfinite(candidate_value):
                return False
            if candidate_value == 0.0:
                next_left = next_right = candidate
                next_left_value = next_right_value = candidate_value
            elif (left_value < 0 < candidate_value) or (candidate_value < 0 < left_value):
                next_left, next_left_value = left, left_value
                next_right, next_right_value = candidate, candidate_value
            else:
                next_left, next_left_value = candidate, candidate_value
                next_right, next_right_value = right, right_value
            expected = NewtonEvent(
                iteration, expected_method, candidate, candidate_value,
                next_left, next_right, next_left_value, next_right_value,
            )
            if event != expected:
                return False
            left, right = next_left, next_right
            left_value, right_value = next_left_value, next_right_value
            current = candidate
        return root == current and abs(function(root)) <= residual_tol
    except (ArithmeticError, ValueError, ZeroDivisionError):
        return False
