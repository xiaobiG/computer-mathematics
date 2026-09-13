"""课堂 Merkle 日志：证明成员与追加前缀，不是透明度服务。"""
from __future__ import annotations

import hashlib


CONTRACT = "append-only-merkle-log/v1"
CHECKPOINT_CONTRACT = "append-only-merkle-log-checkpoint/v1"
SPLIT_VIEW_CONTRACT = "append-only-merkle-log-split-view/v1"


def _digest(tag: bytes, payload: bytes) -> str:
    return hashlib.sha256(tag + payload).hexdigest()


def _leaf(entry: str) -> str:
    if not isinstance(entry, str) or not entry:
        raise ValueError("日志条目必须是非空字符串")
    return _digest(b"leaf:\x00", entry.encode("utf-8"))


def _parent(left: str, right: str) -> str:
    return _digest(b"node:\x00", bytes.fromhex(left) + bytes.fromhex(right))


def _levels(entries: object) -> list[list[str]]:
    if not isinstance(entries, list) or not entries:
        raise ValueError("日志必须是非空字符串列表")
    levels = [[_leaf(entry) for entry in entries]]
    while len(levels[-1]) > 1:
        current = levels[-1]
        paired = current if len(current) % 2 == 0 else current + [current[-1]]
        levels.append([_parent(paired[index], paired[index + 1]) for index in range(0, len(paired), 2)])
    return levels


def merkle_root(entries: object) -> str:
    return _levels(entries)[-1][0]


def inclusion_proof(entries: object, index: int) -> dict[str, object]:
    if not isinstance(index, int) or isinstance(index, bool):
        raise ValueError("index 必须是整数")
    levels = _levels(entries)
    if not 0 <= index < len(levels[0]):
        raise ValueError("index 超出日志范围")
    position, siblings = index, []
    for current in levels[:-1]:
        paired = current if len(current) % 2 == 0 else current + [current[-1]]
        sibling_position = position + 1 if position % 2 == 0 else position - 1
        siblings.append({"hash": paired[sibling_position], "on_left": position % 2 == 1})
        position //= 2
    return {"contract": CONTRACT, "entry": entries[index], "index": index, "size": len(entries), "root": levels[-1][0], "siblings": siblings}


def inclusion_certificate(proof: object) -> bool:
    if not isinstance(proof, dict) or proof.get("contract") != CONTRACT:
        return False
    try:
        entry, index, size = proof["entry"], proof["index"], proof["size"]
        if not isinstance(index, int) or isinstance(index, bool) or not isinstance(size, int) or not 0 <= index < size:
            return False
        value = _leaf(entry)
        for sibling in proof["siblings"]:
            if not isinstance(sibling, dict) or set(sibling) != {"hash", "on_left"} or not isinstance(sibling["on_left"], bool):
                return False
            value = _parent(sibling["hash"], value) if sibling["on_left"] else _parent(value, sibling["hash"])
        return value == proof["root"]
    except (KeyError, TypeError, ValueError):
        return False


def append_only_report(old_entries: object, new_entries: object) -> dict[str, object]:
    old_levels, new_levels = _levels(old_entries), _levels(new_entries)
    prefix_preserved = new_entries[:len(old_entries)] == old_entries
    return {
        "contract": CONTRACT,
        "old_size": len(old_entries), "new_size": len(new_entries),
        "old_root": old_levels[-1][0], "new_root": new_levels[-1][0],
        "old_entries": list(old_entries), "new_entries": list(new_entries),
        "prefix_preserved": prefix_preserved,
        "decision": "append_only" if len(new_entries) >= len(old_entries) and prefix_preserved else "not_append_only",
        "trust_anchor_update_verified": False,
    }


def append_only_certificate(report: object) -> bool:
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        rebuilt = append_only_report(report["old_entries"], report["new_entries"])
        return all(report.get(key) == rebuilt[key] for key in rebuilt) and report["trust_anchor_update_verified"] is False
    except (KeyError, ValueError):
        return False


def _operator_id(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("日志运营者标识必须是非空字符串")
    return value


def checkpoint_from_entries(operator_id: object, entries: object) -> dict[str, object]:
    """Create a replayable teaching checkpoint from a complete small log.

    Real clients normally receive a signed checkpoint without all entries.
    Keeping entries here deliberately trades compactness for a locally
    checkable classroom artifact; it does not authenticate the operator ID.
    """
    operator = _operator_id(operator_id)
    normalized_entries = list(entries) if isinstance(entries, list) else entries
    return {
        "contract": CHECKPOINT_CONTRACT,
        "operator_id": operator,
        "tree_size": len(_levels(normalized_entries)[0]),
        "root": merkle_root(normalized_entries),
        "entries": normalized_entries,
        "checkpoint_authentication": "not_verified",
    }


def checkpoint_certificate(checkpoint: object) -> bool:
    if not isinstance(checkpoint, dict) or checkpoint.get("contract") != CHECKPOINT_CONTRACT:
        return False
    try:
        rebuilt = checkpoint_from_entries(checkpoint["operator_id"], checkpoint["entries"])
        return checkpoint == rebuilt
    except (KeyError, TypeError, ValueError):
        return False


def split_view_report(first: object, second: object) -> dict[str, object]:
    """Compare two replayable checkpoints without claiming operator identity.

    Equal tree sizes and unequal roots are incompatible *if* both checkpoints
    are authenticated as statements by the same log.  Different sizes alone
    are not evidence of a fork: an append-only extension naturally changes
    both size and root, and needs a consistency proof (or this lesson's full
    prefix replay) for comparison.
    """
    if not checkpoint_certificate(first) or not checkpoint_certificate(second):
        raise ValueError("两个检查点都必须是可重放的教学检查点")
    same_operator_claim = first["operator_id"] == second["operator_id"]
    same_tree_size = first["tree_size"] == second["tree_size"]
    same_root = first["root"] == second["root"]
    candidate_equivocation = same_operator_claim and same_tree_size and not same_root
    if candidate_equivocation:
        decision = "candidate_equivocation_requires_authenticated_checkpoints"
    elif same_operator_claim and not same_tree_size:
        decision = "inconclusive_requires_append_only_consistency_evidence"
    elif not same_operator_claim:
        decision = "inconclusive_different_operator_claims"
    else:
        decision = "no_root_conflict_observed"
    return {
        "contract": SPLIT_VIEW_CONTRACT,
        "first": first,
        "second": second,
        "same_operator_claim": same_operator_claim,
        "same_tree_size": same_tree_size,
        "same_root": same_root,
        "candidate_equivocation": candidate_equivocation,
        "decision": decision,
        "checkpoint_authentication": "not_verified",
        "automatic_response": "none",
    }


def split_view_certificate(first: object, second: object, report: object) -> bool:
    if not isinstance(report, dict):
        return False
    try:
        return report == split_view_report(first, second)
    except ValueError:
        return False
