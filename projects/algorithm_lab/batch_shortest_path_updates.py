"""Replayable ordered updates with stable edge identities for teaching graphs."""

from __future__ import annotations

from math import isfinite

from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    MAX_EDGES,
    MAX_VERTICES,
    normalize_shortest_path_input,
    shortest_path_replay_report,
)


CONTRACT = "ordered-shortest-path-updates/v1"
MAX_UPDATES = 6


def _integer(value: object, name: str, upper: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < upper:
        raise ValueError(f"{name} must be a valid vertex")
    return value


def _edge(raw: object, vertex_count: int) -> list[object]:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValueError("each edge must be [edge_id, source, target, weight]")
    edge_id, left, right, weight = raw
    if not isinstance(edge_id, str) or not edge_id.strip():
        raise ValueError("edge_id must be a non-empty string")
    _integer(left, "edge source", vertex_count)
    _integer(right, "edge target", vertex_count)
    if (not isinstance(weight, (int, float)) or isinstance(weight, bool)
            or not isfinite(weight) or float(weight) < 0):
        raise ValueError("edge weight must be finite and non-negative")
    return [edge_id, left, right, float(weight)]


def _state(payload: object) -> dict[str, object]:
    required = {"vertex_count", "edges", "source", "target"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError("state must contain exactly vertex_count, edges, source, target")
    count = payload["vertex_count"]
    if not isinstance(count, int) or isinstance(count, bool) or not 2 <= count <= MAX_VERTICES:
        raise ValueError(f"vertex_count must be an integer from 2 to {MAX_VERTICES}")
    source, target = _integer(payload["source"], "source", count), _integer(payload["target"], "target", count)
    if not isinstance(payload["edges"], list) or len(payload["edges"]) > MAX_EDGES:
        raise ValueError(f"edges must contain at most {MAX_EDGES} entries")
    edges = [_edge(edge, count) for edge in payload["edges"]]
    if len({edge[0] for edge in edges}) != len(edges):
        raise ValueError("edge_id values must be unique")
    return {"vertex_count": count, "edges": edges, "source": source, "target": target}


def _operation(raw: object, vertex_count: int) -> dict[str, object]:
    if not isinstance(raw, dict) or not isinstance(raw.get("kind"), str):
        raise ValueError("each update must be an object with a kind")
    kind = raw["kind"]
    if kind == "insert" and set(raw) == {"kind", "edge"}:
        return {"kind": kind, "edge": _edge(raw["edge"], vertex_count)}
    if kind == "delete" and set(raw) == {"kind", "edge_id"} and isinstance(raw["edge_id"], str) and raw["edge_id"].strip():
        return {"kind": kind, "edge_id": raw["edge_id"]}
    if kind == "set_weight" and set(raw) == {"kind", "edge_id", "weight"} and isinstance(raw["edge_id"], str) and raw["edge_id"].strip():
        weight = raw["weight"]
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or not isfinite(weight) or float(weight) < 0:
            raise ValueError("set_weight requires a finite non-negative weight")
        return {"kind": kind, "edge_id": raw["edge_id"], "weight": float(weight)}
    raise ValueError("update must be insert(edge), delete(edge_id), or set_weight(edge_id, weight)")


def _apply(state: dict[str, object], operation: dict[str, object]) -> dict[str, object]:
    edges = [list(edge) for edge in state["edges"]]  # type: ignore[arg-type]
    ids = {edge[0] for edge in edges}
    if operation["kind"] == "insert":
        edge = operation["edge"]  # type: ignore[assignment]
        if edge[0] in ids or len(edges) >= MAX_EDGES:  # type: ignore[index]
            raise ValueError("inserted edge_id must be new and remain within the edge limit")
        edges.append(edge)  # type: ignore[arg-type]
    else:
        edge_id = operation["edge_id"]
        matches = [index for index, edge in enumerate(edges) if edge[0] == edge_id]
        if len(matches) != 1:
            raise ValueError("update references an edge_id not present in the current snapshot")
        index = matches[0]
        if operation["kind"] == "delete":
            edges.pop(index)
        else:
            edges[index][3] = operation["weight"]
    return {"vertex_count": state["vertex_count"], "edges": edges, "source": state["source"], "target": state["target"]}


def _replay(state: dict[str, object]) -> dict[str, object]:
    ordinary = {
        "contract_version": CONTRACT_VERSION,
        "vertex_count": state["vertex_count"],
        "edges": [[edge[1], edge[2], edge[3]] for edge in state["edges"]],
        "source": state["source"], "target": state["target"],
    }
    normalized = normalize_shortest_path_input(ordinary)
    replay = shortest_path_replay_report(normalized)
    card = replay["comparison"]["algorithms"]["dijkstra"]  # type: ignore[index]
    return {"state": state, "dijkstra": {"target_distance": card["distance"], "target_path": card["path"]}, "replay": replay}


def ordered_shortest_path_updates_report(initial_state: object, updates: object) -> dict[str, object]:
    """Apply a tiny ordered batch and use full reruns as the correctness oracle."""
    state = _state(initial_state)
    if not isinstance(updates, list) or not 1 <= len(updates) <= MAX_UPDATES:
        raise ValueError(f"updates must contain from 1 to {MAX_UPDATES} operations")
    operations = [_operation(update, state["vertex_count"]) for update in updates]  # type: ignore[arg-type]
    steps = [{"sequence_index": 0, "operation": None, **_replay(state)}]
    for index, operation in enumerate(operations, start=1):
        state = _apply(state, operation)
        steps.append({"sequence_index": index, "operation": operation, **_replay(state)})
    return {
        "contract": CONTRACT,
        "input_contract_version": CONTRACT_VERSION,
        "steps": steps,
        "policy": {
            "stable_edge_identity": True,
            "ordered_updates": True,
            "full_recomputation_after_each_update": True,
            "automatic_action": "none",
        },
        "interpretation": "ordered_snapshots_replayed_with_full_dijkstra_oracle",
    }


def ordered_shortest_path_updates_certificate(initial_state: object, updates: object, report: object) -> bool:
    """Rebuild all ordered snapshots and reject changed IDs, order, or outcomes."""
    if not isinstance(report, dict):
        return False
    try:
        return report == ordered_shortest_path_updates_report(initial_state, updates)
    except (TypeError, ValueError):
        return False
