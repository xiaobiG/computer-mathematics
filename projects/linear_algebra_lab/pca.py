"""A small, auditable two-dimensional PCA teaching experiment."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

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
