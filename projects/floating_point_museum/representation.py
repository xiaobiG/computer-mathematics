"""Inspect IEEE 754 binary64 fields and neighbouring representable values."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import inf, isfinite, isnan, nextafter, ulp
from struct import pack, unpack


@dataclass(frozen=True)
class Float64Parts:
    sign: int
    biased_exponent: int
    fraction: int
    classification: str


@dataclass(frozen=True)
class DecimalRoundingReport:
    """An exact audit of a decimal source literal after binary64 conversion."""

    literal: str
    exact_value: Fraction
    stored_value: Fraction
    rounding_error: Fraction
    ulp_error: Fraction
    rounding_direction: str

    @property
    def certificate(self) -> dict[str, bool]:
        """Facts that a nearest-representable conversion must satisfy."""
        return {
            "stored_value_matches_exact_literal_when_marked_exact": (
                self.rounding_direction != "exact" or self.rounding_error == 0
            ),
            "rounding_error_is_within_half_ulp": abs(self.ulp_error) <= Fraction(1, 2),
            "valid": abs(self.ulp_error) <= Fraction(1, 2),
        }


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


def decimal_rounding_report(literal: str) -> DecimalRoundingReport:
    """Compare an exact finite decimal literal with the binary64 it produces.

    ``Fraction(literal)`` parses the source text as a rational decimal rather
    than first rounding it to a float.  The report is deliberately limited to
    finite values: infinities and NaNs have special IEEE-754 semantics and are
    not nearby rational approximations.
    """
    if not isinstance(literal, str):
        raise TypeError("literal must be a decimal string so its exact value is known")
    try:
        exact_value = Fraction(literal)
        stored_float = float(literal)
    except (ValueError, OverflowError, ZeroDivisionError) as error:
        raise ValueError("literal must name a finite rational decimal") from error
    if not isfinite(stored_float):
        raise ValueError("literal must round to a finite binary64 value")

    stored_value = Fraction.from_float(stored_float)
    rounding_error = stored_value - exact_value
    spacing = Fraction.from_float(ulp(stored_float))
    if rounding_error > 0:
        direction = "up"
    elif rounding_error < 0:
        direction = "down"
    else:
        direction = "exact"
    return DecimalRoundingReport(
        literal=literal,
        exact_value=exact_value,
        stored_value=stored_value,
        rounding_error=rounding_error,
        ulp_error=rounding_error / spacing,
        rounding_direction=direction,
    )


def decimal_rounding_certificate(report: DecimalRoundingReport) -> dict[str, bool]:
    """Recompute a decimal-conversion report and check nearest finite neighbours.

    A report's fields are useful teaching evidence but should not be trusted as
    input.  This certificate reparses the source literal exactly, reconstructs
    every report field, then confirms the stored binary64 fraction is no
    farther from the exact decimal than either finite adjacent float.  At the
    finite extremes only the available finite neighbour is compared.
    """
    if not isinstance(report, DecimalRoundingReport):
        return {
            "fields_match_recomputed_literal": False,
            "stored_value_is_nearest_finite_neighbour": False,
            "valid": False,
        }
    try:
        expected = decimal_rounding_report(report.literal)
        fields_match = report == expected
        stored_float = float(expected.stored_value)
        lower, upper = adjacent_values(stored_float)
        stored_distance = abs(expected.stored_value - expected.exact_value)
        neighbour_distances = []
        if isfinite(lower):
            neighbour_distances.append(abs(Fraction.from_float(lower) - expected.exact_value))
        if isfinite(upper):
            neighbour_distances.append(abs(Fraction.from_float(upper) - expected.exact_value))
        nearest = all(stored_distance <= distance for distance in neighbour_distances)
        return {
            "fields_match_recomputed_literal": fields_match,
            "stored_value_is_nearest_finite_neighbour": nearest,
            "valid": fields_match and nearest,
        }
    except (TypeError, ValueError, OverflowError):
        return {
            "fields_match_recomputed_literal": False,
            "stored_value_is_nearest_finite_neighbour": False,
            "valid": False,
        }


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
