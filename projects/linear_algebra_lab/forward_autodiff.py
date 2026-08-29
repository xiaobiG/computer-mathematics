"""Minimal forward-mode automatic differentiation with dual numbers."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, sin
from typing import Callable

from projects.linear_algebra_lab.gradient_check import demo_loss_gradient


@dataclass(frozen=True)
class Dual:
    """A primal value paired with its derivative along one chosen direction."""

    value: float
    tangent: float

    def __add__(self, other: Dual | float) -> Dual:
        right = _as_dual(other)
        return Dual(self.value + right.value, self.tangent + right.tangent)

    def __radd__(self, other: Dual | float) -> Dual:
        return self + other

    def __mul__(self, other: Dual | float) -> Dual:
        right = _as_dual(other)
        return Dual(self.value * right.value, self.tangent * right.value + self.value * right.tangent)

    def __rmul__(self, other: Dual | float) -> Dual:
        return self * other

    def __pow__(self, exponent: int) -> Dual:
        if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
            raise ValueError("teaching dual powers require a non-negative integer exponent")
        if exponent == 0:
            return Dual(1.0, 0.0)
        return Dual(self.value ** exponent, exponent * self.value ** (exponent - 1) * self.tangent)


def _as_dual(value: Dual | float) -> Dual:
    if isinstance(value, Dual):
        return value
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError("dual operands must be finite real values")
    return Dual(float(value), 0.0)


def dual_sin(value: Dual) -> Dual:
    return Dual(sin(value.value), cos(value.value) * value.tangent)


DualFunction = Callable[[list[Dual]], Dual]


def forward_jvp(function: DualFunction, point: list[float], direction: list[float]) -> Dual:
    """Evaluate a scalar function and its Jacobian-vector product in one pass."""
    if (not point or len(point) != len(direction)
            or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                   for value in point + direction)):
        raise ValueError("point and direction must be equally sized non-empty finite vectors")
    result = function([Dual(float(value), float(tangent)) for value, tangent in zip(point, direction)])
    if not isinstance(result, Dual) or not isfinite(result.value) or not isfinite(result.tangent):
        raise ValueError("dual function must return a finite Dual value")
    return result


def demo_loss_dual(variables: list[Dual]) -> Dual:
    """The computation graph for L(x,y)=(xy+sin x)^2 in dual arithmetic."""
    if len(variables) != 2:
        raise ValueError("demo loss expects exactly two variables")
    intermediate = variables[0] * variables[1] + dual_sin(variables[0])
    return intermediate ** 2


def demo_jvp_certificate(point: list[float], direction: list[float], tolerance: float = 1e-12) -> dict[str, float | bool]:
    """Compare forward-mode JVP with grad(L)^T direction for the demo graph."""
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    result = forward_jvp(demo_loss_dual, point, direction)
    reverse_identity = sum(gradient * tangent for gradient, tangent in zip(demo_loss_gradient(point), direction))
    return {
        "value": result.value,
        "forward_jvp": result.tangent,
        "gradient_dot_direction": reverse_identity,
        "matches": abs(result.tangent - reverse_identity) <= tolerance * max(
            1.0, abs(result.tangent), abs(reverse_identity),
        ),
    }
