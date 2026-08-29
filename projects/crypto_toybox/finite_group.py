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
