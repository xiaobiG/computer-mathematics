"""A small, traceable power iteration for real symmetric matrices."""

from __future__ import annotations

from math import isfinite, sqrt


def _norm(vector: list[float]) -> float:
    return sqrt(sum(value * value for value in vector))


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(entry * value for entry, value in zip(row, vector)) for row in matrix]


def dominant_eigenpair(
    matrix: list[list[float]], *, residual_tol: float = 1e-10, max_steps: int = 200,
    initial_vector: list[float] | None = None,
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

    if initial_vector is None:
        vector = [1.0 / sqrt(size)] * size
    else:
        if (not isinstance(initial_vector, list) or len(initial_vector) != size
                or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                       for value in initial_vector)):
            raise ValueError("initial_vector must be a finite numeric vector matching the matrix size")
        initial_norm = _norm(initial_vector)
        if initial_norm == 0.0:
            raise ValueError("initial_vector must be nonzero")
        vector = [float(value) / initial_norm for value in initial_vector]
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


def initialization_sensitivity_report(
    matrix: list[list[float]], primary_initial: list[float], blind_initial: list[float],
    *, residual_tol: float = 1e-10, max_steps: int = 200,
) -> dict[str, object]:
    """Compare two declared initial directions on the same symmetric matrix.

    A small residual certifies an eigenpair, not that the eigenpair has the
    largest magnitude.  This report keeps both initial vectors visible so a
    direction orthogonal to the dominant eigenspace cannot be hidden behind a
    converged residual alone.
    """
    primary_value, primary_vector, primary_trace = dominant_eigenpair(
        matrix, residual_tol=residual_tol, max_steps=max_steps, initial_vector=primary_initial,
    )
    blind_value, blind_vector, blind_trace = dominant_eigenpair(
        matrix, residual_tol=residual_tol, max_steps=max_steps, initial_vector=blind_initial,
    )
    return {
        "primary_initial": list(primary_initial),
        "blind_initial": list(blind_initial),
        "primary": {"eigenvalue": primary_value, "vector": primary_vector, "trace": primary_trace},
        "blind": {"eigenvalue": blind_value, "vector": blind_vector, "trace": blind_trace},
        "both_paths_have_small_residual": (
            primary_trace[-1]["residual_norm"] <= residual_tol
            and blind_trace[-1]["residual_norm"] <= residual_tol
        ),
        "primary_path_has_larger_magnitude_eigenvalue": abs(primary_value) > abs(blind_value),
    }


def initialization_sensitivity_certificate(
    matrix: list[list[float]], primary_initial: list[float], blind_initial: list[float], report: object,
    *, residual_tol: float = 1e-10, max_steps: int = 200,
) -> bool:
    """Replay both declared initializations and reject altered convergence claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == initialization_sensitivity_report(
            matrix, primary_initial, blind_initial, residual_tol=residual_tol, max_steps=max_steps,
        )
    except (TypeError, ValueError, RuntimeError):
        return False
