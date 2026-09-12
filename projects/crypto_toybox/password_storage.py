"""PBKDF2 record-shape teaching code; never a complete authentication system."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes


ALGORITHM = "pbkdf2_sha256"
SALT_BYTES = 16


@dataclass(frozen=True)
class PasswordRecord:
    """The public fields needed to verify one teaching password record."""

    algorithm: str
    rounds: int
    salt: bytes
    derived_key: bytes


def _validate_password(password: str) -> None:
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")


def _validate_rounds(rounds: int) -> None:
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds <= 0:
        raise ValueError("rounds must be a positive integer")


def make_password_record(password: str, *, rounds: int, salt: bytes | None = None) -> PasswordRecord:
    """Create a PBKDF2 record with a unique random salt by default.

    ``salt`` exists only for deterministic classroom tests; callers should omit
    it in this demo.  Production authentication needs an audited password
    library and deployment-specific parameter calibration.
    """
    _validate_password(password)
    _validate_rounds(rounds)
    if salt is None:
        salt = token_bytes(SALT_BYTES)
    if not isinstance(salt, bytes) or len(salt) < SALT_BYTES:
        raise ValueError("salt must contain at least 16 bytes")
    derived_key = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return PasswordRecord(ALGORITHM, rounds, salt, derived_key)


def verify_password(password: str, record: PasswordRecord) -> bool:
    """Derive with record parameters and compare without early-exit equality."""
    _validate_password(password)
    if not isinstance(record, PasswordRecord) or record.algorithm != ALGORITHM:
        raise ValueError("unsupported password record")
    _validate_rounds(record.rounds)
    if not isinstance(record.salt, bytes) or len(record.salt) < SALT_BYTES:
        raise ValueError("invalid password-record salt")
    candidate = pbkdf2_hmac("sha256", password.encode("utf-8"), record.salt, record.rounds)
    return compare_digest(candidate, record.derived_key)


def migrate_after_successful_login(
    password: str, record: PasswordRecord, *, target_rounds: int, salt: bytes | None = None,
) -> PasswordRecord | None:
    """Upgrade an old record only after successful password verification.

    ``None`` means the candidate password was wrong, so no migration is
    permitted.  Returning the original immutable record means no upgrade was
    needed.  The function models record migration, not login rate limiting,
    session management, MFA, or breach response.
    """
    _validate_rounds(target_rounds)
    if not verify_password(password, record):
        return None
    if record.rounds >= target_rounds:
        return record
    return make_password_record(password, rounds=target_rounds, salt=salt)
