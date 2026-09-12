"""Replayable adjacency-list / adjacency-matrix reports for small finite graphs."""

from __future__ import annotations

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
