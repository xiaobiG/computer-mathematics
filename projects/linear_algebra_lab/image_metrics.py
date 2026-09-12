"""Small, auditable image-error metrics for the linear algebra lab.

The module treats an image as a finite rectangular numeric matrix.  It does
not decode image files or make a claim about human visual quality.
"""

from dataclasses import dataclass
from math import inf, isclose, isfinite, log10, sqrt

from projects.linear_algebra_lab.randomized_svd import RandomizedSVDReport, randomized_svd_certificate


@dataclass(frozen=True)
class ImageQualityReport:
    samples: int
    mse: float
    rmse: float
    psnr: float
    max_absolute_error: float


@dataclass(frozen=True)
class RandomizedSVDImageQualityReview:
    """A declared pixel-error budget applied to a verified random-SVD result."""

    source_rank: int
    source_seed: int
    source_oversampling: int
    source_power_iterations: int
    mse_budget: float
    quality: ImageQualityReport
    mse_budget_status: str
    automatic_action: str


@dataclass(frozen=True)
class StructuralSimilarityReport:
    samples: int
    reference_mean: float
    approximation_mean: float
    reference_variance: float
    approximation_variance: float
    covariance: float
    ssim: float


def _validate(reference, approximation, peak):
    if not isinstance(peak, (int, float)) or isinstance(peak, bool) or not isfinite(peak) or peak <= 0:
        raise ValueError("peak must be a finite positive number")
    if not isinstance(reference, (list, tuple)) or not reference or not isinstance(approximation, (list, tuple)):
        raise ValueError("images must be non-empty matrices")
    if len(reference) != len(approximation) or not reference[0]:
        raise ValueError("images must have the same non-empty shape")
    width = len(reference[0])
    if any(not isinstance(row, (list, tuple)) or len(row) != width for row in reference):
        raise ValueError("reference must be rectangular")
    if any(not isinstance(row, (list, tuple)) or len(row) != width for row in approximation):
        raise ValueError("approximation must have the same rectangular shape")
    for matrix in (reference, approximation):
        for row in matrix:
            for value in row:
                if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
                    raise ValueError("image values must be finite numbers")


def image_quality_report(reference, approximation, peak=255.0):
    """Measure pointwise numeric error and PSNR for two same-shaped images."""
    _validate(reference, approximation, peak)
    errors = [float(expected) - float(actual)
              for expected_row, actual_row in zip(reference, approximation)
              for expected, actual in zip(expected_row, actual_row)]
    samples = len(errors)
    mse = sum(error * error for error in errors) / samples
    rmse = sqrt(mse)
    psnr = inf if mse == 0.0 else 20.0 * log10(float(peak) / rmse)
    return ImageQualityReport(
        samples=samples,
        mse=mse,
        rmse=rmse,
        psnr=psnr,
        max_absolute_error=max(abs(error) for error in errors),
    )


def image_quality_certificate(reference, approximation, report, peak=255.0, tolerance=1e-12):
    """Recompute a report and reject altered fields or incompatible inputs."""
    if not isinstance(report, ImageQualityReport):
        return False
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or tolerance < 0:
        return False
    try:
        expected = image_quality_report(reference, approximation, peak)
    except ValueError:
        return False
    return (
        report.samples == expected.samples
        and isclose(report.mse, expected.mse, rel_tol=tolerance, abs_tol=tolerance)
        and isclose(report.rmse, expected.rmse, rel_tol=tolerance, abs_tol=tolerance)
        and ((report.psnr == expected.psnr == inf) or isclose(report.psnr, expected.psnr, rel_tol=tolerance, abs_tol=tolerance))
        and isclose(report.max_absolute_error, expected.max_absolute_error, rel_tol=tolerance, abs_tol=tolerance)
    )


def randomized_svd_image_quality_review(reference, svd_report, mse_budget, peak=255.0):
    """Evaluate the actual reconstruction from a verified randomized-SVD report.

    The source report is consumed as an artifact, rather than asking callers to
    copy out an approximation matrix.  The result is a numeric budget review,
    not a claim about perceived quality, file size, or downstream task quality.
    """
    if (not isinstance(mse_budget, (int, float)) or isinstance(mse_budget, bool)
            or not isfinite(mse_budget) or mse_budget < 0):
        raise ValueError("mse_budget must be a finite non-negative number")
    if not isinstance(svd_report, RandomizedSVDReport):
        raise ValueError("svd_report must be a randomized SVD artifact")
    if not randomized_svd_certificate(reference, svd_report):
        raise ValueError("svd_report does not replay for this reference matrix")
    quality = image_quality_report(reference, svd_report.approximation, peak)
    budget = float(mse_budget)
    return RandomizedSVDImageQualityReview(
        source_rank=svd_report.rank,
        source_seed=svd_report.seed,
        source_oversampling=svd_report.oversampling,
        source_power_iterations=svd_report.power_iterations,
        mse_budget=budget,
        quality=quality,
        mse_budget_status="within_mse_budget" if quality.mse <= budget else "exceeds_mse_budget",
        automatic_action="none",
    )


def randomized_svd_image_quality_review_certificate(reference, svd_report, mse_budget, review, peak=255.0):
    """Rebuild the source-bound quality review and reject altered conclusions."""
    if not isinstance(review, RandomizedSVDImageQualityReview):
        return False
    try:
        return review == randomized_svd_image_quality_review(reference, svd_report, mse_budget, peak)
    except ValueError:
        return False


def structural_similarity_report(reference, approximation, peak=255.0, k1=0.01, k2=0.03):
    """Compute global SSIM for small teaching matrices, not a perceptual benchmark."""
    _validate(reference, approximation, peak)
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0
           for value in (k1, k2)):
        raise ValueError("k1 and k2 must be positive numbers")
    left = [float(value) for row in reference for value in row]
    right = [float(value) for row in approximation for value in row]
    samples = len(left)
    mean_left, mean_right = sum(left) / samples, sum(right) / samples
    divisor = samples - 1
    variance_left = 0.0 if divisor == 0 else sum((value - mean_left) ** 2 for value in left) / divisor
    variance_right = 0.0 if divisor == 0 else sum((value - mean_right) ** 2 for value in right) / divisor
    covariance = 0.0 if divisor == 0 else sum(
        (x - mean_left) * (y - mean_right) for x, y in zip(left, right)
    ) / divisor
    c1, c2 = (k1 * float(peak)) ** 2, (k2 * float(peak)) ** 2
    ssim = ((2 * mean_left * mean_right + c1) * (2 * covariance + c2)) / (
        (mean_left ** 2 + mean_right ** 2 + c1) * (variance_left + variance_right + c2)
    )
    return StructuralSimilarityReport(samples, mean_left, mean_right, variance_left, variance_right, covariance, ssim)


def structural_similarity_certificate(reference, approximation, report, peak=255.0, k1=0.01, k2=0.03, tolerance=1e-12):
    if not isinstance(report, StructuralSimilarityReport):
        return False
    try:
        expected = structural_similarity_report(reference, approximation, peak, k1, k2)
    except ValueError:
        return False
    return all(isclose(getattr(report, field), getattr(expected, field), rel_tol=tolerance, abs_tol=tolerance)
               for field in ("reference_mean", "approximation_mean", "reference_variance", "approximation_variance", "covariance", "ssim")) and report.samples == expected.samples
