"""Auditable fictional trust-root rotation metadata; never a key-management system."""

from __future__ import annotations

from projects.crypto_toybox.transparency_log import append_only_certificate


CONTRACT = "trust-root-rotation-audit/v2"
RECOVERY_COMPATIBILITY_CONTRACT = "root-rotation-recovery-compatibility/v1"


def _nonnegative_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} 必须是非负整数")
    return value


def _nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} 必须是非空字符串")
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


def _operator_ids(value: object, root_ids: list[str]) -> list[str]:
    if (not isinstance(value, list) or len(value) != len(root_ids)
            or any(not isinstance(operator, str) or not operator.strip() for operator in value)):
        raise ValueError("root_operator_ids 必须与 root_ids 等长且包含非空字符串")
    return list(value)


def _state(value: object) -> dict[str, object]:
    required = {"epoch", "root_ids", "threshold", "root_operator_ids", "minimum_distinct_approval_operators"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("trust_state 字段必须包含纪元、根、阈值、根运营者与独立运营者门槛")
    roots = _root_ids(value["root_ids"], "root_ids")
    threshold = _threshold(value["threshold"], roots, "threshold")
    operator_ids = _operator_ids(value["root_operator_ids"], roots)
    independent_threshold = _nonnegative_int(
        value["minimum_distinct_approval_operators"], "minimum_distinct_approval_operators",
    )
    if not 1 <= independent_threshold <= threshold:
        raise ValueError("minimum_distinct_approval_operators 必须在 1 到 threshold 之间")
    return {
        "epoch": _nonnegative_int(value["epoch"], "epoch"),
        "root_ids": roots,
        "threshold": threshold,
        "root_operator_ids": operator_ids,
        "minimum_distinct_approval_operators": independent_threshold,
    }


def _proposal(value: object) -> dict[str, object]:
    required = {"new_epoch", "new_root_ids", "new_threshold", "approval_claims", "witness_evidence_available"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("proposal 字段必须与 trust-root-rotation-audit/v2 完全一致")
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
    operator_for_root = dict(zip(old["root_ids"], old["root_operator_ids"]))
    approval_operators = sorted({operator_for_root[root] for root in approvals if root in operator_for_root})
    checks = {
        "epoch_advances": proposed["new_epoch"] > old["epoch"],
        "root_set_changes": set(proposed["new_root_ids"]) != old_roots,
        "approval_claims_belong_to_current_roots": set(approvals).issubset(old_roots),
        "current_threshold_claimed": len(approvals) >= old["threshold"],
        "approval_claims_meet_independent_operator_threshold": (
            len(approval_operators) >= old["minimum_distinct_approval_operators"]
        ),
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
        "approval_operator_ids": approval_operators,
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
    report_replays = all(
        report.get(field) == rebuilt[field]
        for field in ("checks", "approval_operator_ids", "failed_checks", "decision")
    )
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


def root_rotation_log_link_review(rotation_report: object, append_log_report: object) -> dict[str, object]:
    """Carry an append-only log artifact into a root-rotation manual review.

    The log proves only this teaching log's prefix preservation and entry
    coverage.  It neither verifies approvals nor establishes that a root ID
    names a trustworthy key, so no result from this function can apply a root
    update automatically.
    """
    if not trust_root_rotation_certificate(rotation_report)["valid"]:
        raise ValueError("rotation_report must be a valid root-rotation policy artifact")
    if not append_only_certificate(append_log_report):
        raise ValueError("append_log_report must be a valid append-only log artifact")
    old_roots = set(rotation_report["trust_state"]["root_ids"])
    new_roots = set(rotation_report["proposal"]["new_root_ids"])
    added_roots = sorted(new_roots - old_roots)
    new_entries = set(append_log_report["new_entries"])
    expected_entries = [f"key:{root_id}" for root_id in added_roots]
    missing_entries = [entry for entry in expected_entries if entry not in new_entries]
    log_covers_added_roots = not missing_entries
    policy_decision = rotation_report["decision"]
    if policy_decision == "reject":
        decision = "reject"
    elif policy_decision == "accept_for_policy_only" and log_covers_added_roots:
        decision = "manual_review_with_policy_and_append_only_log_evidence"
    elif log_covers_added_roots:
        decision = "manual_review_with_append_only_log_evidence_and_unresolved_policy"
    else:
        decision = "manual_review_missing_added_root_log_entries"
    return {
        "contract": "root-rotation-log-link-review/v1",
        "rotation_report": rotation_report,
        "append_log_report": append_log_report,
        "added_root_ids": added_roots,
        "expected_log_entries": expected_entries,
        "missing_log_entries": missing_entries,
        "log_covers_added_roots": log_covers_added_roots,
        "policy_decision": policy_decision,
        "decision": decision,
        "automatic_apply": False,
        "cryptographic_verification": "not_performed",
        "identity_binding": "not_established_by_log_entries",
    }


def _positive_versions(value: object, name: str) -> list[int]:
    if (not isinstance(value, list) or not value
            or any(not isinstance(item, int) or isinstance(item, bool) or item < 1 for item in value)
            or len(set(value)) != len(value)):
        raise ValueError(f"{name} 必须是互异的正整数列表")
    return list(value)


def _client_recovery_state(value: object) -> dict[str, object]:
    required = {
        "client_id", "trusted_root_ids", "stored_epoch", "supported_policy_versions",
        "recovery_operator_ids", "minimum_distinct_recovery_operators",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("client 必须声明标识、根、纪元、格式与恢复运营者")
    recovery_operators = _root_ids(value["recovery_operator_ids"], "recovery_operator_ids")
    recovery_threshold = _nonnegative_int(
        value["minimum_distinct_recovery_operators"], "minimum_distinct_recovery_operators",
    )
    if not 1 <= recovery_threshold <= len(recovery_operators):
        raise ValueError("minimum_distinct_recovery_operators 必须在 1 到恢复运营者数量之间")
    return {
        "client_id": _nonempty_string(value["client_id"], "client_id"),
        "trusted_root_ids": _root_ids(value["trusted_root_ids"], "trusted_root_ids"),
        "stored_epoch": _nonnegative_int(value["stored_epoch"], "stored_epoch"),
        "supported_policy_versions": _positive_versions(value["supported_policy_versions"], "supported_policy_versions"),
        "recovery_operator_ids": recovery_operators,
        "minimum_distinct_recovery_operators": recovery_threshold,
    }


def _emergency_recovery_plan(value: object, current_roots: set[str]) -> dict[str, object]:
    required = {
        "policy_format_version", "compromised_root_ids", "recovery_claim_operator_ids", "out_of_band_channel_declared",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("emergency_plan 必须声明格式、受损根、恢复声明和带外通道")
    format_version = _nonnegative_int(value["policy_format_version"], "policy_format_version")
    if format_version < 1:
        raise ValueError("policy_format_version 必须为正整数")
    compromised = _root_ids(value["compromised_root_ids"], "compromised_root_ids")
    if not set(compromised).issubset(current_roots):
        raise ValueError("compromised_root_ids 必须属于当前根集合")
    channel = value["out_of_band_channel_declared"]
    if not isinstance(channel, bool):
        raise ValueError("out_of_band_channel_declared 必须是布尔值")
    return {
        "policy_format_version": format_version,
        "compromised_root_ids": compromised,
        "recovery_claim_operator_ids": _root_ids(value["recovery_claim_operator_ids"], "recovery_claim_operator_ids"),
        "out_of_band_channel_declared": channel,
    }


def root_rotation_recovery_compatibility_report(
    rotation_report: object, clients: object, emergency_plan: object,
) -> dict[str, object]:
    """Replay fictional emergency-recovery compatibility without applying it.

    A client must already pin its recovery authorities and understand the
    declared policy format.  This reports why a particular client needs manual
    recovery; it is neither an updater nor an authorization mechanism.
    """
    if not trust_root_rotation_certificate(rotation_report)["valid"]:
        raise ValueError("rotation_report 必须是有效的根轮换策略产物")
    if not isinstance(clients, list) or not clients:
        raise ValueError("clients 必须是非空列表")
    normalized_clients = [_client_recovery_state(client) for client in clients]
    if len({client["client_id"] for client in normalized_clients}) != len(normalized_clients):
        raise ValueError("client_id 不能重复")
    current_roots = set(rotation_report["trust_state"]["root_ids"])
    plan = _emergency_recovery_plan(emergency_plan, current_roots)
    proposal = rotation_report["proposal"]
    approval_claims = set(proposal["approval_claims"])
    compromised = set(plan["compromised_root_ids"])
    client_reports = []
    for client in normalized_clients:
        covered_approvals = sorted(approval_claims & set(client["trusted_root_ids"]))
        covered_recovery_operators = sorted(
            set(plan["recovery_claim_operator_ids"]) & set(client["recovery_operator_ids"])
        )
        checks = {
            "policy_format_supported": plan["policy_format_version"] in client["supported_policy_versions"],
            "epoch_advances_client_state": proposal["new_epoch"] > client["stored_epoch"],
            "client_covers_current_root_threshold_claims": len(covered_approvals) >= rotation_report["trust_state"]["threshold"],
            "regular_approval_avoids_declared_compromised_roots": not bool(approval_claims & compromised),
            "out_of_band_channel_declared": plan["out_of_band_channel_declared"],
            "client_covers_recovery_operator_threshold": (
                len(covered_recovery_operators) >= client["minimum_distinct_recovery_operators"]
            ),
        }
        if not checks["policy_format_supported"]:
            decision = "manual_recovery_required_unsupported_policy_format"
        elif not checks["epoch_advances_client_state"]:
            decision = "manual_recovery_required_client_epoch_state"
        elif all((checks["out_of_band_channel_declared"], checks["client_covers_recovery_operator_threshold"])):
            decision = "manual_recovery_with_declared_authorities"
        else:
            decision = "manual_recovery_missing_declared_authority_coverage"
        client_reports.append({
            "client": client,
            "covered_current_approval_root_ids": covered_approvals,
            "covered_recovery_operator_ids": covered_recovery_operators,
            "checks": checks,
            "decision": decision,
            "automatic_apply": False,
        })
    return {
        "contract": RECOVERY_COMPATIBILITY_CONTRACT,
        "rotation_policy_decision": rotation_report["decision"],
        "transition": {
            "from_epoch": rotation_report["trust_state"]["epoch"],
            "to_epoch": proposal["new_epoch"],
            "approval_claim_root_ids": sorted(approval_claims),
        },
        "emergency_plan": plan,
        "client_reports": client_reports,
        "automatic_apply": False,
        "cryptographic_verification": "not_performed",
        "interpretation": "fictional_client_compatibility_and_predeclared_recovery_authority_review_only",
    }


def root_rotation_recovery_compatibility_certificate(
    rotation_report: object, clients: object, emergency_plan: object, report: object,
) -> bool:
    """Rebuild the compatibility review and reject changed client decisions."""
    if not isinstance(report, dict):
        return False
    try:
        return report == root_rotation_recovery_compatibility_report(rotation_report, clients, emergency_plan)
    except (KeyError, ValueError):
        return False
