"""Compare shortest-path algorithm preconditions on one small directed graph."""

from __future__ import annotations

from math import inf, isfinite

from projects.algorithm_lab.bellman_ford_trace import bellman_ford_trace, reconstruct_path as bellman_path
from projects.algorithm_lab.bfs_trace import bfs_trace_with_parents, reconstruct_path as bfs_path
from projects.algorithm_lab.dijkstra_trace import dijkstra_trace, reconstruct_path as dijkstra_path
from projects.algorithm_lab.floyd_warshall import floyd_warshall_with_paths, recover_floyd_warshall_path


Edge = tuple[int, int, float]


def _validate(vertex_count: int, edges: list[Edge], source: int, target: int) -> None:
    if not isinstance(vertex_count, int) or isinstance(vertex_count, bool) or vertex_count <= 0:
        raise ValueError("vertex_count must be a positive integer")
    if any(not isinstance(vertex, int) or isinstance(vertex, bool) or not 0 <= vertex < vertex_count for vertex in (source, target)):
        raise ValueError("source and target must be valid vertices")
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 3:
            raise ValueError("each edge must be a (source, target, weight) tuple")
        left, right, weight = edge
        if (not isinstance(left, int) or isinstance(left, bool) or not 0 <= left < vertex_count
                or not isinstance(right, int) or isinstance(right, bool) or not 0 <= right < vertex_count
                or not isinstance(weight, (int, float)) or isinstance(weight, bool) or not isfinite(weight)):
            raise ValueError("edges must have valid endpoints and finite weights")


def _graph(vertex_count: int, edges: list[Edge]) -> dict[int, list[tuple[int, float]]]:
    graph = {vertex: [] for vertex in range(vertex_count)}
    for left, right, weight in edges:
        graph[left].append((right, float(weight)))
    return graph


def _entry(status: str, reason: str, distance: float | None = None, path: list[int] | None = None, invariant: str = "") -> dict[str, object]:
    return {"status": status, "reason": reason, "distance": distance, "path": path, "invariant": invariant}


def shortest_path_comparison(
    vertex_count: int, edges: list[Edge], source: int, target: int
) -> dict[str, object]:
    """Return applicable/rejected results for BFS, Dijkstra, Bellman--Ford and Floyd--Warshall.

    The function does not silently run an algorithm outside its teaching
    precondition.  A rejected card is useful evidence: an answer from that
    algorithm would not have the promised shortest-path interpretation.
    """
    _validate(vertex_count, edges, source, target)
    edges = [(left, right, float(weight)) for left, right, weight in edges]
    all_unit = all(weight == 1.0 for _, _, weight in edges)
    all_nonnegative = all(weight >= 0.0 for _, _, weight in edges)
    report: dict[str, object] = {
        "properties": {
            "vertex_count": vertex_count,
            "edge_count": len(edges),
            "all_unit_weights": all_unit,
            "all_nonnegative_weights": all_nonnegative,
            "has_negative_edge": any(weight < 0.0 for _, _, weight in edges),
        },
        "source": source,
        "target": target,
        "algorithms": {},
    }
    algorithms: dict[str, dict[str, object]] = report["algorithms"]  # type: ignore[assignment]

    if all_unit:
        adjacency = {vertex: [target for target, _ in neighbors] for vertex, neighbors in _graph(vertex_count, edges).items()}
        distances, parents, events = bfs_trace_with_parents(adjacency, source)
        distance = distances.get(target)
        algorithms["bfs"] = _entry(
            "applicable", "所有边权均为 1，按边数最短等于按权重最短。", float(distance) if distance is not None else None,
            bfs_path(parents, target) if target in parents else None,
            "队列按非递减层数处理；首次发现即确定最少边数。",
        )
    else:
        algorithms["bfs"] = _entry("rejected", "BFS 只保证最少边数；存在非单位权边时不能承诺最小总权重。")

    if all_nonnegative:
        distances, parents, _ = dijkstra_trace(_graph(vertex_count, edges), source)
        algorithms["dijkstra"] = _entry(
            "applicable", "所有边权非负。", None if distances[target] == inf else distances[target],
            dijkstra_path(parents, target), "每次弹出的最小暂定距离在非负边下可最终确定。",
        )
    else:
        algorithms["dijkstra"] = _entry("rejected", "存在负边；已确定节点仍可能被未来路径改善。")

    try:
        distances, parents, _ = bellman_ford_trace(vertex_count, edges, source)
        algorithms["bellman_ford"] = _entry(
            "applicable", "允许负边，且从源点可达区域不存在负环。", None if distances[target] == inf else distances[target],
            bellman_path(parents, source, target), "第 k 轮标签对应至多 k 条边的最短路径。",
        )
    except ValueError as error:
        algorithms["bellman_ford"] = _entry("rejected", str(error))

    try:
        distances, next_hop = floyd_warshall_with_paths(vertex_count, edges)
        algorithms["floyd_warshall"] = _entry(
            "applicable", "没有负环；计算所有源点对的距离。", None if distances[source][target] == inf else distances[source][target],
            recover_floyd_warshall_path(next_hop, source, target), "第 k 层只允许前 k 个顶点作为中间点。",
        )
    except ValueError as error:
        algorithms["floyd_warshall"] = _entry("rejected", str(error))
    return report


def shortest_path_comparison_certificate(
    vertex_count: int, edges: list[Edge], source: int, target: int, report: dict[str, object]
) -> bool:
    """Rebuild the complete comparison, including rejected-precondition cards."""
    if not isinstance(report, dict):
        return False
    try:
        return report == shortest_path_comparison(vertex_count, edges, source, target)
    except (TypeError, ValueError):
        return False
