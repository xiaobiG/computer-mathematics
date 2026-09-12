"""A small, traceable power iteration for real symmetric matrices."""

from __future__ import annotations

from math import isfinite, sqrt


def _norm(vector: list[float]) -> float:
    return sqrt(sum(value * value for value in vector))


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(entry * value for entry, value in zip(row, vector)) for row in matrix]


def dominant_eigenpair(
    matrix: list[list[float]], *, residual_tol: float = 1e-10, max_steps: int = 200
) -> tuple[float, list[float], list[dict[str, float | int]]]:
    """Approximate the largest-magnitude eigenpair of a real symmetric matrix.

    The returned trace has a Rayleigh quotient and residual norm per iteration,
    so callers do not have to infer convergence from a visually stable vector.
    """
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be nonempty and square")
    if residual_tol <= 0 or max_steps <= 0:
        raise ValueError("residual_tol and max_steps must be positive")
    if any(not isfinite(value) for row in matrix for value in row):
        raise ValueError("matrix entries must be finite")
    if any(abs(matrix[row][column] - matrix[column][row]) > 1e-12
           for row in range(size) for column in range(size)):
        raise ValueError("teaching implementation requires a symmetric matrix")

    vector = [1.0 / sqrt(size)] * size
    trace: list[dict[str, float | int]] = []
    for step in range(1, max_steps + 1):
        image = _matvec(matrix, vector)
        image_norm = _norm(image)
        if image_norm == 0.0:
            raise ValueError("initial vector reached the zero eigenspace")
        vector = [value / image_norm for value in image]
        image = _matvec(matrix, vector)
        eigenvalue = sum(left * right for left, right in zip(vector, image))
        residual_norm = _norm([value - eigenvalue * coordinate for value, coordinate in zip(image, vector)])
        trace.append({"step": step, "eigenvalue": eigenvalue, "residual_norm": residual_norm})
        if residual_norm <= residual_tol:
            return eigenvalue, vector, trace
    raise RuntimeError("power iteration did not converge within max_steps")
