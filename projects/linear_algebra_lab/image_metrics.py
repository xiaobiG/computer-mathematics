"""Small, auditable image-error metrics for the linear algebra lab.

The module treats an image as a finite rectangular numeric matrix.  It does
not decode image files or make a claim about human visual quality.
"""

from dataclasses import dataclass
from math import inf, isclose, isfinite, log10, sqrt


@dataclass(frozen=True)
class ImageQualityReport:
    samples: int
    mse: float
    rmse: float
    psnr: float
    max_absolute_error: float


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
