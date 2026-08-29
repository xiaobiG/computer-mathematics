"""Floyd–Warshall 全源最短路的教学实现，含负环检测。"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite


@dataclass(frozen=True)
class FloydWarshallEvent:
    """Distance matrix after one newly allowed intermediate vertex."""

    middle: int
    distance: tuple[tuple[float, ...], ...]


def _initial_distance(vertex_count: int, edges: list[tuple[int, int, float]]) -> list[list[float]]:
    if not isinstance(vertex_count, int) or isinstance(vertex_count, bool) or vertex_count <= 0:
        raise ValueError("vertex_count must be a positive integer")
    distance = [[inf] * vertex_count for _ in range(vertex_count)]
    for vertex in range(vertex_count):
        distance[vertex][vertex] = 0.0
    for source, target, weight in edges:
        if not (0 <= source < vertex_count and 0 <= target < vertex_count):
            raise ValueError("edge endpoint is out of range")
        if not isfinite(weight):
            raise ValueError("edge weights must be finite")
        distance[source][target] = min(distance[source][target], float(weight))
    return distance


def floyd_warshall(vertex_count: int, edges: list[tuple[int, int, float]]) -> list[list[float]]:
    """Return all-pairs distances, or reject a graph containing a negative cycle."""
    distance, _ = floyd_warshall_trace(vertex_count, edges)
    return distance


def floyd_warshall_trace(
    vertex_count: int, edges: list[tuple[int, int, float]],
) -> tuple[list[list[float]], list[FloydWarshallEvent]]:
    """Return all-pairs distances and one DP state snapshot per middle vertex."""
    distance = _initial_distance(vertex_count, edges)
    events: list[FloydWarshallEvent] = []

    for middle in range(vertex_count):
        for source in range(vertex_count):
            for target in range(vertex_count):
                through_middle = distance[source][middle] + distance[middle][target]
                if through_middle < distance[source][target]:
                    distance[source][target] = through_middle
        events.append(FloydWarshallEvent(
            middle, tuple(tuple(row) for row in distance),
        ))
    if any(distance[vertex][vertex] < 0 for vertex in range(vertex_count)):
        raise ValueError("negative cycle makes shortest paths undefined")
    return distance, events


def floyd_warshall_trace_certificate(
    vertex_count: int,
    edges: list[tuple[int, int, float]],
    result: list[list[float]],
    events: list[FloydWarshallEvent],
) -> bool:
    """Replay every allowed-intermediate DP layer and verify the final matrix."""
    try:
        distance = _initial_distance(vertex_count, edges)
        if not isinstance(result, list) or len(events) != vertex_count:
            return False
        for middle, event in enumerate(events):
            for source in range(vertex_count):
                for target in range(vertex_count):
                    through_middle = distance[source][middle] + distance[middle][target]
                    if through_middle < distance[source][target]:
                        distance[source][target] = through_middle
            if event != FloydWarshallEvent(middle, tuple(tuple(row) for row in distance)):
                return False
        return (
            not any(distance[vertex][vertex] < 0 for vertex in range(vertex_count))
            and result == distance
        )
    except (ArithmeticError, TypeError, ValueError):
        return False
