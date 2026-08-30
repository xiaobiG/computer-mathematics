"""A small, seeded randomized SVD report built on the teaching range finder."""

from dataclasses import dataclass
from math import isclose

import numpy as np

from projects.linear_algebra_lab.randomized_range import randomized_range_report


@dataclass(frozen=True)
class RandomizedSVDReport:
    seed: int
    rank: int
    oversampling: int
    power_iterations: int
    singular_values: tuple[float, ...]
    approximation: tuple[tuple[float, ...], ...]
    frobenius_error: float


def randomized_svd_report(matrix, rank, oversampling=2, power_iterations=0, seed=0):
    """Build ``Q``, factor small ``B=Q^T A``, then retain ``rank`` terms.

    The seeded range finder supplies Q.  NumPy is used only for the tiny dense
    B decomposition in this teaching artifact; the report records all inputs
    necessary to replay it and does not claim a high-probability error bound.
    """
    range_report = randomized_range_report(matrix, rank, oversampling, power_iterations, seed)
    array = np.asarray(matrix, dtype=float)
    q = np.asarray(range_report.basis, dtype=float).T
    b = q.T @ array
    ub, singular_values, vt = np.linalg.svd(b, full_matrices=False)
    kept = min(rank, len(singular_values))
    approximation = (q @ ub[:, :kept]) @ np.diag(singular_values[:kept]) @ vt[:kept, :]
    return RandomizedSVDReport(
        seed=seed,
        rank=rank,
        oversampling=oversampling,
        power_iterations=power_iterations,
        singular_values=tuple(float(value) for value in singular_values[:kept]),
        approximation=tuple(tuple(float(value) for value in row) for row in approximation),
        frobenius_error=float(np.linalg.norm(array - approximation, ord="fro")),
    )


def randomized_svd_certificate(matrix, report, tolerance=1e-10):
    """Replay the sampled range and small SVD, rejecting altered claims."""
    if not isinstance(report, RandomizedSVDReport) or tolerance <= 0:
        return False
    try:
        expected = randomized_svd_report(matrix, report.rank, report.oversampling, report.power_iterations, report.seed)
    except (ValueError, np.linalg.LinAlgError):
        return False
    if report.singular_values != expected.singular_values or not isclose(report.frobenius_error, expected.frobenius_error, rel_tol=tolerance, abs_tol=tolerance):
        return False
    return all(isclose(actual, target, rel_tol=tolerance, abs_tol=tolerance) for row, target_row in zip(report.approximation, expected.approximation) for actual, target in zip(row, target_row))
