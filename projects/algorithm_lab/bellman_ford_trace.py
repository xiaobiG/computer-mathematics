"""Bellman--Ford with round-by-round certificates for teaching shortest paths."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite


Edge = tuple[int, int, float]


@dataclass(frozen=True)
class BellmanFordEvent:
    """Improvements made when considering paths with one more edge."""

    round_number: int
    relaxed: tuple[tuple[int, int, float], ...]


def _validate_input(vertex_count: int, edges: list[Edge], source: int) -> None:
    if not isinstance(vertex_count, int) or isinstance(vertex_count, bool) or vertex_count <= 0:
        raise ValueError("vertex_count must be a positive integer")
    if not isinstance(source, int) or isinstance(source, bool) or not 0 <= source < vertex_count:
        raise ValueError("source must be a valid vertex")
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 3:
            raise ValueError("each edge must be a (source, target, weight) tuple")
        left, right, weight = edge
        if (not isinstance(left, int) or isinstance(left, bool) or not 0 <= left < vertex_count
                or not isinstance(right, int) or isinstance(right, bool) or not 0 <= right < vertex_count
                or not isinstance(weight, (int, float)) or isinstance(weight, bool) or not isfinite(weight)):
            raise ValueError("edge endpoints and weights must be finite valid values")


def bellman_ford_trace(
    vertex_count: int, edges: list[Edge], source: int,
) -> tuple[list[float], list[int | None], list[BellmanFordEvent]]:
    """Return exact-edge-round distances, parents and a relaxation trace.

    Each round reads the prior round instead of updating in place.  Consequently
    after event ``k``, every distance is the optimum over paths using at most
    ``k`` edges, matching the lesson's induction invariant directly.
    """
    _validate_input(vertex_count, edges, source)
    distances = [inf] * vertex_count
    parents: list[int | None] = [None] * vertex_count
    distances[source] = 0.0
    events: list[BellmanFordEvent] = []
    for round_number in range(1, vertex_count):
        prior = distances
        next_distances = prior.copy()
        next_parents = parents.copy()
        relaxed = []
        for left, right, weight in edges:
            candidate = prior[left] + weight
            if prior[left] != inf and candidate < next_distances[right]:
                next_distances[right] = candidate
                next_parents[right] = left
                relaxed.append((left, right, candidate))
        distances, parents = next_distances, next_parents
        events.append(BellmanFordEvent(round_number, tuple(relaxed)))
        if not relaxed:
            break
    if any(distances[left] != inf and distances[left] + weight < distances[right]
           for left, right, weight in edges):
        raise ValueError("a negative cycle is reachable from the source")
    return distances, parents, events


def reconstruct_path(parents: list[int | None], source: int, target: int) -> list[int] | None:
    """Recover a source-to-target path while rejecting malformed parent cycles."""
    if not 0 <= source < len(parents) or not 0 <= target < len(parents):
        raise ValueError("source and target must be valid vertices")
    path = []
    node: int | None = target
    for _ in range(len(parents) + 1):
        if node is None:
            return None
        path.append(node)
        if node == source:
            return list(reversed(path))
        node = parents[node]
    raise ValueError("parents contain a cycle")


def bellman_ford_certificate(
    vertex_count: int,
    edges: list[Edge],
    source: int,
    distances: list[float],
    parents: list[int | None],
    events: list[BellmanFordEvent],
) -> dict[str, bool]:
    """Recompute a finite Bellman--Ford run and audit its shortest-path proof.

    Parent paths provide a witness that each finite label is attainable.  The
    final edge inequalities provide the complementary lower bound: repeatedly
    extending any source path cannot produce a shorter label.  The replayed
    rounds additionally make the lesson's "at most k edges" invariant
    inspectable rather than trusting a final distance vector alone.
    """
    empty = {
        "trace_matches_edge_rounds": False,
        "labels_match_recomputed_run": False,
        "parent_witnesses_match_labels": False,
        "all_edges_respect_final_labels": False,
        "valid": False,
    }
    try:
        _validate_input(vertex_count, edges, source)
        expected_distances, expected_parents, expected_events = bellman_ford_trace(vertex_count, edges, source)
        if len(distances) != vertex_count or len(parents) != vertex_count:
            return empty

        labels_match = distances == expected_distances and parents == expected_parents
        trace_matches = events == expected_events
        edge_weights: dict[tuple[int, int], float] = {}
        for left, right, weight in edges:
            edge_weights[left, right] = min(edge_weights.get((left, right), inf), weight)

        witnesses_match = True
        for target, distance in enumerate(distances):
            path = reconstruct_path(parents, source, target)
            if distance == inf:
                witnesses_match = witnesses_match and path is None
                continue
            if path is None:
                witnesses_match = False
                break
            path_weight = sum(edge_weights.get((left, right), inf) for left, right in zip(path, path[1:]))
            if path_weight != distance:
                witnesses_match = False
                break

        edge_inequalities = all(
            distances[left] == inf or distances[right] <= distances[left] + weight
            for left, right, weight in edges
        )
        return {
            "trace_matches_edge_rounds": trace_matches,
            "labels_match_recomputed_run": labels_match,
            "parent_witnesses_match_labels": witnesses_match,
            "all_edges_respect_final_labels": edge_inequalities,
            "valid": trace_matches and labels_match and witnesses_match and edge_inequalities,
        }
    except (ArithmeticError, IndexError, TypeError, ValueError):
        return empty
