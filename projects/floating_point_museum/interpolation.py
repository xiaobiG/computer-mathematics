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


def interpolation_certificate(
    nodes: list[float], values: list[float], coefficients: list[float], *, tolerance: float = 1e-12
) -> dict[str, bool]:
    """Recompute Newton coefficients and audit every interpolation-node residual."""
    empty = {
        "coefficients_match_divided_differences": False,
        "all_nodes_are_reconstructed_within_tolerance": False,
        "valid": False,
    }
    try:
        if tolerance < 0.0 or not isfinite(tolerance):
            return empty
        expected = divided_differences(nodes, values)
        if len(coefficients) != len(expected) or any(not isfinite(value) for value in coefficients):
            return empty
        coefficients_match = all(
            abs(actual - target) <= tolerance * max(1.0, abs(actual), abs(target))
            for actual, target in zip(coefficients, expected)
        )
        nodes_match = all(
            abs(evaluate_newton(nodes, coefficients, node) - value)
            <= tolerance * max(1.0, abs(value))
            for node, value in zip(nodes, values)
        )
        return {
            "coefficients_match_divided_differences": coefficients_match,
            "all_nodes_are_reconstructed_within_tolerance": nodes_match,
            "valid": coefficients_match and nodes_match,
        }
    except (TypeError, ValueError):
        return empty
