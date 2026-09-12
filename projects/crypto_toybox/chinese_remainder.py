"""Teaching CRT merger for compatible congruences; not a private-key primitive."""

from __future__ import annotations

from math import gcd

from projects.crypto_toybox.main import modular_inverse, toy_rsa_keypair


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


def toy_rsa_crt_fault_report(
    p: int, q: int, public_exponent: int, representative: int, *, faulted_branch: str,
) -> dict[str, int | str | bool]:
    """Demonstrate the RSA-CRT fault identity with explicitly tiny factors.

    This is deliberately bounded classroom arithmetic.  It requires the
    factors as inputs, corrupts exactly one CRT residue by one, and exposes
    only the resulting gcd relation; it is not a private-key operation or a
    fault-injection tool for real RSA implementations.
    """
    if (not all(isinstance(value, int) and not isinstance(value, bool) for value in (p, q, public_exponent, representative))
            or p > 1_000 or q > 1_000):
        raise ValueError("use explicit integer toy primes no greater than 1000")
    if faulted_branch not in {"p", "q"}:
        raise ValueError("faulted_branch must be 'p' or 'q'")
    key = toy_rsa_keypair(p, q, public_exponent)
    if not 0 <= representative < key.modulus:
        raise ValueError("representative must lie in the toy RSA message range")
    residue_p = pow(representative, key.private_exponent % (p - 1), p)
    residue_q = pow(representative, key.private_exponent % (q - 1), q)
    correct, _ = chinese_remainder([(residue_p, p), (residue_q, q)])
    faulty_p = (residue_p + 1) % p if faulted_branch == "p" else residue_p
    faulty_q = (residue_q + 1) % q if faulted_branch == "q" else residue_q
    faulty, _ = chinese_remainder([(faulty_p, p), (faulty_q, q)])
    recovered_factor = gcd(correct - faulty, key.modulus)
    return {
        "modulus": key.modulus,
        "faulted_branch": faulted_branch,
        "correct_result": correct,
        "faulty_result": faulty,
        "difference_gcd": recovered_factor,
        "cofactor": key.modulus // recovered_factor if recovered_factor > 1 else 0,
        "nontrivial_factor_recovered": 1 < recovered_factor < key.modulus,
        "correct_matches_direct_private_power": correct == pow(representative, key.private_exponent, key.modulus),
    }


def toy_rsa_crt_fault_certificate(
    p: int, q: int, public_exponent: int, representative: int, faulted_branch: str, report: object,
) -> bool:
    """Replay a bounded toy CRT-fault report and reject altered arithmetic."""
    if not isinstance(report, dict):
        return False
    try:
        return report == toy_rsa_crt_fault_report(
            p, q, public_exponent, representative, faulted_branch=faulted_branch,
        )
    except (TypeError, ValueError):
        return False
