"""HMAC 教学包装：使用标准库，不实现自制认证协议。"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest, digest


def hmac_tag(key: bytes, message: bytes) -> bytes:
    """Return an HMAC-SHA-256 tag; require a non-empty shared key for the demo."""
    if not key:
        raise ValueError("shared key must not be empty")
    return digest(key, message, sha256)


def verify_hmac(key: bytes, message: bytes, tag: bytes) -> bool:
    """Verify with constant-time comparison where the platform can provide it."""
    return compare_digest(hmac_tag(key, message), tag)


def _validate_sequence(sequence: int, name: str) -> None:
    if not isinstance(sequence, int) or isinstance(sequence, bool) or not 0 <= sequence < 2 ** 64:
        raise ValueError(f"{name} must be an unsigned 64-bit sequence number")


def encode_sequenced_message(sequence: int, payload: bytes) -> bytes:
    """Length-prefix one sequence number and payload before authenticating it.

    This avoids ambiguous byte concatenation in the teaching protocol.  It is
    intentionally a codec, not a complete wire protocol or serialization
    standard.
    """
    _validate_sequence(sequence, "sequence")
    if not isinstance(payload, bytes) or len(payload) >= 2 ** 32:
        raise ValueError("payload must be bytes shorter than 2**32")
    return sequence.to_bytes(8, "big") + len(payload).to_bytes(4, "big") + payload


def sequenced_hmac_tag(key: bytes, sequence: int, payload: bytes) -> bytes:
    """Authenticate an unambiguously encoded sequence number and payload."""
    return hmac_tag(key, encode_sequenced_message(sequence, payload))


@dataclass(frozen=True)
class SequencedHmacVerification:
    """Separate cryptographic tag validity from replay freshness."""

    tag_valid: bool
    sequence_is_fresh: bool
    accepted: bool


def verify_sequenced_hmac(
    key: bytes, sequence: int, payload: bytes, tag: bytes, *, last_accepted_sequence: int | None,
) -> SequencedHmacVerification:
    """Verify HMAC and a strictly increasing sequence policy without mutating state.

    A real receiver must persist its replay state and specify recovery/window
    rules.  The explicit result makes the key lesson observable: a replay can
    have a valid MAC while still being rejected for being old.
    """
    _validate_sequence(sequence, "sequence")
    if last_accepted_sequence is not None:
        _validate_sequence(last_accepted_sequence, "last_accepted_sequence")
    encoded = encode_sequenced_message(sequence, payload)
    tag_valid = isinstance(tag, bytes) and compare_digest(hmac_tag(key, encoded), tag)
    sequence_is_fresh = last_accepted_sequence is None or sequence > last_accepted_sequence
    return SequencedHmacVerification(tag_valid, sequence_is_fresh, tag_valid and sequence_is_fresh)
