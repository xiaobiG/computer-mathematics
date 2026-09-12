"""教学用的软件发布元数据审计；不验证真实签名，也不下载撤销信息。"""

from __future__ import annotations

CONTRACT = "signed-release-policy-audit/v1"
EXPECTED_CONTEXT = "software-update/v1"
ALLOWED_ALGORITHMS = {"Ed25519", "RSA-PSS-SHA256"}


def _require_nonnegative_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} 必须是非负整数")
    return value


def _require_nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} 必须是非空字符串")
    return value


def _normalize_release(release: object) -> dict[str, object]:
    """Validate classroom metadata, deliberately treating signature validity as an input claim."""
    if not isinstance(release, dict):
        raise ValueError("release 必须是字典")
    required = {
        "version", "key_id", "algorithm", "context", "signature_claim_valid",
        "key_identity_trusted", "key_status", "revocation_info_available",
    }
    if set(release) != required:
        raise ValueError("release 字段必须与 signed-release-policy-audit/v1 完全一致")
    normalized = {
        "version": _require_nonnegative_int(release["version"], "version"),
        "key_id": _require_nonempty_string(release["key_id"], "key_id"),
        "algorithm": _require_nonempty_string(release["algorithm"], "algorithm"),
        "context": _require_nonempty_string(release["context"], "context"),
        "key_status": _require_nonempty_string(release["key_status"], "key_status"),
    }
    for field in ("signature_claim_valid", "key_identity_trusted", "revocation_info_available"):
        if not isinstance(release[field], bool):
            raise ValueError(f"{field} 必须是布尔值")
        normalized[field] = release[field]
    return normalized


def signed_release_policy_report(
    last_accepted_version: int,
    candidate_release: object,
    *,
    on_revocation_info_unavailable: str = "reject",
) -> dict[str, object]:
    """Audit a fictional release against an explicit anti-rollback policy.

    This is not an updater and ``signature_claim_valid`` is not cryptographic
    verification.  It lets a learner replay which prerequisite rejects a
    candidate before any real signature library or network is involved.
    """
    last_accepted_version = _require_nonnegative_int(last_accepted_version, "last_accepted_version")
    if on_revocation_info_unavailable not in {"reject", "manual_review"}:
        raise ValueError("撤销信息不可用策略只能是 reject 或 manual_review")
    release = _normalize_release(candidate_release)
    checks = {
        "newer_than_protected_state": release["version"] > last_accepted_version,
        "signature_claim_valid": release["signature_claim_valid"],
        "key_identity_trusted": release["key_identity_trusted"],
        "algorithm_allowed": release["algorithm"] in ALLOWED_ALGORITHMS,
        "context_matches": release["context"] == EXPECTED_CONTEXT,
        "key_is_active": release["key_status"] == "active",
        "revocation_info_available": release["revocation_info_available"],
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    if not checks["revocation_info_available"] and on_revocation_info_unavailable == "manual_review":
        decision = "manual_review"
    elif all(checks.values()):
        decision = "accept_for_policy_only"
    else:
        decision = "reject"
    return {
        "contract": CONTRACT,
        "last_accepted_version": last_accepted_version,
        "candidate_release": release,
        "on_revocation_info_unavailable": on_revocation_info_unavailable,
        "checks": checks,
        "failed_checks": failed_checks,
        "decision": decision,
        "automatic_install": False,
        "causal_interpretation": "not_established",
    }


def signed_release_policy_certificate(report: object) -> dict[str, bool]:
    """Independently replay a report and reject changed conclusions or fields."""
    empty = {
        "contract_matches": False,
        "release_is_well_formed": False,
        "checks_replay": False,
        "failed_checks_replay": False,
        "decision_replays": False,
        "safety_boundary_preserved": False,
        "valid": False,
    }
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return empty
    try:
        rebuilt = signed_release_policy_report(
            report["last_accepted_version"],
            report["candidate_release"],
            on_revocation_info_unavailable=report["on_revocation_info_unavailable"],
        )
    except (KeyError, ValueError):
        return empty
    checks_replay = report.get("checks") == rebuilt["checks"]
    failed_checks_replay = report.get("failed_checks") == rebuilt["failed_checks"]
    decision_replays = report.get("decision") == rebuilt["decision"]
    safety_boundary_preserved = (
        report.get("automatic_install") is False
        and report.get("causal_interpretation") == "not_established"
    )
    valid = all((checks_replay, failed_checks_replay, decision_replays, safety_boundary_preserved))
    return {
        "contract_matches": True,
        "release_is_well_formed": True,
        "checks_replay": checks_replay,
        "failed_checks_replay": failed_checks_replay,
        "decision_replays": decision_replays,
        "safety_boundary_preserved": safety_boundary_preserved,
        "valid": valid,
    }
