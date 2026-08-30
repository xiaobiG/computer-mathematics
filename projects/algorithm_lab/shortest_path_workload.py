"""Reproducible work counters for repeated shortest-path queries on a small graph.

This module deliberately reports deterministic operations rather than elapsed
milliseconds.  Wall-clock timings depend on the interpreter, CPU, and other
processes; edge scans and dynamic-programming candidate cells can be replayed
from exactly the same input contract.
"""

from __future__ import annotations

from math import ceil, log2

from projects.algorithm_lab.bellman_ford_trace import bellman_ford_trace
from projects.algorithm_lab.bfs_trace import bfs_trace_with_parents
from projects.algorithm_lab.dijkstra_trace import dijkstra_trace
from projects.algorithm_lab.floyd_warshall import floyd_warshall
from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    normalize_shortest_path_input,
)


WORKLOAD_CONTRACT_VERSION = "shortest-path-workload/v1"


def _query_sources(vertex_count: int, query_count: int) -> list[int]:
    if not isinstance(query_count, int) or isinstance(query_count, bool) or not 1 <= query_count <= vertex_count:
        raise ValueError("query_count must be an integer from 1 to vertex_count")
    return list(range(query_count))


def _graph(vertex_count: int, edges: list[tuple[int, int, float]]) -> dict[int, list[tuple[int, float]]]:
    graph = {vertex: [] for vertex in range(vertex_count)}
    for left, right, weight in edges:
        graph[left].append((right, weight))
    return graph


def _entry(status: str, theory: str, **work: int | str) -> dict[str, object]:
    return {"status": status, "theory": theory, "work": work}


def shortest_path_workload_report(payload: object, query_count: int) -> dict[str, object]:
    """Compare deterministic work for the first ``query_count`` source vertices.

    A query here means one full single-source run, not merely an early-stopped
    source-target search.  This keeps all four cards comparable: Floyd--
    Warshall pays once for all source pairs, while the other algorithms repeat
    for each selected source.
    """
    normalized = normalize_shortest_path_input(payload)
    vertex_count = normalized["vertex_count"]
    edges = [tuple(edge) for edge in normalized["edges"]]
    sources = _query_sources(vertex_count, query_count)  # type: ignore[arg-type]
    graph = _graph(vertex_count, edges)  # type: ignore[arg-type]
    edge_count = len(edges)
    all_unit = all(weight == 1.0 for _, _, weight in edges)
    all_nonnegative = all(weight >= 0.0 for _, _, weight in edges)
    logarithm = ceil(log2(max(2, vertex_count)))
    algorithms: dict[str, dict[str, object]] = {}

    if all_unit:
        settled = edge_scans = 0
        for source in sources:
            _, _, events = bfs_trace_with_parents(
                {vertex: [target for target, _ in neighbors] for vertex, neighbors in graph.items()}, source
            )
            settled += len(events)
            edge_scans += sum(len(graph[event.node]) for event in events)
        algorithms["bfs"] = _entry(
            "applicable", "Q·O(V+E)", runs=query_count, settled_vertices=settled, edge_scans=edge_scans,
        )
    else:
        algorithms["bfs"] = _entry("rejected", "Q·O(V+E)", reason="non_unit_weights")

    if all_nonnegative:
        settled = edge_scans = successful_relaxations = 0
        for source in sources:
            _, _, events = dijkstra_trace(graph, source)
            settled += len(events)
            edge_scans += sum(len(graph[event.node]) for event in events)
            successful_relaxations += sum(len(event.relaxed) for event in events)
        algorithms["dijkstra"] = _entry(
            "applicable", "Q·O((V+E)·log V)", runs=query_count, settled_vertices=settled,
            edge_scans=edge_scans, successful_relaxations=successful_relaxations,
            heap_log_factor=logarithm,
        )
    else:
        algorithms["dijkstra"] = _entry("rejected", "Q·O((V+E)·log V)", reason="negative_edge")

    rounds = edge_scans = successful_relaxations = 0
    negative_cycle_sources: list[int] = []
    for source in sources:
        try:
            _, _, events = bellman_ford_trace(vertex_count, edges, source)  # type: ignore[arg-type]
            rounds += len(events)
            edge_scans += len(events) * edge_count
            successful_relaxations += sum(len(event.relaxed) for event in events)
        except ValueError:
            negative_cycle_sources.append(source)
    if negative_cycle_sources:
        algorithms["bellman_ford"] = _entry(
            "rejected", "Q·O(VE)", reason="reachable_negative_cycle",
            rejected_sources=",".join(map(str, negative_cycle_sources)),
        )
    else:
        algorithms["bellman_ford"] = _entry(
            "applicable", "Q·O(VE)", runs=query_count, rounds=rounds, edge_scans=edge_scans,
            successful_relaxations=successful_relaxations,
        )

    # Floyd--Warshall considers each (source, middle, target) candidate exactly once.
    try:
        floyd_warshall(vertex_count, edges)  # type: ignore[arg-type]
        algorithms["floyd_warshall"] = _entry(
            "applicable", "O(V³), independent of Q after preprocessing", runs=1,
            candidate_cells=vertex_count ** 3, requested_sources=query_count,
        )
    except ValueError:
        algorithms["floyd_warshall"] = _entry(
            "rejected", "O(V³), independent of Q after preprocessing", reason="negative_cycle",
            candidate_cells=vertex_count ** 3, requested_sources=query_count,
        )
    return {
        "contract_version": WORKLOAD_CONTRACT_VERSION,
        "input_contract_version": CONTRACT_VERSION,
        "input": normalized,
        "query_sources": sources,
        "algorithms": algorithms,
    }


def shortest_path_workload_certificate(payload: object, query_count: int, report: object) -> bool:
    """Rebuild a workload report so changed counts, sources, or rejection cards fail."""
    if not isinstance(report, dict):
        return False
    try:
        return report == shortest_path_workload_report(payload, query_count)
    except (TypeError, ValueError):
        return False
