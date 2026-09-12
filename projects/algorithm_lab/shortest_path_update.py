"""Auditable invalidation and replay for a changed shortest-path graph."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json

from projects.algorithm_lab.shortest_path_comparison import (
    CONTRACT_VERSION,
    normalize_shortest_path_input,
    shortest_path_replay_report,
)


UPDATE_CONTRACT_VERSION = "shortest-path-update/v1"


def _fingerprint(normalized: dict[str, object]) -> str:
    """Hash canonical input JSON; evidence is tied to this exact graph snapshot."""
    encoded = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def _edge_multiset(normalized: dict[str, object]) -> Counter[tuple[int, int, float]]:
    return Counter(tuple(edge) for edge in normalized["edges"])  # type: ignore[arg-type]


def _expand(counter: Counter[tuple[int, int, float]]) -> list[list[int | float]]:
    return [list(edge) for edge, count in sorted(counter.items()) for _ in range(count)]


def _algorithm_delta(before: dict[str, object], after: dict[str, object]) -> dict[str, dict[str, object]]:
    before_cards = before["comparison"]["algorithms"]  # type: ignore[index]
    after_cards = after["comparison"]["algorithms"]  # type: ignore[index]
    changes: dict[str, dict[str, object]] = {}
    for name in before_cards:
        old = before_cards[name]
        new = after_cards[name]
        fields = [field for field in ("status", "distance", "path", "reason") if old.get(field) != new.get(field)]
        if fields:
            changes[name] = {"changed_fields": fields, "before": old, "after": new}
    return changes


def shortest_path_update_report(before_payload: object, after_payload: object) -> dict[str, object]:
    """Compare two graph snapshots and invalidate every input-bound old report on change.

    The source, target and vertex set are intentionally held fixed.  Otherwise
    the request itself changes and a path comparison would silently mix two
    different questions.  Parallel edges are treated as a multiset, so adding
    or removing one duplicate is still visible in the update evidence.
    """
    before = normalize_shortest_path_input(before_payload)
    after = normalize_shortest_path_input(after_payload)
    if any(before[key] != after[key] for key in ("vertex_count", "source", "target")):
        raise ValueError("updates must keep vertex_count, source and target fixed")
    before_fingerprint = _fingerprint(before)
    after_fingerprint = _fingerprint(after)
    before_edges = _edge_multiset(before)
    after_edges = _edge_multiset(after)
    removed = before_edges - after_edges
    added = after_edges - before_edges
    changed = before_fingerprint != after_fingerprint
    before_replay = shortest_path_replay_report(before)
    after_replay = shortest_path_replay_report(after)
    return {
        "contract_version": UPDATE_CONTRACT_VERSION,
        "input_contract_version": CONTRACT_VERSION,
        "before": {"fingerprint": before_fingerprint, "input": before},
        "after": {"fingerprint": after_fingerprint, "input": after},
        "delta": {"added_edges": _expand(added), "removed_edges": _expand(removed), "graph_changed": changed},
        "invalidation": {
            "old_comparison_report_valid_for_after": not changed,
            "old_workload_report_valid_for_after": not changed,
            "old_query_boundary_report_valid_for_after": not changed,
            "reason": "same_canonical_input" if not changed else "input_fingerprint_changed",
        },
        "algorithm_outcome_changes": _algorithm_delta(before_replay, after_replay),
    }


def shortest_path_update_certificate(before_payload: object, after_payload: object, report: object) -> bool:
    """Rebuild a graph-update report so changed deltas or validity claims fail."""
    if not isinstance(report, dict):
        return False
    try:
        return report == shortest_path_update_report(before_payload, after_payload)
    except (TypeError, ValueError):
        return False
