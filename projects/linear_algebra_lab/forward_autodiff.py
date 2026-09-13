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


@dataclass(eq=False)
class ReverseNode:
    """One scalar graph node holding the local derivatives of its inputs."""

    value: float
    parents: tuple[tuple["ReverseNode", float], ...] = ()
    adjoint: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.value) or not isfinite(self.adjoint):
            raise ValueError("reverse nodes must have finite values and adjoints")
        if any(not isfinite(local_derivative) for _, local_derivative in self.parents):
            raise ValueError("reverse local derivatives must be finite")

    def __add__(self, other: "ReverseNode | float") -> "ReverseNode":
        right = _as_reverse(other)
        return ReverseNode(self.value + right.value, ((self, 1.0), (right, 1.0)))

    def __radd__(self, other: "ReverseNode | float") -> "ReverseNode":
        return self + other

    def __mul__(self, other: "ReverseNode | float") -> "ReverseNode":
        right = _as_reverse(other)
        return ReverseNode(self.value * right.value, ((self, right.value), (right, self.value)))

    def __rmul__(self, other: "ReverseNode | float") -> "ReverseNode":
        return self * other

    def __pow__(self, exponent: int) -> "ReverseNode":
        if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
            raise ValueError("teaching reverse powers require a non-negative integer exponent")
        if exponent == 0:
            return ReverseNode(1.0)
        return ReverseNode(self.value ** exponent, ((self, exponent * self.value ** (exponent - 1)),))


def _as_reverse(value: ReverseNode | float) -> ReverseNode:
    if isinstance(value, ReverseNode):
        return value
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError("reverse operands must be finite real values")
    return ReverseNode(float(value))


def reverse_sin(value: ReverseNode) -> ReverseNode:
    return ReverseNode(sin(value.value), ((value, cos(value.value)),))


ReverseFunction = Callable[[list[ReverseNode]], ReverseNode]


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


def reverse_vjp(function: ReverseFunction, point: list[float]) -> tuple[float, list[float]]:
    """Propagate a scalar output seed of 1 through a small computation graph.

    Every edge adds ``node.adjoint * local_derivative`` to its parent.  Shared
    parents therefore collect all downstream paths, making the returned input
    adjoints the scalar-output VJP (the gradient).
    """
    if (not point or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                         for value in point)):
        raise ValueError("point must be a non-empty finite vector")
    inputs = [ReverseNode(float(value)) for value in point]
    output = function(inputs)
    if not isinstance(output, ReverseNode) or not isfinite(output.value):
        raise ValueError("reverse function must return a finite ReverseNode value")

    ordered: list[ReverseNode] = []
    visited: set[int] = set()

    def visit(node: ReverseNode) -> None:
        if id(node) in visited:
            return
        visited.add(id(node))
        node.adjoint = 0.0
        for parent, _ in node.parents:
            visit(parent)
        ordered.append(node)

    visit(output)
    output.adjoint = 1.0
    for node in reversed(ordered):
        for parent, local_derivative in node.parents:
            parent.adjoint += node.adjoint * local_derivative
    gradient = [node.adjoint for node in inputs]
    if any(not isfinite(value) for value in gradient):
        raise ValueError("reverse VJP produced a non-finite gradient")
    return output.value, gradient


def demo_loss_dual(variables: list[Dual]) -> Dual:
    """The computation graph for L(x,y)=(xy+sin x)^2 in dual arithmetic."""
    if len(variables) != 2:
        raise ValueError("demo loss expects exactly two variables")
    intermediate = variables[0] * variables[1] + dual_sin(variables[0])
    return intermediate ** 2


def demo_loss_reverse(variables: list[ReverseNode]) -> ReverseNode:
    """The same L(x,y) graph, retaining parent links for reverse mode."""
    if len(variables) != 2:
        raise ValueError("demo loss expects exactly two variables")
    intermediate = variables[0] * variables[1] + reverse_sin(variables[0])
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


def demo_reverse_vjp_certificate(point: list[float], tolerance: float = 1e-12) -> dict[str, object]:
    """Check that one reverse traversal returns every demo-loss gradient entry."""
    if tolerance <= 0 or not isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    value, reverse_gradient = reverse_vjp(demo_loss_reverse, point)
    analytic_gradient = demo_loss_gradient(point)
    absolute_error = [abs(reverse - analytic) for reverse, analytic in zip(reverse_gradient, analytic_gradient)]
    return {
        "value": value,
        "reverse_vjp": reverse_gradient,
        "analytic_gradient": analytic_gradient,
        "absolute_error": absolute_error,
        "matches": all(error <= tolerance * max(1.0, abs(reverse), abs(analytic))
                       for error, reverse, analytic in zip(absolute_error, reverse_gradient, analytic_gradient)),
    }


def demo_loss_hessian(point: list[float]) -> list[list[float]]:
    """Return the analytic Hessian of L(x,y)=(xy+sin(x))^2."""
    if len(point) != 2 or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                              for value in point):
        raise ValueError("demo loss expects exactly two finite variables")
    x, y = point
    intermediate = x * y + sin(x)
    slope_x = y + cos(x)
    return [
        [2.0 * slope_x * slope_x - 2.0 * intermediate * sin(x), 2.0 * x * slope_x + 2.0 * intermediate],
        [2.0 * x * slope_x + 2.0 * intermediate, 2.0 * x * x],
    ]


def demo_hvp_certificate(
    point: list[float], direction: list[float], *, step: float = 1e-5, tolerance: float = 1e-7,
) -> dict[str, object]:
    """Compare H(point) @ direction with a central difference of gradients.

    The finite difference is a small-scale test oracle only: its step has both
    truncation and round-off error, unlike the analytic Hessian product.
    """
    if (len(point) != 2 or len(direction) != 2
            or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                   for value in point + direction)
            or not isfinite(step) or not isfinite(tolerance) or step <= 0 or tolerance <= 0):
        raise ValueError("point, direction, step and tolerance must be finite valid values")
    hessian = demo_loss_hessian(point)
    analytic_hvp = [sum(row[column] * direction[column] for column in range(2)) for row in hessian]
    plus = [coordinate + step * tangent for coordinate, tangent in zip(point, direction)]
    minus = [coordinate - step * tangent for coordinate, tangent in zip(point, direction)]
    plus_gradient = demo_loss_gradient(plus)
    minus_gradient = demo_loss_gradient(minus)
    numerical_hvp = [(upper - lower) / (2.0 * step) for upper, lower in zip(plus_gradient, minus_gradient)]
    absolute_error = [abs(left - right) for left, right in zip(analytic_hvp, numerical_hvp)]
    return {
        "hessian": hessian,
        "analytic_hvp": analytic_hvp,
        "numerical_hvp": numerical_hvp,
        "absolute_error": absolute_error,
        "matches": all(error <= tolerance * max(1.0, abs(analytic), abs(numerical))
                       for error, analytic, numerical in zip(absolute_error, analytic_hvp, numerical_hvp)),
    }
