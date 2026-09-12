"""Replayable boundaries for source-target shortest-path work and storage."""

from __future__ import annotations

from collections import deque
from heapq import heappop, heappush
from itertools import count
from math import inf

from projects.algorithm_lab.bellman_ford_trace import bellman_ford_trace
from projects.algorithm_lab.floyd_warshall import floyd_warshall
from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    normalize_shortest_path_input,
)


QUERY_BOUNDARY_CONTRACT_VERSION = "shortest-path-query-boundary/v1"


def _graph(vertex_count: int, edges: list[tuple[int, int, float]]) -> dict[int, list[tuple[int, float]]]:
    graph = {vertex: [] for vertex in range(vertex_count)}
    for left, right, weight in edges:
        graph[left].append((right, weight))
    return graph


def _bfs_work(graph: dict[int, list[tuple[int, float]]], source: int, target: int, stop_at_target: bool) -> dict[str, int | bool]:
    queue = deque([source])
    seen = {source}
    edge_scans = settled_vertices = 0
    while queue:
        vertex = queue.popleft()
        settled_vertices += 1
        if stop_at_target and vertex == target:
            return {"edge_scans": edge_scans, "settled_vertices": settled_vertices, "target_reached": True}
        for neighbor, _ in graph[vertex]:
            edge_scans += 1
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return {"edge_scans": edge_scans, "settled_vertices": settled_vertices, "target_reached": target in seen}


def _dijkstra_work(graph: dict[int, list[tuple[int, float]]], source: int, target: int, stop_at_target: bool) -> dict[str, int | bool]:
    distances = {vertex: inf for vertex in graph}
    distances[source] = 0.0
    sequence = count()
    heap = [(0.0, next(sequence), source)]
    edge_scans = settled_vertices = 0
    while heap:
        distance, _, vertex = heappop(heap)
        if distance != distances[vertex]:
            continue
        settled_vertices += 1
        if stop_at_target and vertex == target:
            return {"edge_scans": edge_scans, "settled_vertices": settled_vertices, "target_reached": True}
        for neighbor, weight in graph[vertex]:
            edge_scans += 1
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                heappush(heap, (candidate, next(sequence), neighbor))
    return {"edge_scans": edge_scans, "settled_vertices": settled_vertices, "target_reached": distances[target] != inf}


def shortest_path_query_boundary_report(payload: object) -> dict[str, object]:
    """Measure safe target stopping, graph density, and storage on one contract input.

    The full-source counters intentionally continue past the target; target-only
    counters stop only where the corresponding invariant permits it.  This
    makes the difference between a destination query and an all-distances query
    auditable instead of assuming they cost the same.
    """
    normalized = normalize_shortest_path_input(payload)
    vertex_count = normalized["vertex_count"]
    source = normalized["source"]
    target = normalized["target"]
    edges = [tuple(edge) for edge in normalized["edges"]]
    graph = _graph(vertex_count, edges)  # type: ignore[arg-type]
    all_unit = all(weight == 1.0 for _, _, weight in edges)
    all_nonnegative = all(weight >= 0.0 for _, _, weight in edges)
    possible_nonloop_edges = vertex_count * (vertex_count - 1)
    unique_nonloop_edges = {(left, right) for left, right, _ in edges if left != right}
    density = len(unique_nonloop_edges) / possible_nonloop_edges
    density_class = "sparse" if density <= 0.5 else "dense"
    algorithms: dict[str, dict[str, object]] = {}

    if all_unit:
        algorithms["bfs"] = {
            "status": "applicable",
            "theory": "O(V+E) per source; target may stop at first dequeue",
            "full_source": _bfs_work(graph, source, target, False),
            "target_only": _bfs_work(graph, source, target, True),
        }
    else:
        algorithms["bfs"] = {"status": "rejected", "reason": "non_unit_weights"}

    if all_nonnegative:
        algorithms["dijkstra"] = {
            "status": "applicable",
            "theory": "O((V+E) log V) per source; target may stop when settled",
            "full_source": _dijkstra_work(graph, source, target, False),
            "target_only": _dijkstra_work(graph, source, target, True),
        }
    else:
        algorithms["dijkstra"] = {"status": "rejected", "reason": "negative_edge"}

    try:
        _, _, events = bellman_ford_trace(vertex_count, edges, source)  # type: ignore[arg-type]
        algorithms["bellman_ford"] = {
            "status": "applicable",
            "theory": "O(VE) per source",
            "full_source": {"rounds": len(events), "edge_scans": len(events) * len(edges)},
            "target_only": {"status": "not_safe", "reason": "a later relaxation can still improve the target"},
        }
    except ValueError:
        algorithms["bellman_ford"] = {"status": "rejected", "reason": "reachable_negative_cycle"}

    try:
        floyd_warshall(vertex_count, edges)  # type: ignore[arg-type]
        algorithms["floyd_warshall"] = {
            "status": "applicable",
            "theory": "O(V³) preprocessing for all source-target pairs",
            "full_source": {"candidate_cells": vertex_count ** 3},
            "target_only": {"status": "not_safe", "reason": "the DP matrix is still all-pairs"},
        }
    except ValueError:
        algorithms["floyd_warshall"] = {"status": "rejected", "reason": "negative_cycle"}

    return {
        "contract_version": QUERY_BOUNDARY_CONTRACT_VERSION,
        "input_contract_version": CONTRACT_VERSION,
        "input": normalized,
        "graph": {
            "unique_nonloop_edges": len(unique_nonloop_edges),
            "possible_nonloop_edges": possible_nonloop_edges,
            "directed_density": density,
            "density_class": density_class,
        },
        "storage": {
            "adjacency_list_slots": vertex_count + len(edges),
            "floyd_matrix_cells": vertex_count ** 2,
        },
        "algorithms": algorithms,
    }


def shortest_path_query_boundary_certificate(payload: object, report: object) -> bool:
    """Replay source-target boundaries and reject changed counts or safety claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == shortest_path_query_boundary_report(payload)
    except (TypeError, ValueError):
        return False
