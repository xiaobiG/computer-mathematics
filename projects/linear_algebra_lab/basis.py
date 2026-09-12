"""Small, auditable experiments for column independence and basis coordinates."""

from __future__ import annotations

from math import isfinite, sqrt

from projects.linear_algebra_lab.main import EPSILON, solve


def _validate_columns(columns: list[list[float]], tolerance: float) -> int:
    if not columns or not columns[0] or any(len(column) != len(columns[0]) for column in columns):
        raise ValueError("columns must be a non-empty list of equally sized vectors")
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
           for column in columns for value in column):
        raise ValueError("columns must contain finite real values")
    return len(columns[0])


def column_independence_report(columns: list[list[float]], tolerance: float = EPSILON) -> dict[str, object]:
    """Return an order-preserving independent subfamily using Gram--Schmidt.

    A nonzero orthogonal residual means that the next column contributes a new
    direction; a residual at or below ``tolerance`` is numerically dependent on
    earlier retained directions.  This is a teaching rank diagnostic, not a
    replacement for pivoted QR/SVD on ill-conditioned production data.
    """
    ambient_dimension = _validate_columns(columns, tolerance)
    orthonormal: list[list[float]] = []
    basis_indices: list[int] = []
    residual_norms: list[float] = []
    for index, column in enumerate(columns):
        residual = [float(value) for value in column]
        for direction in orthonormal:
            coefficient = sum(left * right for left, right in zip(residual, direction))
            residual = [value - coefficient * direction[row] for row, value in enumerate(residual)]
        residual_norm = sqrt(sum(value * value for value in residual))
        residual_norms.append(residual_norm)
        if residual_norm > tolerance:
            orthonormal.append([value / residual_norm for value in residual])
            basis_indices.append(index)
    rank = len(basis_indices)
    return {
        "ambient_dimension": ambient_dimension,
        "rank": rank,
        "basis_indices": basis_indices,
        "residual_norms": residual_norms,
        "is_linearly_independent": rank == len(columns),
        "is_basis_for_ambient_space": len(columns) == ambient_dimension and rank == ambient_dimension,
    }


def column_independence_certificate(
    columns: list[list[float]], report: dict[str, object], tolerance: float = EPSILON,
) -> dict[str, bool]:
    """Recompute a Gram--Schmidt rank diagnostic instead of trusting its labels."""
    empty = {
        "fields_match_recomputed_diagnostic": False,
        "rank_and_independence_agree": False,
        "valid": False,
    }
    try:
        expected = column_independence_report(columns, tolerance)
        if not isinstance(report, dict):
            return empty
        diagnostic_fields = (
            "ambient_dimension", "rank", "basis_indices", "residual_norms",
            "is_linearly_independent", "is_basis_for_ambient_space",
        )
        fields_match = all(report.get(field) == expected[field] for field in diagnostic_fields)
        rank = report.get("rank")
        independence_agrees = (
            isinstance(rank, int)
            and report.get("is_linearly_independent") == (rank == len(columns))
            and report.get("is_basis_for_ambient_space")
            == (len(columns) == expected["ambient_dimension"] and rank == expected["ambient_dimension"])
        )
        return {
            "fields_match_recomputed_diagnostic": fields_match,
            "rank_and_independence_agree": fields_match and independence_agrees,
            "valid": fields_match and independence_agrees,
        }
    except (TypeError, ValueError):
        return empty


def basis_coordinate_report(
    columns: list[list[float]], target: list[float], tolerance: float = EPSILON,
) -> dict[str, object]:
    """Recover unique coordinates in a basis and return an Ax=b certificate."""
    report = column_independence_report(columns, tolerance)
    dimension = report["ambient_dimension"]
    if not report["is_basis_for_ambient_space"]:
        raise ValueError("coordinate recovery requires a linearly independent ambient-space basis")
    if len(target) != dimension or any(not isinstance(value, (int, float)) or isinstance(value, bool)
                                       or not isfinite(value) for value in target):
        raise ValueError("target must be a finite vector in the basis ambient space")
    matrix = [[columns[column][row] for column in range(dimension)] for row in range(dimension)]
    coordinates = solve(matrix, target, tolerance)
    reconstruction = [sum(matrix[row][column] * coordinates[column] for column in range(dimension))
                      for row in range(dimension)]
    residual = [reconstruction[row] - target[row] for row in range(dimension)]
    return {
        **report,
        "coordinates": coordinates,
        "reconstruction": reconstruction,
        "residual": residual,
        "reconstructs_target": all(abs(value) <= tolerance for value in residual),
    }


def basis_coordinate_certificate(
    columns: list[list[float]], target: list[float], report: dict[str, object], tolerance: float = EPSILON,
) -> dict[str, bool]:
    """Recompute coordinates and reconstruction; reject a changed basis report."""
    empty = {
        "basis_diagnostic_matches": False,
        "coordinates_match_recomputed_solution": False,
        "reconstruction_matches_target": False,
        "valid": False,
    }
    try:
        expected = basis_coordinate_report(columns, target, tolerance)
        if not isinstance(report, dict):
            return empty
        basis_fields = (
            "ambient_dimension", "rank", "basis_indices", "residual_norms",
            "is_linearly_independent", "is_basis_for_ambient_space",
        )
        basis_matches = all(report.get(field) == expected[field] for field in basis_fields)
        coordinates_match = report.get("coordinates") == expected["coordinates"]
        reconstruction_match = (
            report.get("reconstruction") == expected["reconstruction"]
            and report.get("residual") == expected["residual"]
            and report.get("reconstructs_target") is True
        )
        return {
            "basis_diagnostic_matches": basis_matches,
            "coordinates_match_recomputed_solution": basis_matches and coordinates_match,
            "reconstruction_matches_target": basis_matches and coordinates_match and reconstruction_match,
            "valid": basis_matches and coordinates_match and reconstruction_match,
        }
    except (TypeError, ValueError):
        return empty


FUNDAMENTAL_SUBSPACES_CONTRACT = "fundamental-subspaces/v1"


def _validate_matrix(matrix: object, tolerance: float) -> list[list[float]]:
    if not isinstance(matrix, list) or not matrix or not isinstance(matrix[0], list) or not matrix[0]:
        raise ValueError("matrix must be a non-empty rectangular list")
    width = len(matrix[0])
    if any(not isinstance(row, list) or len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")
    if tolerance <= 0.0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)
           for row in matrix for value in row):
        raise ValueError("matrix must contain finite real values")
    return [[float(value) for value in row] for row in matrix]


def _clean(value: float, tolerance: float) -> float:
    return 0.0 if abs(value) <= tolerance else value


def _rref(matrix: list[list[float]], tolerance: float) -> tuple[list[list[float]], list[int]]:
    """Return a small teaching RREF and its pivot columns using partial pivoting."""
    work = [row[:] for row in matrix]
    rows, columns = len(work), len(work[0])
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        if pivot_row == rows:
            break
        candidate = max(range(pivot_row, rows), key=lambda row: abs(work[row][column]))
        if abs(work[candidate][column]) <= tolerance:
            continue
        work[pivot_row], work[candidate] = work[candidate], work[pivot_row]
        pivot = work[pivot_row][column]
        work[pivot_row] = [_clean(value / pivot, tolerance) for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if abs(factor) <= tolerance:
                continue
            work[row] = [_clean(value - factor * pivot_value, tolerance)
                         for value, pivot_value in zip(work[row], work[pivot_row])]
        pivot_columns.append(column)
        pivot_row += 1
    return [[_clean(value, tolerance) for value in row] for row in work], pivot_columns


def _null_space_basis(rref: list[list[float]], pivot_columns: list[int], tolerance: float) -> list[list[float]]:
    columns = len(rref[0])
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    basis: list[list[float]] = []
    for free in free_columns:
        vector = [0.0] * columns
        vector[free] = 1.0
        for pivot_row, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = _clean(-rref[pivot_row][free], tolerance)
        basis.append(vector)
    return basis


def _dot(left: list[float], right: list[float]) -> float:
    return sum(first * second for first, second in zip(left, right))


def fundamental_subspaces_report(matrix: object, tolerance: float = EPSILON) -> dict[str, object]:
    """Expose the four fundamental subspaces for a finite teaching matrix.

    Original pivot columns form a column-space basis; nonzero RREF rows form a
    row-space basis; free variables of ``A`` and ``A^T`` produce null bases.
    This is a tolerance-dependent teaching diagnostic, not a production rank
    decision in place of pivoted QR/SVD.
    """
    original = _validate_matrix(matrix, tolerance)
    rows, columns = len(original), len(original[0])
    rref, pivots = _rref(original, tolerance)
    transpose = [[original[row][column] for row in range(rows)] for column in range(columns)]
    transpose_rref, transpose_pivots = _rref(transpose, tolerance)
    rank = len(pivots)
    column_basis = [[original[row][column] for row in range(rows)] for column in pivots]
    row_basis = [rref[index] for index in range(rank)]
    null_basis = _null_space_basis(rref, pivots, tolerance)
    left_null_basis = _null_space_basis(transpose_rref, transpose_pivots, tolerance)
    left_orthogonal = all(abs(_dot(vector, column)) <= tolerance for vector in left_null_basis for column in column_basis)
    row_orthogonal = all(abs(_dot(vector, row)) <= tolerance for vector in null_basis for row in row_basis)
    return {
        "contract": FUNDAMENTAL_SUBSPACES_CONTRACT,
        "matrix": original,
        "tolerance": tolerance,
        "shape": {"rows": rows, "columns": columns},
        "rref": rref,
        "pivot_columns": pivots,
        "column_space_basis": column_basis,
        "row_space_basis": row_basis,
        "null_space_basis": null_basis,
        "left_null_space_basis": left_null_basis,
        "dimensions": {
            "rank": rank,
            "column_space": len(column_basis),
            "row_space": len(row_basis),
            "null_space": len(null_basis),
            "left_null_space": len(left_null_basis),
        },
        "certificate": {
            "rank_nullity_for_domain": rank + len(null_basis) == columns,
            "rank_nullity_for_codomain": rank + len(left_null_basis) == rows,
            "column_space_orthogonal_to_left_null_space": left_orthogonal,
            "row_space_orthogonal_to_null_space": row_orthogonal,
        },
        "interpretation": "tolerance_dependent_teaching_diagnostic_not_a_production_rank_decision",
    }


def fundamental_subspaces_certificate(matrix: object, report: object, tolerance: float = EPSILON) -> bool:
    """Replay every basis, dimension identity and orthogonality claim."""
    if not isinstance(report, dict):
        return False
    try:
        return report == fundamental_subspaces_report(matrix, tolerance)
    except (TypeError, ValueError):
        return False
