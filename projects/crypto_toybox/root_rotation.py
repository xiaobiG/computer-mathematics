"""Auditable fictional trust-root rotation metadata; never a key-management system."""

from __future__ import annotations


CONTRACT = "trust-root-rotation-audit/v1"


def _nonnegative_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} 必须是非负整数")
    return value


def _root_ids(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} 必须是非空列表")
    if any(not isinstance(root, str) or not root.strip() for root in value):
        raise ValueError(f"{name} 中的根标识必须是非空字符串")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} 中的根标识不能重复")
    return list(value)


def _threshold(value: object, root_ids: list[str], name: str) -> int:
    value = _nonnegative_int(value, name)
    if not 1 <= value <= len(root_ids):
        raise ValueError(f"{name} 必须在 1 到根数量之间")
    return value


def _state(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"epoch", "root_ids", "threshold"}:
        raise ValueError("trust_state 字段必须是 epoch、root_ids、threshold")
    roots = _root_ids(value["root_ids"], "root_ids")
    return {
        "epoch": _nonnegative_int(value["epoch"], "epoch"),
        "root_ids": roots,
        "threshold": _threshold(value["threshold"], roots, "threshold"),
    }


def _proposal(value: object) -> dict[str, object]:
    required = {"new_epoch", "new_root_ids", "new_threshold", "approval_claims", "witness_evidence_available"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("proposal 字段必须与 trust-root-rotation-audit/v1 完全一致")
    roots = _root_ids(value["new_root_ids"], "new_root_ids")
    evidence = value["witness_evidence_available"]
    if not isinstance(evidence, bool):
        raise ValueError("witness_evidence_available 必须是布尔值")
    return {
        "new_epoch": _nonnegative_int(value["new_epoch"], "new_epoch"),
        "new_root_ids": roots,
        "new_threshold": _threshold(value["new_threshold"], roots, "new_threshold"),
        # These are deliberately claims supplied by an external mature verifier,
        # not signatures produced or verified by this teaching module.
        "approval_claims": _root_ids(value["approval_claims"], "approval_claims"),
        "witness_evidence_available": evidence,
    }


def trust_root_rotation_report(trust_state: object, proposal: object) -> dict[str, object]:
    """Audit a fictional threshold-authorized root-set transition.

    The result models policy only.  It never changes a trust store and never
    establishes that an approval claim is a cryptographic signature.
    """
    old = _state(trust_state)
    proposed = _proposal(proposal)
    old_roots = set(old["root_ids"])
    approvals = proposed["approval_claims"]
    checks = {
        "epoch_advances": proposed["new_epoch"] > old["epoch"],
        "root_set_changes": set(proposed["new_root_ids"]) != old_roots,
        "approval_claims_belong_to_current_roots": set(approvals).issubset(old_roots),
        "current_threshold_claimed": len(approvals) >= old["threshold"],
        "witness_evidence_available": proposed["witness_evidence_available"],
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    if not checks["witness_evidence_available"]:
        decision = "manual_review"
    elif all(checks.values()):
        decision = "accept_for_policy_only"
    else:
        decision = "reject"
    return {
        "contract": CONTRACT,
        "trust_state": old,
        "proposal": proposed,
        "checks": checks,
        "failed_checks": failed_checks,
        "decision": decision,
        "automatic_apply": False,
        "cryptographic_verification": "not_performed",
    }


def trust_root_rotation_certificate(report: object) -> dict[str, bool]:
    """Replay every policy field and preserve the non-operational boundary."""
    empty = {
        "contract_matches": False,
        "report_replays": False,
        "safety_boundary_preserved": False,
        "valid": False,
    }
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return empty
    try:
        rebuilt = trust_root_rotation_report(report["trust_state"], report["proposal"])
    except (KeyError, ValueError):
        return empty
    report_replays = all(report.get(field) == rebuilt[field] for field in ("checks", "failed_checks", "decision"))
    safety_boundary_preserved = (
        report.get("automatic_apply") is False
        and report.get("cryptographic_verification") == "not_performed"
    )
    valid = report_replays and safety_boundary_preserved
    return {
        "contract_matches": True,
        "report_replays": report_replays,
        "safety_boundary_preserved": safety_boundary_preserved,
        "valid": valid,
    }
