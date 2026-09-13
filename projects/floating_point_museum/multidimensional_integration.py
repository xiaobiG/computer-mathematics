"""Auditable two-dimensional grid and Monte Carlo integration benchmark."""

from __future__ import annotations

from math import isfinite, sqrt
from random import Random


UNIT_SQUARE_INTEGRATION_CONTRACT_VERSION = "unit-square-integration/v2"
EXACT_INTEGRAL = 5.0 / 6.0
# Var(X^2 + Y) = Var(X^2) + Var(Y) = (1/5 - 1/9) + 1/12.
EXACT_INTEGRAND_VARIANCE = 31.0 / 180.0


def _positive_int(value: object, name: str, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer from 1 to {maximum}")
    return value


def _seed(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("seed must be an integer")
    return value


def _integrand(x: float, y: float) -> float:
    return x * x + y


def _grid_midpoint(subdivisions: int) -> dict[str, float | int]:
    width = 1.0 / subdivisions
    total = 0.0
    for row in range(subdivisions):
        y = (row + 0.5) * width
        for column in range(subdivisions):
            x = (column + 0.5) * width
            total += _integrand(x, y)
    estimate = total * width * width
    return {"subdivisions_per_axis": subdivisions, "sample_count": subdivisions * subdivisions, "estimate": estimate, "absolute_error": abs(estimate - EXACT_INTEGRAL)}


def _monte_carlo(sample_count: int, seed: int) -> dict[str, float | int | None]:
    generator = Random(seed)
    values = [_integrand(generator.random(), generator.random()) for _ in range(sample_count)]
    estimate = sum(values) / sample_count
    squared_deviations = sum((value - estimate) ** 2 for value in values)
    unbiased_sample_variance = None if sample_count == 1 else squared_deviations / (sample_count - 1)
    estimated_standard_error = None if unbiased_sample_variance is None else sqrt(unbiased_sample_variance / sample_count)
    theoretical_standard_error = sqrt(EXACT_INTEGRAND_VARIANCE / sample_count)
    signed_error = estimate - EXACT_INTEGRAL
    return {
        "sample_count": sample_count,
        "seed": seed,
        "estimate": estimate,
        "signed_error": signed_error,
        "absolute_error": abs(signed_error),
        "unbiased_sample_variance": unbiased_sample_variance,
        "estimated_standard_error": estimated_standard_error,
        "theoretical_integrand_variance": EXACT_INTEGRAND_VARIANCE,
        "theoretical_standard_error": theoretical_standard_error,
        "error_in_theoretical_standard_errors": signed_error / theoretical_standard_error,
    }


def unit_square_integration_report(grid_subdivisions: object, monte_carlo_samples: object, seed: object) -> dict[str, object]:
    """Compare deterministic midpoint cells with reproducible random samples."""
    subdivisions = _positive_int(grid_subdivisions, "grid_subdivisions", 128)
    samples = _positive_int(monte_carlo_samples, "monte_carlo_samples", 100_000)
    random_seed = _seed(seed)
    return {
        "contract_version": UNIT_SQUARE_INTEGRATION_CONTRACT_VERSION,
        "domain": {"x": [0.0, 1.0], "y": [0.0, 1.0], "area": 1.0},
        "integrand": "x_squared_plus_y",
        "exact_integral": EXACT_INTEGRAL,
        "grid_midpoint": _grid_midpoint(subdivisions),
        "monte_carlo": _monte_carlo(samples, random_seed),
        "interpretation": "fixed benchmark only; grid uses a tensor product, the sample standard error is unavailable for one draw, and neither sample nor theoretical standard error is a guaranteed error bound",
    }


def unit_square_integration_certificate(grid_subdivisions: object, monte_carlo_samples: object, seed: object, report: object) -> bool:
    """Rebuild the benchmark to reject altered samples, errors, or interpretations."""
    if not isinstance(report, dict):
        return False
    try:
        return report == unit_square_integration_report(grid_subdivisions, monte_carlo_samples, seed)
    except (TypeError, ValueError):
        return False
