"""Small, auditable condition-number experiments for 2-by-2 systems.

This module intentionally uses the closed-form inverse only for a teaching
example.  Real applications should estimate conditioning from a factorization
instead of forming an inverse explicitly.
"""

from __future__ import annotations

from math import isfinite


Matrix = list[list[float]]


def _validate_matrix(matrix: Matrix) -> None:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("this teaching experiment requires a 2-by-2 matrix")
    if any(not isfinite(value) for row in matrix for value in row):
        raise ValueError("matrix entries must be finite")


def _validate_vector(values: list[float]) -> None:
    if len(values) != 2 or any(not isfinite(value) for value in values):
        raise ValueError("right_side must contain two finite values")


def infinity_norm(values: list[float]) -> float:
    """Return the vector infinity norm."""
    return max(abs(value) for value in values)


def matrix_infinity_norm(matrix: Matrix) -> float:
    """Return max_i sum_j |a_ij| for a finite 2-by-2 matrix."""
    _validate_matrix(matrix)
    return max(sum(abs(value) for value in row) for row in matrix)


def inverse_2x2(matrix: Matrix, *, singular_tol: float = 1e-15) -> Matrix:
    """Return a 2-by-2 inverse, rejecting matrices too close to singular."""
    _validate_matrix(matrix)
    if singular_tol <= 0 or not isfinite(singular_tol):
        raise ValueError("singular_tol must be finite and positive")
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    if abs(determinant) <= singular_tol:
        raise ValueError("matrix is singular or too close to singular for this experiment")
    return [[d / determinant, -b / determinant], [-c / determinant, a / determinant]]


def condition_number_infinity_2x2(matrix: Matrix) -> float:
    """Compute ||A||_inf ||A^-1||_inf for a small teaching matrix."""
    return matrix_infinity_norm(matrix) * matrix_infinity_norm(inverse_2x2(matrix))


def solve_2x2(matrix: Matrix, right_side: list[float]) -> list[float]:
    """Solve Ax=b by multiplying by the teaching inverse."""
    _validate_vector(right_side)
    inverse = inverse_2x2(matrix)
    return [sum(entry * value for entry, value in zip(row, right_side)) for row in inverse]


def residual(matrix: Matrix, estimate: list[float], right_side: list[float]) -> list[float]:
    """Return b-Ax, separating a small residual from a small forward error."""
    _validate_matrix(matrix)
    _validate_vector(estimate)
    _validate_vector(right_side)
    return [target - sum(entry * value for entry, value in zip(row, estimate)) for row, target in zip(matrix, right_side)]


def relative_change(reference: list[float], changed: list[float]) -> float:
    """Return ||changed-reference||_inf / ||reference||_inf."""
    _validate_vector(reference)
    _validate_vector(changed)
    scale = infinity_norm(reference)
    if scale == 0:
        raise ValueError("relative change is undefined for a zero reference vector")
    return infinity_norm([new - old for old, new in zip(reference, changed)]) / scale


def perturbation_report(matrix: Matrix, baseline_rhs: list[float], perturbed_rhs: list[float]) -> dict[str, float | list[float]]:
    """Measure how a right-side perturbation changes the solution of Ax=b."""
    baseline_solution = solve_2x2(matrix, baseline_rhs)
    perturbed_solution = solve_2x2(matrix, perturbed_rhs)
    return {
        "condition_number": condition_number_infinity_2x2(matrix),
        "relative_rhs_change": relative_change(baseline_rhs, perturbed_rhs),
        "relative_solution_change": relative_change(baseline_solution, perturbed_solution),
        "baseline_solution": baseline_solution,
        "perturbed_solution": perturbed_solution,
        "perturbed_residual_norm": infinity_norm(residual(matrix, perturbed_solution, perturbed_rhs)),
    }
