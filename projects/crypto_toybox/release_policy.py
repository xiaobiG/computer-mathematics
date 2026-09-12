"""教学用的软件发布元数据审计；不验证真实签名，也不下载撤销信息。"""

from __future__ import annotations

CONTRACT = "signed-release-policy-audit/v2"
TRUSTED_KEY_REGISTRY_CONTRACT = "trusted-key-registry/v1"
EXPECTED_CONTEXT = "software-update/v1"
EXPECTED_PURPOSE = "code-signing"
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
        "version", "issuer", "key_id", "algorithm", "purpose", "context",
        "signature_claim_valid", "revocation_info_available",
    }
    if set(release) != required:
        raise ValueError("release 字段必须与 signed-release-policy-audit/v1 完全一致")
    normalized = {
        "version": _require_nonnegative_int(release["version"], "version"),
        "issuer": _require_nonempty_string(release["issuer"], "issuer"),
        "key_id": _require_nonempty_string(release["key_id"], "key_id"),
        "algorithm": _require_nonempty_string(release["algorithm"], "algorithm"),
        "purpose": _require_nonempty_string(release["purpose"], "purpose"),
        "context": _require_nonempty_string(release["context"], "context"),
    }
    for field in ("signature_claim_valid", "revocation_info_available"):
        if not isinstance(release[field], bool):
            raise ValueError(f"{field} 必须是布尔值")
        normalized[field] = release[field]
    return normalized


def _normalize_trusted_key_registry(value: object) -> list[dict[str, str]]:
    """Normalize a frozen fictional registry, never a real trust store."""
    if not isinstance(value, list) or not value:
        raise ValueError("trusted_key_registry must be a non-empty list")
    records: list[dict[str, str]] = []
    identifiers: set[tuple[str, str]] = set()
    required = {"issuer", "key_id", "algorithm", "purpose", "status"}
    for item in value:
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError("each trusted key record must match trusted-key-registry/v1")
        record = {field: _require_nonempty_string(item[field], field) for field in required}
        if record["status"] not in {"active", "retired", "revoked"}:
            raise ValueError("trusted key status must be active, retired, or revoked")
        identifier = (record["issuer"], record["key_id"])
        if identifier in identifiers:
            raise ValueError("trusted key registry must not repeat an issuer/key_id binding")
        identifiers.add(identifier)
        records.append(record)
    return records


def signed_release_policy_report(
    last_accepted_version: int,
    candidate_release: object,
    trusted_key_registry: object,
    *,
    on_revocation_info_unavailable: str = "reject",
) -> dict[str, object]:
    """Audit a fictional release against an explicit anti-rollback policy.

    This is not an updater and ``signature_claim_valid`` is not cryptographic
    verification.  The registry is a fixed, fictional trust input rather than
    a candidate's self-declared "trusted" flag.  It lets a learner replay
    which prerequisite rejects a candidate before any real signature library
    or network is involved.
    """
    last_accepted_version = _require_nonnegative_int(last_accepted_version, "last_accepted_version")
    if on_revocation_info_unavailable not in {"reject", "manual_review"}:
        raise ValueError("撤销信息不可用策略只能是 reject 或 manual_review")
    release = _normalize_release(candidate_release)
    registry = _normalize_trusted_key_registry(trusted_key_registry)
    key_record = next(
        (record for record in registry if (record["issuer"], record["key_id"]) == (release["issuer"], release["key_id"])),
        None,
    )
    checks = {
        "newer_than_protected_state": release["version"] > last_accepted_version,
        "signature_claim_valid": release["signature_claim_valid"],
        "issuer_key_binding_is_registered": key_record is not None,
        "algorithm_allowed": release["algorithm"] in ALLOWED_ALGORITHMS,
        "algorithm_matches_registered_key": key_record is not None and release["algorithm"] == key_record["algorithm"],
        "purpose_matches_expected_protocol": release["purpose"] == EXPECTED_PURPOSE,
        "purpose_matches_registered_key": key_record is not None and release["purpose"] == key_record["purpose"],
        "context_matches": release["context"] == EXPECTED_CONTEXT,
        "key_is_active": key_record is not None and key_record["status"] == "active",
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
        "trusted_key_registry_contract": TRUSTED_KEY_REGISTRY_CONTRACT,
        "trusted_key_registry": registry,
        "matched_trusted_key": key_record,
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
            report["trusted_key_registry"],
            on_revocation_info_unavailable=report["on_revocation_info_unavailable"],
        )
    except (KeyError, ValueError):
        return empty
    registry_replays = (
        report.get("trusted_key_registry_contract") == TRUSTED_KEY_REGISTRY_CONTRACT
        and report.get("trusted_key_registry") == rebuilt["trusted_key_registry"]
        and report.get("matched_trusted_key") == rebuilt["matched_trusted_key"]
    )
    checks_replay = report.get("checks") == rebuilt["checks"]
    failed_checks_replay = report.get("failed_checks") == rebuilt["failed_checks"]
    decision_replays = report.get("decision") == rebuilt["decision"]
    safety_boundary_preserved = (
        report.get("automatic_install") is False
        and report.get("causal_interpretation") == "not_established"
    )
    valid = all((registry_replays, checks_replay, failed_checks_replay, decision_replays, safety_boundary_preserved))
    return {
        "contract_matches": True,
        "release_is_well_formed": True,
        "trusted_registry_replays": registry_replays,
        "checks_replay": checks_replay,
        "failed_checks_replay": failed_checks_replay,
        "decision_replays": decision_replays,
        "safety_boundary_preserved": safety_boundary_preserved,
        "valid": valid,
    }
