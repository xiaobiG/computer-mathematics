"""Newton divided-difference interpolation for small teaching examples."""

from __future__ import annotations

from math import isfinite


def _validate(nodes: list[float], values: list[float]) -> None:
    if not nodes or len(nodes) != len(values) or len(set(nodes)) != len(nodes):
        raise ValueError("nodes and values must have equal nonzero length and distinct nodes")
    if any(not isfinite(value) for value in nodes + values):
        raise ValueError("nodes and values must be finite")


def divided_differences(nodes: list[float], values: list[float]) -> list[float]:
    """Return Newton coefficients c_k = f[x_0, ..., x_k]."""
    _validate(nodes, values)
    work = [float(value) for value in values]
    coefficients = [work[0]]
    for order in range(1, len(nodes)):
        for index in range(len(nodes) - 1, order - 1, -1):
            work[index] = (work[index] - work[index - 1]) / (nodes[index] - nodes[index - order])
        coefficients.append(work[order])
    return coefficients


def evaluate_newton(nodes: list[float], coefficients: list[float], point: float) -> float:
    """Evaluate c_0 + c_1(x-x_0) + ... by nested multiplication."""
    if not nodes or len(nodes) != len(coefficients) or not isfinite(point):
        raise ValueError("nodes, coefficients and point must be finite and have matching nonzero length")
    result = coefficients[-1]
    for index in range(len(coefficients) - 2, -1, -1):
        result = coefficients[index] + (point - nodes[index]) * result
    return result
