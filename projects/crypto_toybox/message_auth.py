"""HMAC 教学包装：使用标准库，不实现自制认证协议。"""

from __future__ import annotations

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
