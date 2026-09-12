"""Teaching CRT merger for compatible congruences; not a private-key primitive."""

from __future__ import annotations

from math import gcd

from projects.crypto_toybox.main import modular_inverse


Congruence = tuple[int, int]


def _validate_congruence(congruence: Congruence) -> None:
    if (not isinstance(congruence, tuple) or len(congruence) != 2
            or not all(isinstance(value, int) and not isinstance(value, bool) for value in congruence)
            or congruence[1] <= 0):
        raise ValueError("each congruence must be an integer (residue, positive modulus) pair")


def combine_congruences(first: Congruence, second: Congruence) -> Congruence:
    """Merge two compatible congruences and return the least positive modulus.

    The result ``(r, M)`` represents every solution ``x == r (mod M)``.
    It accepts non-coprime moduli exactly when their residues agree modulo the
    gcd; otherwise the two constraints cannot be true at the same time.
    """
    _validate_congruence(first)
    _validate_congruence(second)
    first_residue, first_modulus = first
    second_residue, second_modulus = second
    first_residue %= first_modulus
    second_residue %= second_modulus
    divisor = gcd(first_modulus, second_modulus)
    difference = second_residue - first_residue
    if difference % divisor:
        raise ValueError("congruences are incompatible")
    reduced_first = first_modulus // divisor
    reduced_second = second_modulus // divisor
    multiplier = (difference // divisor * modular_inverse(reduced_first, reduced_second)) % reduced_second \
        if reduced_second > 1 else 0
    modulus = first_modulus * reduced_second
    return (first_residue + first_modulus * multiplier) % modulus, modulus


def chinese_remainder(congruences: list[Congruence]) -> Congruence:
    """Merge a non-empty list of congruences from left to right."""
    if not isinstance(congruences, list) or not congruences:
        raise ValueError("congruences must be a non-empty list")
    result = congruences[0]
    _validate_congruence(result)
    for congruence in congruences[1:]:
        result = combine_congruences(result, congruence)
    return result
