"""Inspect IEEE 754 binary64 fields and neighbouring representable values."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite, isnan, nextafter, ulp
from struct import pack, unpack


@dataclass(frozen=True)
class Float64Parts:
    sign: int
    biased_exponent: int
    fraction: int
    classification: str


def float64_parts(value: float) -> Float64Parts:
    """Return the sign, exponent and 52 fraction bits of a Python float.

    CPython's ``float`` is IEEE 754 binary64 on the supported teaching
    platforms.  The bit inspection is illustrative, not a replacement for a
    portability check in unusual runtimes.
    """
    bits = unpack(">Q", pack(">d", value))[0]
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7FF
    fraction = bits & ((1 << 52) - 1)
    if exponent == 0x7FF:
        classification = "infinity" if fraction == 0 else "nan"
    elif exponent == 0:
        classification = "zero" if fraction == 0 else "subnormal"
    else:
        classification = "normal"
    return Float64Parts(sign, exponent, fraction, classification)


def adjacent_values(value: float) -> tuple[float, float]:
    """Return the immediately representable finite neighbours of a finite value."""
    if not isfinite(value):
        raise ValueError("adjacent values are only defined here for finite inputs")
    return nextafter(value, -inf), nextafter(value, inf)


def spacing_at(value: float) -> float:
    """Return the ULP spacing at a finite non-NaN teaching value."""
    if not isfinite(value) or isnan(value):
        raise ValueError("spacing is only defined here for finite inputs")
    return ulp(value)
