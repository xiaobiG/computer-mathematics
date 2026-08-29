"""Dijkstra shortest paths with a trace of settled vertices and relaxations."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf, isfinite
from typing import Hashable


Node = Hashable
Graph = dict[Node, list[tuple[Node, float]]]


@dataclass(frozen=True)
class DijkstraEvent:
    node: Node
    distance: float
    relaxed: tuple[tuple[Node, float], ...]


def dijkstra_trace(graph: Graph, start: Node) -> tuple[dict[Node, float], dict[Node, Node | None], list[DijkstraEvent]]:
    """Return shortest-distance upper bounds, parents, and settled-node trace."""
    if start not in graph:
        raise ValueError("start must be a graph key")
    for neighbors in graph.values():
        for neighbor, weight in neighbors:
            if neighbor not in graph or weight < 0 or not isfinite(weight):
                raise ValueError("every neighbor must be a graph key with a finite non-negative weight")
    distances = {node: inf for node in graph}
    parents: dict[Node, Node | None] = {start: None}
    distances[start] = 0.0
    sequence = count()
    heap = [(0.0, next(sequence), start)]
    events: list[DijkstraEvent] = []
    while heap:
        distance, _, node = heappop(heap)
        if distance != distances[node]:
            continue
        relaxed = []
        for neighbor, weight in graph[node]:
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = node
                relaxed.append((neighbor, candidate))
                heappush(heap, (candidate, next(sequence), neighbor))
        events.append(DijkstraEvent(node, distance, tuple(relaxed)))
    return distances, parents, events


def reconstruct_path(parents: dict[Node, Node | None], target: Node) -> list[Node] | None:
    """Return a source-to-target path, or None when target was unreachable."""
    if target not in parents:
        return None
    path = []
    node: Node | None = target
    while node is not None:
        path.append(node)
        node = parents[node]
    return list(reversed(path))
