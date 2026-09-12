"""Newton divided-difference interpolation for small teaching examples."""

from __future__ import annotations

from math import cos, isfinite, pi


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


def _runge_value(point: float) -> float:
    return 1.0 / (1.0 + 25.0 * point * point)


def _runge_nodes(node_count: int, kind: str) -> list[float]:
    if kind == "uniform":
        return [-1.0 + 2.0 * index / (node_count - 1) for index in range(node_count)]
    if kind == "chebyshev":
        return sorted(cos((2 * index + 1) * pi / (2 * node_count)) for index in range(node_count))
    raise ValueError("unknown node kind")


def runge_node_comparison_report(node_count: int = 11, grid_points: int = 401) -> dict[str, object]:
    """Compare equal-size uniform and Chebyshev interpolation on Runge's function.

    The report is a fixed, finite experiment for ``1 / (1 + 25x²)`` on
    [-1, 1].  It demonstrates one node-placement tradeoff, not a universal
    preference for global polynomial interpolation.
    """
    if (not isinstance(node_count, int) or isinstance(node_count, bool) or node_count < 3
            or not isinstance(grid_points, int) or isinstance(grid_points, bool) or grid_points < 3):
        raise ValueError("node_count and grid_points must be integers of at least three")
    grid = [-1.0 + 2.0 * index / (grid_points - 1) for index in range(grid_points)]

    def evaluate(kind: str) -> dict[str, object]:
        nodes = _runge_nodes(node_count, kind)
        values = [_runge_value(node) for node in nodes]
        coefficients = divided_differences(nodes, values)
        errors = [abs(evaluate_newton(nodes, coefficients, point) - _runge_value(point)) for point in grid]
        edge_errors = [error for point, error in zip(grid, errors) if abs(point) >= .8]
        return {
            "nodes": tuple(nodes),
            "max_absolute_error": max(errors),
            "edge_max_absolute_error": max(edge_errors),
            "interpolation_certificate": interpolation_certificate(nodes, values, coefficients),
        }

    uniform = evaluate("uniform")
    chebyshev = evaluate("chebyshev")
    return {
        "function": "runge/1/(1+25x^2)",
        "node_count": node_count,
        "grid_points": grid_points,
        "uniform": uniform,
        "chebyshev": chebyshev,
        "chebyshev_has_smaller_max_error": chebyshev["max_absolute_error"] < uniform["max_absolute_error"],
        "chebyshev_has_smaller_edge_error": chebyshev["edge_max_absolute_error"] < uniform["edge_max_absolute_error"],
    }


def runge_node_comparison_certificate(node_count: int, grid_points: int, report: object) -> bool:
    """Replay the fixed Runge experiment and reject altered node-choice claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == runge_node_comparison_report(node_count, grid_points)
    except (TypeError, ValueError):
        return False
