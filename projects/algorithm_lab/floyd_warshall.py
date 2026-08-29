"""Floyd–Warshall 全源最短路的教学实现，含负环检测。"""

from __future__ import annotations

from math import inf


def floyd_warshall(vertex_count: int, edges: list[tuple[int, int, float]]) -> list[list[float]]:
    """Return all-pairs distances, or reject a graph containing a negative cycle."""
    if vertex_count <= 0:
        raise ValueError("vertex_count must be positive")
    distance = [[inf] * vertex_count for _ in range(vertex_count)]
    for vertex in range(vertex_count):
        distance[vertex][vertex] = 0.0
    for source, target, weight in edges:
        if not (0 <= source < vertex_count and 0 <= target < vertex_count):
            raise ValueError("edge endpoint is out of range")
        distance[source][target] = min(distance[source][target], float(weight))

    for middle in range(vertex_count):
        for source in range(vertex_count):
            for target in range(vertex_count):
                through_middle = distance[source][middle] + distance[middle][target]
                if through_middle < distance[source][target]:
                    distance[source][target] = through_middle
    if any(distance[vertex][vertex] < 0 for vertex in range(vertex_count)):
        raise ValueError("negative cycle makes shortest paths undefined")
    return distance
