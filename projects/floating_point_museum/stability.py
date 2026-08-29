"""Auditable stable and unstable formulas for a quadratic's small root."""

from __future__ import annotations

from decimal import Decimal, localcontext
from math import isfinite, sqrt


def _validate_quadratic(a: float, b: float, c: float) -> None:
    if any(not isfinite(value) for value in (a, b, c)):
        raise ValueError("quadratic coefficients must be finite")
    if a == 0:
        raise ValueError("a must be nonzero for a quadratic")
    if b * b - 4.0 * a * c < 0:
        raise ValueError("this teaching experiment requires real roots")


def direct_quadratic_roots(a: float, b: float, c: float) -> tuple[float, float]:
    """Use the textbook formula, including its cancellation-prone branch."""
    _validate_quadratic(a, b, c)
    discriminant = sqrt(b * b - 4.0 * a * c)
    return ((-b - discriminant) / (2.0 * a), (-b + discriminant) / (2.0 * a))


def stable_quadratic_roots(a: float, b: float, c: float) -> tuple[float, float]:
    """Compute roots via q=-1/2(b+sign(b)*sqrt(discriminant)).

    One root is ``q/a``; the other follows from the Vieta relation
    ``r_1*r_2=c/a`` as ``c/q``.  This avoids subtracting nearly equal values
    on the small-root branch.  It is a teaching implementation, not a full
    production polynomial solver.
    """
    _validate_quadratic(a, b, c)
    discriminant = sqrt(b * b - 4.0 * a * c)
    if discriminant == 0.0:
        root = -b / (2.0 * a)
        return root, root
    sign_b = 1.0 if b >= 0 else -1.0
    q = -0.5 * (b + sign_b * discriminant)
    return q / a, c / q


def decimal_reference_roots(a: float, b: float, c: float) -> tuple[float, float]:
    """Use high-precision decimal arithmetic as a classroom reference."""
    _validate_quadratic(a, b, c)
    with localcontext() as context:
        context.prec = 80
        coefficient_a, coefficient_b, coefficient_c = (Decimal(str(value)) for value in (a, b, c))
        discriminant = coefficient_b * coefficient_b - Decimal(4) * coefficient_a * coefficient_c
        root_discriminant = discriminant.sqrt()
        denominator = Decimal(2) * coefficient_a
        return (
            float((-coefficient_b - root_discriminant) / denominator),
            float((-coefficient_b + root_discriminant) / denominator),
        )


def _relative_error(estimate: float, reference: float) -> float:
    if reference == 0.0:
        return abs(estimate)
    return abs(estimate - reference) / abs(reference)


def quadratic_stability_report(a: float, b: float, c: float) -> dict[str, object]:
    """Compare direct and stable formulas against a high-precision reference."""
    direct_roots = direct_quadratic_roots(a, b, c)
    stable_roots = stable_quadratic_roots(a, b, c)
    reference_roots = decimal_reference_roots(a, b, c)
    direct_small = min(direct_roots, key=abs)
    stable_small = min(stable_roots, key=abs)
    reference_small = min(reference_roots, key=abs)
    direct_error = _relative_error(direct_small, reference_small)
    stable_error = _relative_error(stable_small, reference_small)
    return {
        "direct_roots": direct_roots,
        "stable_roots": stable_roots,
        "reference_roots": reference_roots,
        "direct_small_root_relative_error": direct_error,
        "stable_small_root_relative_error": stable_error,
        "certificate": {
            "stable_formula_is_no_worse_for_small_root": stable_error <= direct_error,
            "stable_small_root_has_high_accuracy": stable_error <= 1e-12,
            "direct_formula_exposes_cancellation": direct_error >= 1e-6,
        },
    }
