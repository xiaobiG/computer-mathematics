"""Tiny finite-field multiplicative-group experiments; never security code."""

from __future__ import annotations

from math import isqrt


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    return not any(value % divisor == 0 for divisor in range(3, isqrt(value) + 1, 2))


def _require_prime_field(prime: int) -> None:
    if not is_prime(prime):
        raise ValueError("teaching multiplicative groups require a prime modulus")


def multiplicative_order(element: int, prime: int) -> int:
    """Return the order of a nonzero element in F_p^* by small-group enumeration."""
    _require_prime_field(prime)
    element %= prime
    if element == 0:
        raise ValueError("zero is not in the multiplicative group")
    value = 1
    for order in range(1, prime):
        value = value * element % prime
        if value == 1:
            return order
    raise AssertionError("a finite group element must return to its identity")


def subgroup_elements(generator: int, prime: int) -> list[int]:
    """Enumerate <generator> in a small prime field, starting with its identity."""
    order = multiplicative_order(generator, prime)
    return [pow(generator, exponent, prime) for exponent in range(order)]


def primitive_generators(prime: int) -> list[int]:
    """Return all generators of F_p^*; O(p^2) and suitable only for lessons."""
    _require_prime_field(prime)
    return [element for element in range(1, prime) if multiplicative_order(element, prime) == prime - 1]


def finite_group_report(generator: int, prime: int) -> dict[str, object]:
    """Record small-field subgroup facts as explicit, finite witnesses.

    This is deliberately exhaustive: it is useful for teaching $p=23$, not for
    selecting real cryptographic groups. Every result below is a checkable
    finite counterpart of a group-theory statement used by DH parameter rules.
    """
    order = multiplicative_order(generator, prime)
    elements = tuple(subgroup_elements(generator, prime))
    element_set = set(elements)
    powers = tuple((exponent, pow(generator, exponent, prime)) for exponent in range(order))
    inverses = tuple((element, pow(element, prime - 2, prime)) for element in elements)
    return {
        "generator": generator % prime,
        "prime": prime,
        "order": order,
        "powers": powers,
        "elements": elements,
        "order_divides_group_size": (prime - 1) % order == 0,
        "elements_are_distinct": len(element_set) == order,
        "closed_under_multiplication": all((left * right) % prime in element_set
                                             for left in elements for right in elements),
        "inverses_stay_in_subgroup": all((element * inverse) % prime == 1
                                           and inverse in element_set for element, inverse in inverses),
        "generator_spans_full_group": order == prime - 1,
    }


def finite_group_certificate(generator: int, prime: int, report: dict[str, object]) -> dict[str, bool]:
    """Recompute a finite subgroup report, including every listed power and inverse."""
    empty = {
        "fields_match_recomputed_group": False,
        "order_divides_group_size": False,
        "elements_are_distinct": False,
        "closed_under_multiplication": False,
        "inverses_stay_in_subgroup": False,
        "valid": False,
    }
    try:
        if not isinstance(report, dict):
            return empty
        expected = finite_group_report(generator, prime)
        if set(report) != set(expected):
            return empty
        fields_match = report == expected
        return {
            "fields_match_recomputed_group": fields_match,
            "order_divides_group_size": fields_match and expected["order_divides_group_size"],
            "elements_are_distinct": fields_match and expected["elements_are_distinct"],
            "closed_under_multiplication": fields_match and expected["closed_under_multiplication"],
            "inverses_stay_in_subgroup": fields_match and expected["inverses_stay_in_subgroup"],
            "valid": fields_match and all((
                expected["order_divides_group_size"], expected["elements_are_distinct"],
                expected["closed_under_multiplication"], expected["inverses_stay_in_subgroup"],
            )),
        }
    except (TypeError, ValueError):
        return empty


def discrete_log_toy(generator: int, target: int, prime: int, *, max_prime: int = 1_000) -> int | None:
    """Brute-force a tiny discrete log to demonstrate why small groups are unsafe.

    The explicit bound prevents this teaching helper from being mistaken for a
    general cryptanalytic tool.
    """
    if prime > max_prime:
        raise ValueError("toy discrete-log enumeration is limited to tiny prime fields")
    target %= prime
    powers = subgroup_elements(generator, prime)
    return powers.index(target) if target in powers else None
