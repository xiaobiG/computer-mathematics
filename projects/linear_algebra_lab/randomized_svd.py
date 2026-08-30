"""A small, seeded randomized SVD report built on the teaching range finder."""

from dataclasses import dataclass
from math import isclose, sqrt

from projects.linear_algebra_lab.main import rank_k_approximation
from projects.linear_algebra_lab.randomized_range import _matmul, _transpose
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

    The seeded range finder supplies Q.  The tiny B decomposition reuses this
    lab's finite-iteration deflation SVD; it records all inputs necessary to
    replay it and does not claim a high-probability error bound.
    """
    range_report = randomized_range_report(matrix, rank, oversampling, power_iterations, seed)
    q = [list(column) for column in _transpose(range_report.basis)]
    b = _matmul(_transpose(q), matrix)
    components, b_approximation = rank_k_approximation(b, rank)
    approximation = _matmul(q, b_approximation)
    singular_values = [component[0] for component in components]
    error = sqrt(sum((float(matrix[row][column]) - approximation[row][column]) ** 2
                     for row in range(len(matrix)) for column in range(len(matrix[0]))))
    return RandomizedSVDReport(
        seed=seed,
        rank=rank,
        oversampling=oversampling,
        power_iterations=power_iterations,
        singular_values=tuple(float(value) for value in singular_values),
        approximation=tuple(tuple(float(value) for value in row) for row in approximation),
        frobenius_error=error,
    )


def randomized_svd_certificate(matrix, report, tolerance=1e-10):
    """Replay the sampled range and small SVD, rejecting altered claims."""
    if not isinstance(report, RandomizedSVDReport) or tolerance <= 0:
        return False
    try:
        expected = randomized_svd_report(matrix, report.rank, report.oversampling, report.power_iterations, report.seed)
    except ValueError:
        return False
    if report.singular_values != expected.singular_values or not isclose(report.frobenius_error, expected.frobenius_error, rel_tol=tolerance, abs_tol=tolerance):
        return False
    return all(isclose(actual, target, rel_tol=tolerance, abs_tol=tolerance) for row, target_row in zip(report.approximation, expected.approximation) for actual, target in zip(row, target_row))
