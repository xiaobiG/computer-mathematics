"""Auditable Jacobi and Gauss--Seidel iterations for a small linear system."""

from __future__ import annotations

from math import isfinite
from typing import Literal


Method = Literal["jacobi", "gauss-seidel"]


def infinity_norm(values: list[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def residual(matrix: list[list[float]], estimate: list[float], right_side: list[float]) -> list[float]:
    """Return b - Ax, whose norm is an independently checkable stopping signal."""
    return [target - sum(entry * value for entry, value in zip(row, estimate)) for row, target in zip(matrix, right_side)]


def is_strictly_diagonally_dominant(matrix: list[list[float]]) -> bool:
    """Check a useful sufficient condition, not a necessary convergence test."""
    return all(abs(row[index]) > sum(abs(value) for column, value in enumerate(row) if column != index)
               for index, row in enumerate(matrix))


def solve_iteratively(
    matrix: list[list[float]],
    right_side: list[float],
    *,
    method: Method = "jacobi",
    residual_tol: float = 1e-10,
    step_tol: float = 1e-10,
    max_steps: int = 200,
) -> tuple[list[float], list[dict[str, float | int | list[float]]]]:
    """Solve Ax=b by stationary iteration and return the full convergence trace.

    The trace deliberately includes both residual and update norm.  Neither
    one alone establishes that a finite-precision iterate is a useful answer.
    """
    size = len(matrix)
    if size == 0 or len(right_side) != size or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be nonempty and square, and match right_side")
    if method not in ("jacobi", "gauss-seidel"):
        raise ValueError("method must be 'jacobi' or 'gauss-seidel'")
    if residual_tol <= 0 or step_tol <= 0 or max_steps <= 0:
        raise ValueError("tolerances and max_steps must be positive")
    if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in right_side):
        raise ValueError("matrix and right_side must be finite")
    if any(row[index] == 0 for index, row in enumerate(matrix)):
        raise ValueError("iteration requires a nonzero diagonal")

    estimate = [0.0] * size
    trace: list[dict[str, float | int | list[float]]] = []
    for step in range(1, max_steps + 1):
        next_estimate = estimate.copy()
        for row_index, row in enumerate(matrix):
            subtotal = sum(row[column] * (next_estimate[column] if method == "gauss-seidel" and column < row_index else estimate[column])
                           for column in range(size) if column != row_index)
            next_estimate[row_index] = (right_side[row_index] - subtotal) / row[row_index]
        if any(not isfinite(value) for value in next_estimate):
            raise RuntimeError("iteration became non-finite")
        step_norm = infinity_norm([new - old for new, old in zip(next_estimate, estimate)])
        residual_norm = infinity_norm(residual(matrix, next_estimate, right_side))
        trace.append({
            "step": step,
            "estimate": next_estimate.copy(),
            "step_norm": step_norm,
            "residual_norm": residual_norm,
        })
        if residual_norm <= residual_tol and step_norm <= step_tol * max(1.0, infinity_norm(next_estimate)):
            return next_estimate, trace
        estimate = next_estimate
    raise RuntimeError("iteration did not converge within max_steps")


def iteration_trace_certificate(
    matrix: list[list[float]],
    right_side: list[float],
    method: Method,
    solution: list[float],
    trace: list[dict[str, float | int | list[float]]],
    *,
    residual_tol: float = 1e-10,
    step_tol: float = 1e-10,
) -> dict[str, bool]:
    """Replay a converged stationary-iteration trace without trusting its labels.

    Each event stores the complete iterate, so the checker can recompute the
    selected Jacobi/Gauss--Seidel update, step norm and residual from the prior
    state.  The certificate establishes a faithful execution trace and the
    declared stopping condition; it does not turn a small residual into a
    forward-error guarantee for an ill-conditioned system.
    """
    try:
        if not trace or method not in ("jacobi", "gauss-seidel"):
            raise ValueError
        size = len(matrix)
        if size == 0 or len(right_side) != size or any(len(row) != size for row in matrix):
            raise ValueError
        if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in right_side):
            raise ValueError
        if any(row[index] == 0 for index, row in enumerate(matrix)):
            raise ValueError
        previous = [0.0] * size
        updates_match = True
        metrics_match = True
        for expected_step, event in enumerate(trace, start=1):
            candidate = previous.copy()
            for row_index, row in enumerate(matrix):
                subtotal = sum(
                    row[column] * (candidate[column] if method == "gauss-seidel" and column < row_index else previous[column])
                    for column in range(size) if column != row_index
                )
                candidate[row_index] = (right_side[row_index] - subtotal) / row[row_index]
            expected_step_norm = infinity_norm([new - old for new, old in zip(candidate, previous)])
            expected_residual_norm = infinity_norm(residual(matrix, candidate, right_side))
            if (event.get("step") != expected_step or event.get("estimate") != candidate):
                updates_match = False
            if event.get("step_norm") != expected_step_norm or event.get("residual_norm") != expected_residual_norm:
                metrics_match = False
            previous = candidate
        final_event = trace[-1]
        solution_matches_final_estimate = solution == previous
        stopping_condition_met = (
            isinstance(final_event.get("residual_norm"), (int, float))
            and isinstance(final_event.get("step_norm"), (int, float))
            and final_event["residual_norm"] <= residual_tol
            and final_event["step_norm"] <= step_tol * max(1.0, infinity_norm(previous))
        )
    except (AttributeError, KeyError, TypeError, ValueError):
        return {
            "updates_match": False,
            "metrics_match": False,
            "solution_matches_final_estimate": False,
            "stopping_condition_met": False,
            "valid": False,
        }
    return {
        "updates_match": updates_match,
        "metrics_match": metrics_match,
        "solution_matches_final_estimate": solution_matches_final_estimate,
        "stopping_condition_met": stopping_condition_met,
        "valid": all((updates_match, metrics_match, solution_matches_final_estimate, stopping_condition_met)),
    }
