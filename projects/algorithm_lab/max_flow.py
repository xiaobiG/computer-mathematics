"""Edmonds--Karp maximum flow with an inspectable augmenting-path trace."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Augmentation:
    path: tuple[int, ...]
    bottleneck: float
    total_flow: float


def max_flow(
    vertex_count: int, edges: list[tuple[int, int, float]], source: int, sink: int
) -> tuple[float, set[int], list[Augmentation]]:
    """Return max-flow value, source-side residual cut, and BFS augmentations.

    Parallel edges are deliberately accumulated.  The returned source-side set
    is a certificate: when no residual s--t path remains, its original outgoing
    capacity equals the achieved flow under exact arithmetic.
    """
    if vertex_count <= 1 or not (0 <= source < vertex_count and 0 <= sink < vertex_count) or source == sink:
        raise ValueError("need distinct in-range source and sink in a graph with at least two vertices")
    residual = [[0.0] * vertex_count for _ in range(vertex_count)]
    for left, right, capacity in edges:
        if not (0 <= left < vertex_count and 0 <= right < vertex_count) or capacity < 0:
            raise ValueError("edge endpoints must be in range and capacities nonnegative")
        residual[left][right] += float(capacity)

    value = 0.0
    trace: list[Augmentation] = []
    while True:
        parent = [-1] * vertex_count
        parent[source] = source
        queue = deque([source])
        while queue and parent[sink] == -1:
            left = queue.popleft()
            for right, capacity in enumerate(residual[left]):
                if capacity > 0 and parent[right] == -1:
                    parent[right] = left
                    queue.append(right)
                    if right == sink:
                        break
        if parent[sink] == -1:
            break

        path = [sink]
        while path[-1] != source:
            path.append(parent[path[-1]])
        path.reverse()
        bottleneck = min(residual[left][right] for left, right in zip(path, path[1:]))
        for left, right in zip(path, path[1:]):
            residual[left][right] -= bottleneck
            residual[right][left] += bottleneck
        value += bottleneck
        trace.append(Augmentation(tuple(path), bottleneck, value))

    reachable = {source}
    queue = deque([source])
    while queue:
        left = queue.popleft()
        for right, capacity in enumerate(residual[left]):
            if capacity > 0 and right not in reachable:
                reachable.add(right)
                queue.append(right)
    return value, reachable, trace
