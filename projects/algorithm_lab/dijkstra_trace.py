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


def _validate_graph(graph: Graph, start: Node) -> None:
    if start not in graph:
        raise ValueError("start must be a graph key")
    for neighbors in graph.values():
        for neighbor, weight in neighbors:
            if neighbor not in graph or weight < 0 or not isfinite(weight):
                raise ValueError("every neighbor must be a graph key with a finite non-negative weight")


def dijkstra_trace(graph: Graph, start: Node) -> tuple[dict[Node, float], dict[Node, Node | None], list[DijkstraEvent]]:
    """Return shortest-distance upper bounds, parents, and settled-node trace."""
    _validate_graph(graph, start)
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


def shortest_path_certificate(
    graph: Graph, start: Node, distances: dict[Node, float], parents: dict[Node, Node | None],
    events: list[DijkstraEvent],
) -> dict[str, bool]:
    """Independently check a Dijkstra result using path and relaxation evidence.

    A finite parent path proves each reported distance is attainable.  The
    relaxation inequalities prove no path can be shorter: apply the inequality
    edge by edge along any source-to-vertex path.  With non-negative weights,
    the settled order additionally exposes the greedy invariant in the trace.
    """
    _validate_graph(graph, start)
    matching_vertices = set(distances) == set(graph)
    finite_distances = matching_vertices and all(
        isinstance(distance, (int, float)) and isfinite(distance)
        for distance in distances.values() if distance != inf
    )
    reachable = {node for node, distance in distances.items() if distance != inf}
    event_nodes = [event.node for event in events]
    settled_order_monotone = all(
        left.distance <= right.distance for left, right in zip(events, events[1:])
    )
    trace_covers_reachable = (
        len(event_nodes) == len(set(event_nodes))
        and set(event_nodes) == reachable
        and all(event.node in distances and event.distance == distances[event.node] for event in events)
    )
    all_edges_relaxed = matching_vertices and all(
        distances[target] <= distances[source] + weight
        for source, neighbors in graph.items() if distances[source] != inf
        for target, weight in neighbors
    )

    parent_paths_match_distances = matching_vertices and distances.get(start) == 0.0 and parents.get(start) is None
    for node in reachable - {start}:
        parent = parents.get(node)
        parent_edges = graph.get(parent, []) if parent in graph else []
        if parent is None or distances.get(parent, inf) == inf or not any(
            target == node and distances[parent] + weight == distances[node]
            for target, weight in parent_edges
        ):
            parent_paths_match_distances = False
            break
        seen = {node}
        cursor = parent
        while cursor != start:
            if cursor in seen or cursor not in parents or parents[cursor] is None:
                parent_paths_match_distances = False
                break
            seen.add(cursor)
            cursor = parents[cursor]
        if not parent_paths_match_distances:
            break
    if any(node in parents for node in set(graph) - reachable):
        parent_paths_match_distances = False

    valid = all((finite_distances, settled_order_monotone, trace_covers_reachable,
                 all_edges_relaxed, parent_paths_match_distances))
    return {
        "finite_distances": finite_distances,
        "settled_order_monotone": settled_order_monotone,
        "trace_covers_reachable": trace_covers_reachable,
        "all_edges_relaxed": all_edges_relaxed,
        "parent_paths_match_distances": parent_paths_match_distances,
        "valid": valid,
    }


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
