"""Small finite-difference gradient checks for testing analytic derivatives."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, sin
from typing import Callable


ScalarFunction = Callable[[list[float]], float]
GradientFunction = Callable[[list[float]], list[float]]


@dataclass(frozen=True)
class GradientCheck:
    coordinate: int
    analytic: float
    numerical: float
    absolute_error: float
    relative_error: float


def _validate_point(point: list[float], step: float) -> None:
    if not point or not all(isfinite(value) for value in point) or not isfinite(step) or step <= 0:
        raise ValueError("point must be nonempty and finite, and step must be finite and positive")


def central_gradient(function: ScalarFunction, point: list[float], step: float = 1e-6) -> list[float]:
    """Approximate a scalar gradient with two function calls per coordinate."""
    _validate_point(point, step)
    result = []
    for coordinate in range(len(point)):
        left, right = point.copy(), point.copy()
        left[coordinate] -= step
        right[coordinate] += step
        left_value, right_value = float(function(left)), float(function(right))
        if not isfinite(left_value) or not isfinite(right_value):
            raise ValueError("function must be finite at gradient-check samples")
        result.append((right_value - left_value) / (2.0 * step))
    return result


def gradient_check(function: ScalarFunction, analytic_gradient: GradientFunction, point: list[float], step: float = 1e-6) -> list[GradientCheck]:
    """Return per-coordinate absolute and scale-aware relative gradient errors."""
    numerical = central_gradient(function, point, step)
    analytic = analytic_gradient(point.copy())
    if len(analytic) != len(point) or not all(isfinite(value) for value in analytic):
        raise ValueError("analytic gradient must have one finite value per coordinate")
    return [GradientCheck(
        coordinate,
        exact,
        estimate,
        abs(exact - estimate),
        abs(exact - estimate) / max(1.0, abs(exact), abs(estimate)),
    ) for coordinate, (exact, estimate) in enumerate(zip(analytic, numerical))]


def demo_loss(point: list[float]) -> float:
    x, y = point
    return (x * y + sin(x)) ** 2


def demo_loss_gradient(point: list[float]) -> list[float]:
    x, y = point
    intermediate = x * y + sin(x)
    return [2.0 * intermediate * (y + cos(x)), 2.0 * intermediate * x]
