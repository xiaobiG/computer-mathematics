"""Small, replayable preconditioned conjugate-gradient experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class CgEvent:
    iteration: int
    alpha: float
    beta: float
    solution: tuple[float, ...]
    residual_norm: float
    preconditioned_residual_dot: float


def _validate_system(matrix: list[list[float]], right_side: list[float], symmetry_tolerance: float = 1e-12) -> None:
    if not matrix or not isinstance(matrix, list) or any(not isinstance(row, list) or len(row) != len(matrix) for row in matrix):
        raise ValueError("matrix must be a non-empty square list")
    if len(right_side) != len(matrix):
        raise ValueError("right_side must match the matrix dimension")
    values = [value for row in matrix for value in row] + list(right_side)
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) for value in values):
        raise ValueError("matrix and right_side must contain finite real values")
    for row in range(len(matrix)):
        if matrix[row][row] <= 0:
            raise ValueError("Jacobi preconditioner requires positive diagonal entries")
        for column in range(row):
            if abs(matrix[row][column] - matrix[column][row]) > symmetry_tolerance:
                raise ValueError("conjugate gradient requires a symmetric matrix")


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(value * vector[column] for column, value in enumerate(row)) for row in matrix]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(first * second for first, second in zip(left, right))


def _norm(vector: list[float]) -> float:
    return sqrt(_dot(vector, vector))


def preconditioned_conjugate_gradient(
    matrix: list[list[float]], right_side: list[float], tolerance: float = 1e-10, max_steps: int | None = None,
) -> tuple[list[float], list[CgEvent]]:
    """Solve a small SPD system with diagonal-preconditioned CG.

    Symmetry and positive diagonal are checked directly.  Positive definiteness
    is additionally witnessed at runtime by positive search-direction
    curvature; a failure is reported rather than being treated as convergence.
    """
    _validate_system(matrix, right_side)
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be a positive finite number")
    dimension = len(matrix)
    if max_steps is None:
        max_steps = 4 * dimension
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps <= 0:
        raise ValueError("max_steps must be a positive integer")
    solution = [0.0] * dimension
    residual = [float(value) for value in right_side]
    if _norm(residual) <= tolerance:
        return solution, []
    preconditioned = [residual[index] / matrix[index][index] for index in range(dimension)]
    direction = preconditioned[:]
    residual_dot = _dot(residual, preconditioned)
    events: list[CgEvent] = []
    for iteration in range(1, max_steps + 1):
        matrix_direction = _matvec(matrix, direction)
        curvature = _dot(direction, matrix_direction)
        if curvature <= 0 or not isfinite(curvature):
            raise ValueError("non-positive curvature: matrix is not positive definite on this direction")
        alpha = residual_dot / curvature
        solution = [solution[index] + alpha * direction[index] for index in range(dimension)]
        residual = [residual[index] - alpha * matrix_direction[index] for index in range(dimension)]
        residual_norm = _norm(residual)
        next_preconditioned = [residual[index] / matrix[index][index] for index in range(dimension)]
        next_residual_dot = _dot(residual, next_preconditioned)
        beta = 0.0 if residual_norm <= tolerance else next_residual_dot / residual_dot
        events.append(CgEvent(iteration, alpha, beta, tuple(solution), residual_norm, next_residual_dot))
        if residual_norm <= tolerance:
            return solution, events
        direction = [next_preconditioned[index] + beta * direction[index] for index in range(dimension)]
        preconditioned, residual_dot = next_preconditioned, next_residual_dot
    raise RuntimeError("preconditioned conjugate gradient did not meet tolerance within max_steps")


def pcg_trace_certificate(
    matrix: list[list[float]], right_side: list[float], solution: list[float], events: list[CgEvent],
    tolerance: float = 1e-10, max_steps: int | None = None,
) -> dict[str, bool]:
    """Replay the public PCG trace and its stopping residual."""
    empty = {"trace_matches_recomputation": False, "terminal_residual_is_small": False, "valid": False}
    if not isinstance(events, list) or not isinstance(solution, list):
        return empty
    try:
        expected_solution, expected_events = preconditioned_conjugate_gradient(matrix, right_side, tolerance, max_steps)
    except (ValueError, RuntimeError, TypeError):
        return empty
    trace_matches = events == expected_events and solution == expected_solution
    terminal_small = bool(events) and events[-1].residual_norm <= tolerance
    return {
        "trace_matches_recomputation": trace_matches,
        "terminal_residual_is_small": terminal_small,
        "valid": trace_matches and terminal_small,
    }
