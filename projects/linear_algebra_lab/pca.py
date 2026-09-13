"""A small, auditable two-dimensional PCA teaching experiment."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite

from projects.linear_algebra_lab.power_iteration import dominant_eigenpair


@dataclass(frozen=True)
class Pca2DReport:
    """One-component PCA results plus numerical certificates for a 2-D sample."""

    mean: tuple[float, float]
    covariance: tuple[tuple[float, float], tuple[float, float]]
    component: tuple[float, float]
    eigenvalue: float
    explained_variance_ratio: float
    scores: tuple[float, ...]
    reconstructed_rows: tuple[tuple[float, float], ...]
    reconstruction_error_squared: float
    certificate: dict[str, bool]


def _validate_rows(rows: list[list[float]]) -> None:
    if len(rows) < 2 or any(len(row) != 2 for row in rows):
        raise ValueError("two-dimensional PCA requires at least two 2-D rows")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
           for row in rows for value in row):
        raise ValueError("PCA rows must contain finite real values")


def pca_2d_report(rows: list[list[float]], *, residual_tol: float = 1e-10) -> Pca2DReport:
    """Fit one principal component and certify centering/projection identities.

    The function intentionally handles only two features so every operation is
    inspectable in the accompanying lesson.  It uses the sample covariance
    denominator ``m - 1`` and fails when all centered data has zero variance.
    """
    _validate_rows(rows)
    if residual_tol <= 0 or not isfinite(residual_tol):
        raise ValueError("residual_tol must be finite and positive")
    sample_count = len(rows)
    mean = tuple(sum(row[column] for row in rows) / sample_count for column in range(2))
    centered = [[row[column] - mean[column] for column in range(2)] for row in rows]
    covariance = tuple(
        tuple(sum(row[left] * row[right] for row in centered) / (sample_count - 1) for right in range(2))
        for left in range(2)
    )
    total_variance = covariance[0][0] + covariance[1][1]
    if total_variance <= residual_tol:
        raise ValueError("PCA is undefined for zero-variance centered data")
    eigenvalue, component, _ = dominant_eigenpair([list(row) for row in covariance], residual_tol=residual_tol)
    component_pair = (component[0], component[1])
    scores = tuple(sum(row[column] * component_pair[column] for column in range(2)) for row in centered)
    reconstructed_rows = tuple(
        tuple(mean[column] + score * component_pair[column] for column in range(2))
        for score in scores
    )
    residuals = [
        [rows[row_index][column] - reconstructed_rows[row_index][column] for column in range(2)]
        for row_index in range(sample_count)
    ]
    reconstruction_error_squared = sum(value * value for row in residuals for value in row)
    expected_error = (sample_count - 1) * (total_variance - eigenvalue)
    certificate = {
        "centered_columns_sum_to_zero": all(abs(sum(row[column] for row in centered)) <= residual_tol
                                              for column in range(2)),
        "component_has_unit_norm": abs(sum(value * value for value in component_pair) - 1.0) <= residual_tol,
        "residuals_are_orthogonal_to_component": all(
            abs(sum(value * direction for value, direction in zip(residual, component_pair))) <= residual_tol
            for residual in residuals
        ),
        "reconstruction_error_matches_discarded_variance": abs(
            reconstruction_error_squared - expected_error
        ) <= residual_tol * max(1.0, reconstruction_error_squared, abs(expected_error)),
    }
    certificate["valid"] = all(certificate.values())
    return Pca2DReport(
        mean=mean,
        covariance=covariance,
        component=component_pair,
        eigenvalue=eigenvalue,
        explained_variance_ratio=eigenvalue / total_variance,
        scores=scores,
        reconstructed_rows=reconstructed_rows,
        reconstruction_error_squared=reconstruction_error_squared,
        certificate=certificate,
    )


def pca_2d_report_certificate(
    rows: list[list[float]], report: Pca2DReport, *, residual_tol: float = 1e-10
) -> bool:
    """Independently replay a 2-D PCA report and reject altered claims.

    ``Pca2DReport.certificate`` is useful when the report is first produced,
    but a Boolean stored inside a report is not evidence by itself.  This
    verifier recomputes centering, covariance, the deterministic dominant
    eigenpair, projections, reconstruction error, and every certificate
    field from the declared rows.  It intentionally remains a tiny 2-D
    teaching replayer, not a general numerical-PCA validation framework.
    """
    if not isinstance(report, Pca2DReport) or residual_tol <= 0 or not isfinite(residual_tol):
        return False
    try:
        expected = pca_2d_report(rows, residual_tol=residual_tol)
    except (TypeError, ValueError):
        return False

    scalar_pairs = [
        (report.eigenvalue, expected.eigenvalue),
        (report.explained_variance_ratio, expected.explained_variance_ratio),
        (report.reconstruction_error_squared, expected.reconstruction_error_squared),
    ]
    vector_pairs = [
        (report.mean, expected.mean),
        (report.component, expected.component),
        (report.scores, expected.scores),
    ]
    matrix_pairs = [
        (report.covariance, expected.covariance),
        (report.reconstructed_rows, expected.reconstructed_rows),
    ]
    close = lambda actual, target: isclose(actual, target, rel_tol=residual_tol, abs_tol=residual_tol)
    return (
        all(close(actual, target) for actual, target in scalar_pairs)
        and all(len(actual) == len(target) and all(close(value, expected_value)
                for value, expected_value in zip(actual, target))
                for actual, target in vector_pairs)
        and all(
            len(actual) == len(target)
            and all(len(actual_row) == len(target_row)
                    and all(close(value, expected_value) for value, expected_value in zip(actual_row, target_row))
                    for actual_row, target_row in zip(actual, target))
            for actual, target in matrix_pairs
        )
        and report.certificate == expected.certificate
    )


def pca_2d_centering_comparison_report(
    rows: list[list[float]], *, residual_tol: float = 1e-10,
) -> dict[str, object]:
    """Contrast centered PCA with the uncentered second-moment direction.

    The two paths consume exactly the same rows.  The uncentered path is a
    valid eigendecomposition of ``X^T X / m`` but is not PCA about the sample
    mean; this report makes that distinction observable on a finite 2-D case.
    """
    _validate_rows(rows)
    if residual_tol <= 0 or not isfinite(residual_tol):
        raise ValueError("residual_tol must be finite and positive")
    centered = pca_2d_report(rows, residual_tol=residual_tol)
    sample_count = len(rows)
    mean = centered.mean
    mean_norm = sum(value * value for value in mean) ** .5
    if mean_norm <= residual_tol:
        raise ValueError("centering comparison requires a non-zero sample mean")
    second_moment = tuple(
        tuple(sum(row[left] * row[right] for row in rows) / sample_count for right in range(2))
        for left in range(2)
    )
    uncentered_eigenvalue, uncentered_component, _ = dominant_eigenpair(
        [list(row) for row in second_moment], residual_tol=residual_tol,
    )
    centered_alignment = abs(sum(direction * average for direction, average in zip(centered.component, mean)) / mean_norm)
    uncentered_alignment = abs(sum(direction * average for direction, average in zip(uncentered_component, mean)) / mean_norm)
    component_alignment = abs(sum(left * right for left, right in zip(centered.component, uncentered_component)))
    return {
        "rows": tuple(tuple(float(value) for value in row) for row in rows),
        "mean": mean,
        "centered_covariance": centered.covariance,
        "uncentered_second_moment": second_moment,
        "centered_component": centered.component,
        "uncentered_component": tuple(uncentered_component),
        "centered_eigenvalue": centered.eigenvalue,
        "uncentered_eigenvalue": uncentered_eigenvalue,
        "centered_alignment_to_mean": centered_alignment,
        "uncentered_alignment_to_mean": uncentered_alignment,
        "component_absolute_alignment": component_alignment,
        "uncentered_is_more_aligned_to_mean": uncentered_alignment > centered_alignment + residual_tol,
        "components_are_different_directions": component_alignment < 1.0 - residual_tol,
        "interpretation": "uncentered_second_moment_can_follow_mean_offset_not_centered_variation",
    }


def pca_2d_centering_comparison_certificate(
    rows: object, report: object, *, residual_tol: float = 1e-10,
) -> bool:
    """Rebuild both paths, rejecting changed direction or centering claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == pca_2d_centering_comparison_report(rows, residual_tol=residual_tol)
    except (TypeError, ValueError):
        return False
