"""A deliberately narrow, auditable repair after one non-negative edge insertion."""

from __future__ import annotations

from collections import Counter
from heapq import heappop, heappush
from itertools import count
from math import inf

from projects.algorithm_lab.dijkstra_trace import dijkstra_trace, reconstruct_path
from projects.algorithm_lab.shortest_path_comparison import CONTRACT_VERSION, normalize_shortest_path_input


INCREMENTAL_SHORTEST_PATH_CONTRACT_VERSION = "incremental-shortest-path/v1"


def _edges(payload: dict[str, object]) -> list[tuple[int, int, float]]:
    return [tuple(edge) for edge in payload["edges"]]  # type: ignore[return-value]


def _graph(vertex_count: int, edges: list[tuple[int, int, float]]) -> dict[int, list[tuple[int, float]]]:
    graph = {vertex: [] for vertex in range(vertex_count)}
    for left, right, weight in edges:
        graph[left].append((right, weight))
    return graph


def _json_distances(distances: dict[int, float]) -> list[float | None]:
    return [None if distances[vertex] == inf else distances[vertex] for vertex in range(len(distances))]


def _one_inserted_edge(before: list[tuple[int, int, float]], after: list[tuple[int, int, float]]) -> tuple[int, int, float]:
    before_counter, after_counter = Counter(before), Counter(after)
    removed, added = before_counter - after_counter, after_counter - before_counter
    if removed or sum(added.values()) != 1:
        raise ValueError("incremental repair requires exactly one inserted edge and no removed or changed edge")
    return next(added.elements())


def _repair_after_insertion(
    vertex_count: int,
    before_edges: list[tuple[int, int, float]],
    inserted: tuple[int, int, float],
    source: int,
) -> tuple[dict[int, float], dict[int, int | None], dict[str, object]]:
    """Seed Dijkstra only if the new edge lowers its destination label."""
    distances, parents, _ = dijkstra_trace(_graph(vertex_count, before_edges), source)
    left, right, weight = inserted
    candidate = distances[left] + weight
    if candidate >= distances[right]:
        return distances, parents, {
            "seed_improved": False,
            "edge_scans": 0,
            "successful_relaxations": 0,
            "settled_vertices": [],
        }
    graph = _graph(vertex_count, before_edges + [inserted])
    distances[right], parents[right] = candidate, left
    sequence = count()
    heap = [(candidate, next(sequence), right)]
    edge_scans, successful_relaxations, settled_vertices = 0, 1, []
    while heap:
        distance, _, vertex = heappop(heap)
        if distance != distances[vertex]:
            continue
        settled_vertices.append(vertex)
        for neighbor, neighbor_weight in graph[vertex]:
            edge_scans += 1
            next_distance = distance + neighbor_weight
            if next_distance < distances[neighbor]:
                distances[neighbor], parents[neighbor] = next_distance, vertex
                successful_relaxations += 1
                heappush(heap, (next_distance, next(sequence), neighbor))
    return distances, parents, {
        "seed_improved": True,
        "edge_scans": edge_scans,
        "successful_relaxations": successful_relaxations,
        "settled_vertices": settled_vertices,
    }


def incremental_shortest_path_report(before_payload: object, after_payload: object) -> dict[str, object]:
    """Repair one insertion and prove its labels equal a full Dijkstra rerun.

    The contract intentionally rejects deletions, weight changes, negative
    edges, and changes to the query scope.  Those updates need different
    invariants; treating them as an insertion would produce a plausible but
    unjustified answer.
    """
    before, after = normalize_shortest_path_input(before_payload), normalize_shortest_path_input(after_payload)
    if any(before[key] != after[key] for key in ("vertex_count", "source", "target")):
        raise ValueError("incremental repair must keep vertex_count, source and target fixed")
    before_edges, after_edges = _edges(before), _edges(after)
    if any(weight < 0.0 for _, _, weight in before_edges + after_edges):
        raise ValueError("incremental Dijkstra repair requires non-negative weights")
    inserted = _one_inserted_edge(before_edges, after_edges)
    vertex_count, source, target = before["vertex_count"], before["source"], before["target"]
    repaired_distances, repaired_parents, work = _repair_after_insertion(
        vertex_count, before_edges, inserted, source  # type: ignore[arg-type]
    )
    full_distances, full_parents, _ = dijkstra_trace(_graph(vertex_count, after_edges), source)  # type: ignore[arg-type]
    distance_match = repaired_distances == full_distances
    target_match = repaired_distances[target] == full_distances[target]  # type: ignore[index]
    return {
        "contract_version": INCREMENTAL_SHORTEST_PATH_CONTRACT_VERSION,
        "input_contract_version": CONTRACT_VERSION,
        "before": before,
        "after": after,
        "inserted_edge": list(inserted),
        "policy": {"update_kind": "one_nonnegative_edge_insertion", "automatic_action": "none"},
        "repair": {
            **work,
            "distances": _json_distances(repaired_distances),
            "target_distance": None if repaired_distances[target] == inf else repaired_distances[target],  # type: ignore[index]
            "target_path": reconstruct_path(repaired_parents, target),  # type: ignore[arg-type]
        },
        "full_recomputation": {
            "distances": _json_distances(full_distances),
            "target_distance": None if full_distances[target] == inf else full_distances[target],  # type: ignore[index]
            "target_path": reconstruct_path(full_parents, target),  # type: ignore[arg-type]
        },
        "verification": {"all_distances_match_full_recomputation": distance_match, "target_distance_matches": target_match},
        "interpretation": "repair_matches_full_recomputation" if distance_match else "repair_mismatch_requires_review",
    }


def incremental_shortest_path_certificate(before_payload: object, after_payload: object, report: object) -> bool:
    """Replay the restricted update and reject changed work or distances."""
    if not isinstance(report, dict):
        return False
    try:
        return report == incremental_shortest_path_report(before_payload, after_payload)
    except (TypeError, ValueError):
        return False
