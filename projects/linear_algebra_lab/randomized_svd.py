"""A small, seeded randomized SVD report built on the teaching range finder."""

from dataclasses import dataclass
from math import isclose, sqrt

from projects.linear_algebra_lab.main import rank_k_approximation
from projects.linear_algebra_lab.randomized_range import (
    RandomizedRangeReport,
    _matmul,
    _transpose,
    randomized_range_certificate,
    randomized_range_report,
)


@dataclass(frozen=True)
class RandomizedSVDReport:
    seed: int
    rank: int
    oversampling: int
    power_iterations: int
    singular_values: tuple[float, ...]
    approximation: tuple[tuple[float, ...], ...]
    frobenius_error: float
    range_projection_error: float
    in_range_truncation_error: float
    pythagorean_residual: float
    source_range_report: RandomizedRangeReport


def randomized_svd_report(matrix, rank, oversampling=2, power_iterations=0, seed=0):
    """Build ``Q``, factor small ``B=Q^T A``, then retain ``rank`` terms.

    The seeded range finder supplies Q.  The tiny B decomposition reuses this
    lab's finite-iteration deflation SVD; it records all inputs necessary to
    replay it and does not claim a high-probability error bound.
    """
    range_report = randomized_range_report(matrix, rank, oversampling, power_iterations, seed)
    return randomized_svd_from_range_report(matrix, range_report, rank)


def randomized_svd_from_range_report(matrix, range_report, rank):
    """Factor a reader-supplied, replayable randomized range artifact.

    The range report is not a decorative seed record: its verified orthogonal
    basis is the actual subspace on which the smaller SVD is computed.  A
    caller can deliberately retain fewer terms than the range finder sampled,
    but cannot silently swap its source sketch or its oversampling policy.
    """
    if not isinstance(range_report, RandomizedRangeReport):
        raise ValueError("range_report must be a randomized range artifact")
    if not randomized_range_certificate(matrix, range_report, oversampling=range_report.oversampling):
        raise ValueError("range_report does not replay for this matrix")
    if (not isinstance(rank, int) or isinstance(rank, bool)
            or not 0 < rank <= min(range_report.basis_columns, len(matrix[0]))):
        raise ValueError("rank must fit the verified sampled basis and matrix columns")
    q = [list(column) for column in _transpose(range_report.basis)]
    b = _matmul(_transpose(q), matrix)
    components, b_approximation = rank_k_approximation(b, rank)
    approximation = _matmul(q, b_approximation)
    singular_values = [component[0] for component in components]
    error = sqrt(sum((float(matrix[row][column]) - approximation[row][column]) ** 2
                     for row in range(len(matrix)) for column in range(len(matrix[0]))))
    projection_error = range_report.frobenius_error
    in_range_error = sqrt(sum(
        (float(range_report.approximation[row][column]) - approximation[row][column]) ** 2
        for row in range(len(matrix)) for column in range(len(matrix[0]))
    ))
    # A - A_k = (I - QQ^T)A + Q(B - B_k).  The summands are orthogonal:
    # Q^T(I - QQ^T) = 0, so their squared Frobenius norms add.
    pythagorean_residual = abs(error * error - projection_error * projection_error - in_range_error * in_range_error)
    return RandomizedSVDReport(
        seed=range_report.seed,
        rank=rank,
        oversampling=range_report.oversampling,
        power_iterations=range_report.power_iterations,
        singular_values=tuple(float(value) for value in singular_values),
        approximation=tuple(tuple(float(value) for value in row) for row in approximation),
        frobenius_error=error,
        range_projection_error=projection_error,
        in_range_truncation_error=in_range_error,
        pythagorean_residual=pythagorean_residual,
        source_range_report=range_report,
    )


def randomized_svd_certificate(matrix, report, tolerance=1e-10):
    """Replay the sampled range and small SVD, rejecting altered claims."""
    if not isinstance(report, RandomizedSVDReport) or tolerance <= 0:
        return False
    try:
        if not randomized_range_certificate(matrix, report.source_range_report,
                                            oversampling=report.source_range_report.oversampling):
            return False
        expected = randomized_svd_from_range_report(matrix, report.source_range_report, report.rank)
    except ValueError:
        return False
    if (report.seed != report.source_range_report.seed
            or report.oversampling != report.source_range_report.oversampling
            or report.power_iterations != report.source_range_report.power_iterations
            or report.singular_values != expected.singular_values
            or not isclose(report.frobenius_error, expected.frobenius_error, rel_tol=tolerance, abs_tol=tolerance)
            or not isclose(report.range_projection_error, expected.range_projection_error, rel_tol=tolerance, abs_tol=tolerance)
            or not isclose(report.in_range_truncation_error, expected.in_range_truncation_error, rel_tol=tolerance, abs_tol=tolerance)
            or not isclose(report.pythagorean_residual, expected.pythagorean_residual, rel_tol=tolerance, abs_tol=tolerance)):
        return False
    # ``zip`` alone silently accepts a truncated or overlong approximation.
    # Shape is part of the report claim: an m-by-n reconstruction cannot be
    # verified by comparing only a matching prefix of its rows or columns.
    if len(report.approximation) != len(expected.approximation):
        return False
    return all(
        len(row) == len(target_row)
        and all(
            isclose(actual, target, rel_tol=tolerance, abs_tol=tolerance)
            for actual, target in zip(row, target_row)
        )
        for row, target_row in zip(report.approximation, expected.approximation)
    )
