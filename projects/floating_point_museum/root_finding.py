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


def _finite_scalar(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _parse_reader_root_task(task: object, derivative: Callable[[float], float] | None) -> dict[str, object]:
    """Validate a reader-authored root-finding contract before selecting a method."""
    common_fields = {
        "strategy", "derivative_availability", "acceptance_invariant",
        "left", "right", "residual_tol", "step_tol", "max_steps",
    }
    if not isinstance(task, dict):
        raise ValueError("root task must be a mapping")
    strategy = task["strategy"]
    availability = task["derivative_availability"]
    expected_invariant = {
        "preserve_sign_change_bracket": "finite_residual_and_retained_sign_change_bracket",
        "local_residual_search": "finite_residual_without_global_bracket_claim",
    }
    if strategy not in expected_invariant:
        raise ValueError("strategy must preserve a sign-change bracket or request a local residual search")
    required = common_fields | ({"initial"} if strategy == "preserve_sign_change_bracket" else set())
    if set(task) != required:
        raise ValueError("the bracketed Newton contract requires initial; the secant contract must not include it")
    if task["acceptance_invariant"] != expected_invariant[strategy]:
        raise ValueError("acceptance_invariant does not match the requested root-finding guarantee")
    if availability not in {"available", "unavailable"}:
        raise ValueError("derivative_availability must be available or unavailable")
    if (availability == "available") != (derivative is not None):
        raise ValueError("declared derivative availability must match the supplied derivative")
    if strategy == "preserve_sign_change_bracket" and derivative is None:
        raise ValueError("a safeguarded Newton task requires a derivative")
    if strategy == "local_residual_search" and derivative is not None:
        raise ValueError("a local secant task must not silently discard an available derivative")
    left, right = task["left"], task["right"]
    if not all(_finite_scalar(value) for value in (left, right)) or left >= right:
        raise ValueError("left and right must be finite with left < right")
    initial = task.get("initial")
    if strategy == "preserve_sign_change_bracket" and (
        not _finite_scalar(initial) or not left <= initial <= right
    ):
        raise ValueError("a bracketed Newton task needs a finite initial point inside its bracket")
    if not all(_finite_scalar(task[key]) for key in ("residual_tol", "step_tol")):
        raise ValueError("tolerances must be finite scalars")
    if task["residual_tol"] <= 0 or task["step_tol"] <= 0:
        raise ValueError("tolerances must be positive")
    max_steps = task["max_steps"]
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps <= 0:
        raise ValueError("max_steps must be a positive integer")
    return {
        "strategy": strategy,
        "left": float(left), "right": float(right),
        "initial": float(initial) if initial is not None else None,
        "residual_tol": float(task["residual_tol"]), "step_tol": float(task["step_tol"]),
        "max_steps": max_steps,
    }


def diagnose_root_task(
    function: Callable[[float], float], task: object, *, derivative: Callable[[float], float] | None = None,
) -> dict[str, object]:
    """Run the method warranted by a reader-declared root-finding contract.

    A sign change is finite evidence only after continuity is supplied from the
    mathematical model; this diagnostic cannot infer continuity or uniqueness.
    It does make the difference between a retained bracket and a merely local
    residual explicit before calling Newton or secant.
    """
    if not callable(function) or (derivative is not None and not callable(derivative)):
        raise ValueError("function and supplied derivative must be callable")
    parsed = _parse_reader_root_task(task, derivative)
    left, right = parsed["left"], parsed["right"]
    residual_tol, step_tol, max_steps = parsed["residual_tol"], parsed["step_tol"], parsed["max_steps"]
    if parsed["strategy"] == "preserve_sign_change_bracket":
        left_value, right_value = function(left), function(right)
        if not isfinite(left_value) or not isfinite(right_value) or left_value * right_value > 0:
            raise ValueError("a bracket guarantee requires finite endpoint values with opposite signs or an endpoint root")
        root, events = safeguarded_newton_trace(
            function, derivative, left, right, parsed["initial"],
            residual_tol=residual_tol, step_tol=step_tol, max_steps=max_steps,
        )
        root_value = function(root)
        retained = (not events and left_value * right_value <= 0) or all(
            event.left_value * event.right_value <= 0 for event in events
        )
        return {
            "recommended_method": "safeguarded_newton",
            "root": root,
            "residual": abs(root_value),
            "steps": len(events),
            "reader_invariant": "finite residual and a sign-change bracket retained at every accepted step",
            "invariant_holds": isfinite(root_value) and abs(root_value) <= residual_tol and retained,
            "first_missing_premise": "continuity is still an external model assumption behind a sign-change root claim",
            "fallback_steps": sum(event.method == "bisection" for event in events),
        }

    root, events = secant_trace(
        function, left, right,
        residual_tol=residual_tol, step_tol=step_tol, max_steps=max_steps,
    )
    root_value = function(root)
    return {
        "recommended_method": "secant",
        "root": root,
        "residual": abs(root_value),
        "steps": len(events),
        "reader_invariant": "finite residual only; no global bracket guarantee is claimed",
        "invariant_holds": isfinite(root_value) and abs(root_value) <= residual_tol,
        "first_missing_premise": "no sign-change bracket is retained, so global root containment is not established",
        "fallback_steps": None,
    }


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


@dataclass(frozen=True)
class BracketedRootPositionReview:
    """A position-error budget derived from a verified sign-change bracket."""

    root: float
    source_steps: int
    final_left: float
    final_right: float
    bracket_width: float
    root_position_error_upper_bound: float
    position_error_budget: float
    position_budget_status: str
    continuity_assumption: str
    automatic_action: str


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


def bracketed_root_position_review(
    function: Callable[[float], float], derivative: Callable[[float], float],
    left: float, right: float, initial: float, root: float, events: list[NewtonEvent], *,
    position_error_budget: float, continuous_on_initial_bracket: bool,
    residual_tol: float = 1e-12, derivative_tol: float = 1e-14,
) -> BracketedRootPositionReview:
    """Turn a verified bracketed-Newton artifact into a position-bound review.

    A finite trace cannot establish continuity; the caller must declare it as a
    model premise.  Under that premise, the retained sign-change interval
    contains a root, so its maximum distance from the returned estimate is a
    conservative position-error upper bound.  Small residual alone supplies
    no such bound.
    """
    if (not _finite_scalar(position_error_budget) or position_error_budget < 0.0):
        raise ValueError("position_error_budget must be a finite non-negative number")
    if continuous_on_initial_bracket is not True:
        raise ValueError("a position bound requires an explicit continuity declaration")
    if not safeguarded_newton_trace_certificate(
        function, derivative, left, right, initial, root, events,
        residual_tol=residual_tol, derivative_tol=derivative_tol,
    ):
        raise ValueError("root trace does not replay under the stated bracket contract")
    if events:
        final_left, final_right = events[-1].left, events[-1].right
    else:
        final_left, final_right = float(left), float(right)
    upper_bound = max(abs(root - final_left), abs(final_right - root))
    budget = float(position_error_budget)
    return BracketedRootPositionReview(
        root=float(root),
        source_steps=len(events),
        final_left=final_left,
        final_right=final_right,
        bracket_width=final_right - final_left,
        root_position_error_upper_bound=upper_bound,
        position_error_budget=budget,
        position_budget_status=("within_position_error_budget" if upper_bound <= budget
                                else "exceeds_position_error_budget"),
        continuity_assumption="declared_not_proven_by_finite_trace",
        automatic_action="none",
    )


def bracketed_root_position_review_certificate(
    function: Callable[[float], float], derivative: Callable[[float], float],
    left: float, right: float, initial: float, root: float, events: list[NewtonEvent],
    position_error_budget: float, review: object, *, continuous_on_initial_bracket: bool,
    residual_tol: float = 1e-12, derivative_tol: float = 1e-14,
) -> bool:
    """Rebuild a source-bound bracket position review and reject changed bounds."""
    if not isinstance(review, BracketedRootPositionReview):
        return False
    try:
        expected = bracketed_root_position_review(
            function, derivative, left, right, initial, root, events,
            position_error_budget=position_error_budget,
            continuous_on_initial_bracket=continuous_on_initial_bracket,
            residual_tol=residual_tol, derivative_tol=derivative_tol,
        )
    except ValueError:
        return False
    return review == expected
