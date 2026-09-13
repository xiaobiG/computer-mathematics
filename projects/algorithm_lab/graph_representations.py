"""Replayable adjacency-list / adjacency-matrix reports for small finite graphs."""

from __future__ import annotations

from collections import deque
from math import isfinite


GRAPH_REPRESENTATIONS_CONTRACT_VERSION = "graph-representations/v1"


def _count(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 32:
        raise ValueError("vertex_count must be an integer from 1 to 32")
    return value


def _edge_list(value: object, vertex_count: int, directed: bool) -> list[tuple[int, int]]:
    if not isinstance(value, list):
        raise ValueError("edges must be a list")
    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for edge in value:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError("each edge must have exactly two endpoints")
        source, target = edge
        if not isinstance(source, int) or isinstance(source, bool) or not isinstance(target, int) or isinstance(target, bool):
            raise ValueError("edge endpoints must be integer vertex indices")
        if not 0 <= source < vertex_count or not 0 <= target < vertex_count or source == target:
            raise ValueError("edges must join two distinct in-range vertices")
        key = (source, target) if directed else tuple(sorted((source, target)))
        if key in seen:
            raise ValueError("duplicate edges are not allowed")
        seen.add(key)
        edges.append((source, target))
    return edges


def _queries(value: object, vertex_count: int) -> list[tuple[int, int]]:
    if not isinstance(value, list):
        raise ValueError("queries must be a list")
    result = []
    for query in value:
        if not isinstance(query, (list, tuple)) or len(query) != 2:
            raise ValueError("each query must have two endpoints")
        source, target = query
        if not isinstance(source, int) or isinstance(source, bool) or not isinstance(target, int) or isinstance(target, bool):
            raise ValueError("query endpoints must be integer vertex indices")
        if not 0 <= source < vertex_count or not 0 <= target < vertex_count:
            raise ValueError("query endpoints must be in range")
        result.append((source, target))
    return result


def _vertex(value: object, vertex_count: int, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < vertex_count:
        raise ValueError(f"{name} must be an in-range integer vertex index")
    return value


def _weighted_edge_list(value: object, vertex_count: int, directed: bool) -> list[tuple[int, int, float | int]]:
    """Validate finite weighted edges while preserving a legitimate weight of zero."""
    if not isinstance(value, list):
        raise ValueError("weighted_edges must be a list")
    edges: list[tuple[int, int, float | int]] = []
    seen: set[tuple[int, int]] = set()
    for edge in value:
        if not isinstance(edge, (list, tuple)) or len(edge) != 3:
            raise ValueError("each weighted edge must have two endpoints and one weight")
        source, target, weight = edge
        if (not isinstance(source, int) or isinstance(source, bool)
                or not isinstance(target, int) or isinstance(target, bool)
                or not isinstance(weight, (int, float)) or isinstance(weight, bool) or not isfinite(weight)):
            raise ValueError("weighted edges need integer endpoints and finite numeric weights")
        if not 0 <= source < vertex_count or not 0 <= target < vertex_count or source == target:
            raise ValueError("weighted edges must join two distinct in-range vertices")
        key = (source, target) if directed else tuple(sorted((source, target)))
        if key in seen:
            raise ValueError("duplicate weighted edges are not allowed")
        seen.add(key)
        edges.append((source, target, weight))
    return edges


def graph_representations_report(vertex_count: object, edges: object, directed: object, queries: object) -> dict[str, object]:
    """Build both representations and bind storage and operation-count trade-offs."""
    count = _count(vertex_count)
    if not isinstance(directed, bool):
        raise ValueError("directed must be a boolean")
    edge_list = _edge_list(edges, count, directed)
    edge_queries = _queries(queries, count)
    adjacency = [[] for _ in range(count)]
    matrix = [[0 for _ in range(count)] for _ in range(count)]
    for source, target in edge_list:
        adjacency[source].append(target)
        matrix[source][target] = 1
        if not directed:
            adjacency[target].append(source)
            matrix[target][source] = 1
    for neighbors in adjacency:
        neighbors.sort()
    maximum_edges = count * (count - 1) if directed else count * (count - 1) // 2
    query_rows = []
    for source, target in edge_queries:
        list_answer = target in adjacency[source]
        matrix_answer = bool(matrix[source][target])
        query_rows.append({
            "edge": [source, target],
            "adjacency_list_answer": list_answer,
            "adjacency_matrix_answer": matrix_answer,
            "answers_agree": list_answer == matrix_answer,
            "list_neighbor_checks": len(adjacency[source]),
            "matrix_cell_checks": 1,
        })
    return {
        "contract_version": GRAPH_REPRESENTATIONS_CONTRACT_VERSION,
        "directed": directed,
        "vertex_count": count,
        "edges": [list(edge) for edge in edge_list],
        "adjacency_list": adjacency,
        "adjacency_matrix": matrix,
        "density": {"edge_count": len(edge_list), "maximum_edge_count": maximum_edges, "value": len(edge_list) / maximum_edges if maximum_edges else 0.0},
        "storage": {
            "adjacency_list_vertex_slots": count,
            "adjacency_list_neighbor_slots": sum(len(neighbors) for neighbors in adjacency),
            "adjacency_matrix_cells": count * count,
        },
        "neighbor_enumeration": [{"vertex": vertex, "list_checks": len(neighbors), "matrix_checks": count} for vertex, neighbors in enumerate(adjacency)],
        "edge_queries": query_rows,
    }


def graph_representations_certificate(vertex_count: object, edges: object, directed: object, queries: object, report: object) -> bool:
    """Reject altered adjacency, matrix, density, storage, or query claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == graph_representations_report(vertex_count, edges, directed, queries)
    except (TypeError, ValueError):
        return False


def weighted_matrix_sentinel_report(vertex_count: object, edges: object, directed: object) -> dict[str, object]:
    """Show why a weighted adjacency matrix needs a distinct no-edge sentinel.

    A zero is a valid finite edge weight, so a matrix using zero for both
    ``no edge`` and ``weight zero`` cannot reconstruct the original edge set.
    ``None`` is the explicit absence sentinel in this small teaching report.
    """
    count = _count(vertex_count)
    if not isinstance(directed, bool):
        raise ValueError("directed must be a boolean")
    edge_list = _weighted_edge_list(edges, count, directed)
    sentinel_matrix: list[list[float | int | None]] = [[None for _ in range(count)] for _ in range(count)]
    zero_sentinel_matrix: list[list[float | int]] = [[0 for _ in range(count)] for _ in range(count)]
    zero_weight_edges: list[list[int]] = []
    for source, target, weight in edge_list:
        sentinel_matrix[source][target] = weight
        zero_sentinel_matrix[source][target] = weight
        if not directed:
            sentinel_matrix[target][source] = weight
            zero_sentinel_matrix[target][source] = weight
        if weight == 0:
            zero_weight_edges.append([source, target])
    ambiguous_pairs = [
        [source, target]
        for source, target in zero_weight_edges
        if zero_sentinel_matrix[source][target] == 0
    ]
    return {
        "contract_version": GRAPH_REPRESENTATIONS_CONTRACT_VERSION,
        "directed": directed,
        "vertex_count": count,
        "weighted_edges": [[source, target, weight] for source, target, weight in edge_list],
        "no_edge_sentinel": None,
        "weighted_adjacency_matrix": sentinel_matrix,
        "zero_sentinel_matrix": zero_sentinel_matrix,
        "zero_weight_edges": zero_weight_edges,
        "ambiguous_pairs": ambiguous_pairs,
        "zero_as_no_edge_is_lossy": bool(ambiguous_pairs),
    }


def weighted_matrix_sentinel_certificate(vertex_count: object, edges: object, directed: object, report: object) -> bool:
    """Replay the sentinel counterexample and reject altered matrix claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == weighted_matrix_sentinel_report(vertex_count, edges, directed)
    except (TypeError, ValueError):
        return False


def _bfs_from_list(adjacency: list[list[int]], source: int) -> tuple[list[int | None], list[int], int]:
    distances: list[int | None] = [None] * len(adjacency)
    distances[source] = 0
    queue = deque([source])
    order, checks = [], 0
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor in adjacency[vertex]:
            checks += 1
            if distances[neighbor] is None:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)
    return distances, order, checks


def _bfs_from_matrix(matrix: list[list[int]], source: int) -> tuple[list[int | None], list[int], int]:
    distances: list[int | None] = [None] * len(matrix)
    distances[source] = 0
    queue = deque([source])
    order, checks = [], 0
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor, is_edge in enumerate(matrix[vertex]):
            checks += 1
            if is_edge and distances[neighbor] is None:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)
    return distances, order, checks


def graph_representation_bfs_report(vertex_count: object, edges: object, directed: object, source: object) -> dict[str, object]:
    """Replay the same BFS through two graph representations and count scans."""
    count = _count(vertex_count)
    start = _vertex(source, count, "source")
    representation = graph_representations_report(count, edges, directed, [])
    adjacency = representation["adjacency_list"]
    matrix = representation["adjacency_matrix"]
    list_distances, list_order, list_checks = _bfs_from_list(adjacency, start)
    matrix_distances, matrix_order, matrix_checks = _bfs_from_matrix(matrix, start)
    return {
        "contract_version": GRAPH_REPRESENTATIONS_CONTRACT_VERSION,
        "operation": "breadth_first_search",
        "source": start,
        "representation": representation,
        "adjacency_list_bfs": {"distances": list_distances, "dequeue_order": list_order, "neighbor_slot_checks": list_checks},
        "adjacency_matrix_bfs": {"distances": matrix_distances, "dequeue_order": matrix_order, "matrix_cell_checks": matrix_checks},
        "distances_agree": list_distances == matrix_distances,
        "reachable_vertex_count": sum(distance is not None for distance in list_distances),
    }


def graph_representation_bfs_certificate(vertex_count: object, edges: object, directed: object, source: object, report: object) -> bool:
    """Rebuild both BFS paths so altered scan counts or distances fail."""
    if not isinstance(report, dict):
        return False
    try:
        return report == graph_representation_bfs_report(vertex_count, edges, directed, source)
    except (TypeError, ValueError):
        return False
