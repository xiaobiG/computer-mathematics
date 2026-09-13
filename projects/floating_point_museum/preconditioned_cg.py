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
        for column in range(row):
            if abs(matrix[row][column] - matrix[column][row]) > symmetry_tolerance:
                raise ValueError("conjugate gradient requires a symmetric matrix")
    spd = spd_cholesky_report(matrix)
    if not spd["positive_definite"]:
        raise ValueError("conjugate gradient requires a positive-definite matrix")


def spd_cholesky_report(matrix: list[list[float]], symmetry_tolerance: float = 1e-12) -> dict[str, object]:
    """Expose Cholesky pivots as a finite, replayable SPD diagnostic."""
    if not matrix or not isinstance(matrix, list) or any(not isinstance(row, list) or len(row) != len(matrix) for row in matrix):
        raise ValueError("matrix must be a non-empty square list")
    values = [value for row in matrix for value in row]
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) for value in values):
        raise ValueError("matrix must contain finite real values")
    for row in range(len(matrix)):
        for column in range(row):
            if abs(matrix[row][column] - matrix[column][row]) > symmetry_tolerance:
                raise ValueError("Cholesky SPD diagnostic requires a symmetric matrix")

    dimension = len(matrix)
    lower = [[0.0] * dimension for _ in range(dimension)]
    pivots: list[float] = []
    for row in range(dimension):
        pivot = float(matrix[row][row]) - sum(lower[row][column] ** 2 for column in range(row))
        pivots.append(pivot)
        if pivot <= 0 or not isfinite(pivot):
            return {
                "matrix": [[float(value) for value in current_row] for current_row in matrix],
                "positive_definite": False,
                "cholesky_pivots": pivots,
                "failing_pivot_index": row,
                "lower_factor": None,
            }
        lower[row][row] = sqrt(pivot)
        for target_row in range(row + 1, dimension):
            numerator = float(matrix[target_row][row]) - sum(
                lower[target_row][column] * lower[row][column] for column in range(row)
            )
            lower[target_row][row] = numerator / lower[row][row]
    return {
        "matrix": [[float(value) for value in current_row] for current_row in matrix],
        "positive_definite": True,
        "cholesky_pivots": pivots,
        "failing_pivot_index": None,
        "lower_factor": lower,
    }


def spd_cholesky_certificate(matrix: list[list[float]], report: object) -> bool:
    """Rebuild the Cholesky diagnostic so a claimed SPD premise cannot be forged."""
    if not isinstance(report, dict):
        return False
    try:
        return report == spd_cholesky_report(matrix)
    except (TypeError, ValueError):
        return False


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(value * vector[column] for column, value in enumerate(row)) for row in matrix]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(first * second for first, second in zip(left, right))


def _norm(vector: list[float]) -> float:
    return sqrt(_dot(vector, vector))


def _apply_preconditioner(matrix: list[list[float]], residual: list[float], preconditioner: str) -> list[float]:
    if preconditioner == "identity":
        return residual[:]
    if preconditioner == "jacobi":
        return [residual[index] / matrix[index][index] for index in range(len(residual))]
    raise ValueError("preconditioner must be 'identity' or 'jacobi'")


def preconditioned_conjugate_gradient(
    matrix: list[list[float]], right_side: list[float], tolerance: float = 1e-10, max_steps: int | None = None,
    *, preconditioner: str = "jacobi",
) -> tuple[list[float], list[CgEvent]]:
    """Solve a small SPD system with identity or diagonal-Jacobi CG.

    Symmetry and positive definiteness are checked before iteration.  The
    latter uses real Cholesky pivots, rather than incorrectly treating a
    positive diagonal as sufficient evidence of positive definiteness.
    """
    _validate_system(matrix, right_side)
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be a positive finite number")
    dimension = len(matrix)
    if max_steps is None:
        max_steps = 4 * dimension
    if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps <= 0:
        raise ValueError("max_steps must be a positive integer")
    if preconditioner not in {"identity", "jacobi"}:
        raise ValueError("preconditioner must be 'identity' or 'jacobi'")
    solution = [0.0] * dimension
    residual = [float(value) for value in right_side]
    if _norm(residual) <= tolerance:
        return solution, []
    preconditioned = _apply_preconditioner(matrix, residual, preconditioner)
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
        next_preconditioned = _apply_preconditioner(matrix, residual, preconditioner)
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
    tolerance: float = 1e-10, max_steps: int | None = None, *, preconditioner: str = "jacobi",
) -> dict[str, bool]:
    """Replay the public PCG trace and its stopping residual."""
    empty = {"trace_matches_recomputation": False, "terminal_residual_is_small": False, "valid": False}
    if not isinstance(events, list) or not isinstance(solution, list):
        return empty
    try:
        expected_solution, expected_events = preconditioned_conjugate_gradient(
            matrix, right_side, tolerance, max_steps, preconditioner=preconditioner,
        )
    except (ValueError, RuntimeError, TypeError):
        return empty
    trace_matches = events == expected_events and solution == expected_solution
    terminal_small = bool(events) and events[-1].residual_norm <= tolerance
    return {
        "trace_matches_recomputation": trace_matches,
        "terminal_residual_is_small": terminal_small,
        "valid": trace_matches and terminal_small,
    }
