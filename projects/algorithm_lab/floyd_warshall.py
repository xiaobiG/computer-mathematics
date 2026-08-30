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


def floyd_warshall_with_paths(
    vertex_count: int, edges: list[tuple[int, int, float]],
) -> tuple[list[list[float]], list[list[int | None]]]:
    """Return all-pairs distances plus the next-hop matrix for path recovery."""
    distance = _initial_distance(vertex_count, edges)
    next_hop: list[list[int | None]] = [[None] * vertex_count for _ in range(vertex_count)]
    for source in range(vertex_count):
        next_hop[source][source] = source
    for source, target, weight in edges:
        if float(weight) == distance[source][target]:
            next_hop[source][target] = target

    for middle in range(vertex_count):
        for source in range(vertex_count):
            for target in range(vertex_count):
                through_middle = distance[source][middle] + distance[middle][target]
                if through_middle < distance[source][target]:
                    distance[source][target] = through_middle
                    next_hop[source][target] = next_hop[source][middle]
    if any(distance[vertex][vertex] < 0 for vertex in range(vertex_count)):
        raise ValueError("negative cycle makes shortest paths undefined")
    return distance, next_hop


def recover_floyd_warshall_path(
    next_hop: list[list[int | None]], source: int, target: int,
) -> list[int] | None:
    """Recover one shortest path, or ``None`` for an unreachable target."""
    vertex_count = len(next_hop)
    if (vertex_count == 0 or any(len(row) != vertex_count for row in next_hop)
            or not all(isinstance(vertex, int) and not isinstance(vertex, bool)
                       and 0 <= vertex < vertex_count
                       for vertex in (source, target))):
        raise ValueError("next-hop matrix must be square and endpoints in range")
    if source == target:
        return [source]
    if next_hop[source][target] is None:
        return None
    path = [source]
    current = source
    for _ in range(vertex_count):
        current = next_hop[current][target]
        if current is None or not isinstance(current, int) or not 0 <= current < vertex_count:
            raise ValueError("next-hop matrix contains an invalid path link")
        path.append(current)
        if current == target:
            return path
    raise ValueError("next-hop matrix contains a cycle without reaching target")


def floyd_warshall_path_certificate(
    vertex_count: int, edges: list[tuple[int, int, float]],
    distance: list[list[float]], next_hop: list[list[int | None]],
    source: int, target: int, path: list[int] | None,
) -> bool:
    """Replay all-pairs path construction and bind one recovered path to it."""
    try:
        expected_distance, expected_next_hop = floyd_warshall_with_paths(vertex_count, edges)
        return (
            distance == expected_distance
            and next_hop == expected_next_hop
            and path == recover_floyd_warshall_path(expected_next_hop, source, target)
        )
    except (ArithmeticError, TypeError, ValueError):
        return False
