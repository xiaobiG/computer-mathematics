"""Auditable single-edge deletion reports for a small non-negative graph."""

from __future__ import annotations

from collections import Counter
from math import isfinite

from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    normalize_shortest_path_input,
    shortest_path_replay_report,
)


DELETION_SHORTEST_PATH_CONTRACT_VERSION = "deletion-shortest-path/v1"


def _edges(payload: dict[str, object]) -> list[tuple[int, int, float]]:
    return [tuple(edge) for edge in payload["edges"]]  # type: ignore[return-value,arg-type]


def _one_deleted_edge(before: list[tuple[int, int, float]], after: list[tuple[int, int, float]]) -> tuple[int, int, float]:
    before_counter, after_counter = Counter(before), Counter(after)
    removed, added = before_counter - after_counter, after_counter - before_counter
    if added or sum(removed.values()) != 1:
        raise ValueError("deletion audit requires exactly one removed edge and no inserted or changed edge")
    return next(removed.elements())


def _dijkstra_card(replay: dict[str, object]) -> dict[str, object]:
    card = replay["comparison"]["algorithms"]["dijkstra"]  # type: ignore[index]
    if card["status"] != "applicable":
        raise ValueError("deletion audit requires non-negative weights")
    return card


def _path_uses_endpoint(path: object, edge: tuple[int, int, float]) -> bool:
    if not isinstance(path, list):
        return False
    return any(path[index] == edge[0] and path[index + 1] == edge[1] for index in range(len(path) - 1))


def deletion_shortest_path_report(before_payload: object, after_payload: object) -> dict[str, object]:
    """Audit the effects of deleting one edge by independently rerunning Dijkstra.

    This is intentionally *not* a dynamic deletion algorithm.  A deletion can
    invalidate a parent chain and increase a label, so the report uses a full
    rerun as its oracle and makes that cost/semantic boundary explicit.
    """
    before, after = normalize_shortest_path_input(before_payload), normalize_shortest_path_input(after_payload)
    if any(before[key] != after[key] for key in ("vertex_count", "source", "target")):
        raise ValueError("deletion audit must keep vertex_count, source and target fixed")
    before_edges, after_edges = _edges(before), _edges(after)
    if any(weight < 0.0 or not isfinite(weight) for _, _, weight in before_edges + after_edges):
        raise ValueError("deletion audit requires non-negative finite weights")
    deleted = _one_deleted_edge(before_edges, after_edges)
    before_replay, after_replay = shortest_path_replay_report(before), shortest_path_replay_report(after)
    before_card, after_card = _dijkstra_card(before_replay), _dijkstra_card(after_replay)
    old_distance, new_distance = before_card["distance"], after_card["distance"]
    target_worsened = (
        old_distance is not None and (new_distance is None or float(new_distance) > float(old_distance))
    )
    return {
        "contract_version": DELETION_SHORTEST_PATH_CONTRACT_VERSION,
        "input_contract_version": CONTRACT_VERSION,
        "deleted_edge": list(deleted),
        "before": {"distances": before_card["distance"], "target_path": before_card["path"], "replay": before_replay},
        "after": {"distances": after_card["distance"], "target_path": after_card["path"], "replay": after_replay},
        "audit": {
            "deleted_endpoint_pair_is_in_recorded_old_target_path": _path_uses_endpoint(before_card["path"], deleted),
            "target_distance_worsened_or_became_unreachable": target_worsened,
            "full_recomputation_required_by_this_contract": True,
            "reason": "deletion_can_invalidate_parent_chain_and_only_raise_labels",
        },
    }


def deletion_shortest_path_certificate(before_payload: object, after_payload: object, report: object) -> bool:
    """Replay the restricted deletion audit and reject changed paths or claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == deletion_shortest_path_report(before_payload, after_payload)
    except (TypeError, ValueError):
        return False
