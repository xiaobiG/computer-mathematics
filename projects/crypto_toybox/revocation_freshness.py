"""Replay a fictional certificate-status freshness decision; never parse PKI."""

from __future__ import annotations


CONTRACT = "revocation-status-freshness-audit/v1"


def _nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _nonnegative_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _status_response(value: object) -> dict[str, object]:
    required = {
        "issuer", "key_id", "status", "this_update", "next_update", "produced_at", "signer_authorized",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("status_response must match revocation-status-freshness-audit/v1")
    status = _nonempty_string(value["status"], "status")
    if status not in {"good", "revoked", "unknown"}:
        raise ValueError("status must be good, revoked, or unknown")
    if not isinstance(value["signer_authorized"], bool):
        raise ValueError("signer_authorized must be boolean")
    response = {
        "issuer": _nonempty_string(value["issuer"], "issuer"),
        "key_id": _nonempty_string(value["key_id"], "key_id"),
        "status": status,
        "this_update": _nonnegative_int(value["this_update"], "this_update"),
        "next_update": _nonnegative_int(value["next_update"], "next_update"),
        "produced_at": _nonnegative_int(value["produced_at"], "produced_at"),
        "signer_authorized": value["signer_authorized"],
    }
    if not response["this_update"] <= response["produced_at"] <= response["next_update"]:
        raise ValueError("status response times must satisfy this_update <= produced_at <= next_update")
    return response


def revocation_status_freshness_report(
    expected_issuer: object, expected_key_id: object, status_response: object, validation_time: object,
) -> dict[str, object]:
    """Audit the time and authority claims of a declared fictional status response.

    Integer times are classroom timeline ticks, not Unix timestamps.  The
    ``signer_authorized`` field is an external trust assertion, not signature
    verification.  Consequently this report can only teach decision ordering.
    """
    issuer = _nonempty_string(expected_issuer, "expected_issuer")
    key_id = _nonempty_string(expected_key_id, "expected_key_id")
    response = _status_response(status_response)
    now = _nonnegative_int(validation_time, "validation_time")
    checks = {
        "status_targets_expected_issuer_key": (response["issuer"], response["key_id"]) == (issuer, key_id),
        "status_signer_is_authorized": response["signer_authorized"],
        "status_is_good": response["status"] == "good",
        "this_update_is_not_in_the_future": response["this_update"] <= now,
        "produced_at_is_not_in_the_future": response["produced_at"] <= now,
        "next_update_has_not_elapsed": now <= response["next_update"],
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    return {
        "contract": CONTRACT,
        "expected_issuer": issuer,
        "expected_key_id": key_id,
        "validation_time": now,
        "declared_status_response": response,
        "checks": checks,
        "failed_checks": failed_checks,
        "decision": "fresh_good_status_for_policy_only" if all(checks.values()) else "reject",
        "automatic_install": False,
        "network_or_signature_verification_performed": False,
        "boundary": (
            "fictional timeline only; does not parse OCSP or CRL, verify a responder signature, "
            "establish issuer authorization, contact a network service, or model clock compromise"
        ),
    }


def revocation_status_freshness_certificate(
    expected_issuer: object, expected_key_id: object, status_response: object, validation_time: object, report: object,
) -> bool:
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        expected = revocation_status_freshness_report(
            expected_issuer, expected_key_id, status_response, validation_time,
        )
    except (TypeError, ValueError):
        return False
    return report == expected
