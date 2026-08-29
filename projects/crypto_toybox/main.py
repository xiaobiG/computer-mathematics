"""教学用途的模运算与小参数 RSA；不可用于真实安全场景。"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd

from projects.crypto_toybox.finite_group import is_prime


def _validate_mod_pow_inputs(base: int, exponent: int, modulus: int) -> None:
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (base, exponent, modulus)):
        raise ValueError("底数、指数和模数必须是整数")
    if modulus <= 1 or exponent < 0:
        raise ValueError("模数必须大于 1，指数必须非负")


@dataclass(frozen=True)
class ModPowEvent:
    """One square-and-multiply round after processing its lowest exponent bit."""

    iteration: int
    exponent_before: int
    bit: int
    result_after: int
    base_after: int
    exponent_after: int


@dataclass(frozen=True)
class ModPowOperationProfile:
    """Public teaching summary of square-and-multiply control flow."""

    bit_length: int
    one_bits: int
    squares: int
    conditional_multiplies: int
    total_modular_multiplications: int


@dataclass(frozen=True)
class EuclidEvent:
    """One division step in the nonnegative Euclidean algorithm."""

    iteration: int
    dividend: int
    divisor: int
    quotient: int
    remainder: int


def mod_pow_trace(base: int, exponent: int, modulus: int) -> tuple[int, list[ModPowEvent]]:
    """Compute a modular power while exposing the teaching loop invariant.

    Recording exponent bits is deliberately unsuitable for secret exponents.
    This function exists to audit the square-and-multiply derivation only.
    """
    _validate_mod_pow_inputs(base, exponent, modulus)
    result = 1
    base %= modulus
    events: list[ModPowEvent] = []
    iteration = 0
    while exponent:
        iteration += 1
        exponent_before = exponent
        bit = exponent & 1
        if bit:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
        events.append(ModPowEvent(iteration, exponent_before, bit, result, base, exponent))
    return result, events


def mod_pow_trace_certificate(
    original_base: int, original_exponent: int, modulus: int, result: int, events: list[ModPowEvent],
) -> bool:
    """Check every update against square-and-multiply and its terminal value."""
    try:
        _validate_mod_pow_inputs(original_base, original_exponent, modulus)
    except ValueError:
        return False
    expected_result, expected_base, expected_exponent = 1, original_base % modulus, original_exponent
    for iteration, event in enumerate(events, start=1):
        if (event.iteration != iteration or event.exponent_before != expected_exponent
                or event.bit != expected_exponent & 1):
            return False
        if event.bit:
            expected_result = (expected_result * expected_base) % modulus
        expected_base = (expected_base * expected_base) % modulus
        expected_exponent >>= 1
        if (event.result_after, event.base_after, event.exponent_after) != (
            expected_result, expected_base, expected_exponent,
        ):
            return False
    return expected_exponent == 0 and result == expected_result


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """Return the teaching modular power without retaining a bit-level trace."""
    result, _ = mod_pow_trace(base, exponent, modulus)
    return result


def mod_pow_operation_profile(exponent: int) -> ModPowOperationProfile:
    """Expose the public operation-count dependence on an exponent's bit pattern.

    This is a classroom leakage model, not a timing measurement or an attack.
    It must never be called with a secret exponent in a real cryptosystem.
    """
    if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
        raise ValueError("exponent must be a non-negative integer")
    bit_length = exponent.bit_length()
    one_bits = exponent.bit_count()
    return ModPowOperationProfile(
        bit_length=bit_length,
        one_bits=one_bits,
        squares=bit_length,
        conditional_multiplies=one_bits,
        total_modular_multiplications=bit_length + one_bits,
    )


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    divisor, x1, y1 = extended_gcd(b, a % b)
    return divisor, y1, x1 - (a // b) * y1


def extended_gcd_trace(a: int, b: int) -> tuple[tuple[int, int, int], list[EuclidEvent]]:
    """Return Bézout coefficients plus the decreasing remainder chain.

    The trace intentionally accepts only nonnegative classroom inputs, so each
    event has the familiar ``0 <= remainder < divisor`` termination argument.
    """
    if (any(not isinstance(value, int) or isinstance(value, bool) for value in (a, b))
            or a < 0 or b < 0 or (a == 0 and b == 0)):
        raise ValueError("Euclid trace needs nonnegative integers that are not both zero")
    left, right = a, b
    events: list[EuclidEvent] = []
    iteration = 0
    while right:
        iteration += 1
        quotient, remainder = divmod(left, right)
        events.append(EuclidEvent(iteration, left, right, quotient, remainder))
        left, right = right, remainder
    return extended_gcd(a, b), events


def extended_gcd_trace_certificate(
    a: int, b: int, result: tuple[int, int, int], events: list[EuclidEvent],
) -> bool:
    """Replay Euclidean divisions and independently check Bézout's identity."""
    if (any(not isinstance(value, int) or isinstance(value, bool) for value in (a, b))
            or a < 0 or b < 0 or (a == 0 and b == 0)
            or not isinstance(result, tuple) or len(result) != 3):
        return False
    divisor, coefficient_a, coefficient_b = result
    if any(not isinstance(value, int) or isinstance(value, bool) for value in result):
        return False
    left, right = a, b
    for iteration, event in enumerate(events, start=1):
        if right == 0:
            return False
        quotient, remainder = divmod(left, right)
        if event != EuclidEvent(iteration, left, right, quotient, remainder):
            return False
        left, right = right, remainder
    return right == 0 and divisor == left and a * coefficient_a + b * coefficient_b == divisor


def modular_inverse(value: int, modulus: int) -> int:
    divisor, inverse, _ = extended_gcd(value, modulus)
    if divisor != 1:
        raise ValueError("模逆元不存在")
    return inverse % modulus


@dataclass(frozen=True)
class RsaKeyPair:
    modulus: int
    public_exponent: int
    private_exponent: int


def toy_rsa_keypair(p: int, q: int, public_exponent: int) -> RsaKeyPair:
    """Construct a tiny RSA key after checking the mathematical preconditions.

    Trial division is deliberately limited to user-supplied classroom primes;
    this function never generates keys and is not cryptographic key validation.
    """
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (p, q, public_exponent)):
        raise ValueError("教学 RSA 参数必须是整数")
    if p == q:
        raise ValueError("教学参数中的两个质数必须不同")
    if not is_prime(p) or not is_prime(q):
        raise ValueError("教学 RSA 参数中的 p 和 q 必须是质数")
    phi = (p - 1) * (q - 1)
    if not 1 < public_exponent < phi or gcd(public_exponent, phi) != 1:
        raise ValueError("公开指数必须位于 (1, phi) 且与 phi 互素")
    return RsaKeyPair(p * q, public_exponent, modular_inverse(public_exponent, phi))


def rsa_keypair_certificate(p: int, q: int, key: RsaKeyPair) -> dict[str, bool]:
    """Independently audit the classroom RSA construction preconditions.

    Passing ``p`` and ``q`` is intentional: a real private-key API must not
    expose factorization merely to verify itself.  Here they make the theorem
    assumptions explicit and let learners check the modular-inverse relation
    used by the RSA correctness proof.
    """
    if (not isinstance(key, RsaKeyPair)
            or any(not isinstance(value, int) or isinstance(value, bool) for value in (p, q))):
        return {
            "distinct_prime_factors": False,
            "modulus_matches_factors": False,
            "public_exponent_is_a_unit": False,
            "private_exponent_is_inverse": False,
            "valid": False,
        }
    phi = (p - 1) * (q - 1)
    distinct_primes = p != q and is_prime(p) and is_prime(q)
    modulus_matches = key.modulus == p * q
    public_exponent_is_a_unit = 1 < key.public_exponent < phi and gcd(key.public_exponent, phi) == 1
    private_exponent_is_inverse = (
        public_exponent_is_a_unit and (key.public_exponent * key.private_exponent) % phi == 1
    )
    return {
        "distinct_prime_factors": distinct_primes,
        "modulus_matches_factors": modulus_matches,
        "public_exponent_is_a_unit": public_exponent_is_a_unit,
        "private_exponent_is_inverse": private_exponent_is_inverse,
        "valid": all((distinct_primes, modulus_matches, public_exponent_is_a_unit, private_exponent_is_inverse)),
    }


def encrypt(message: int, key: RsaKeyPair) -> int:
    if not 0 <= message < key.modulus:
        raise ValueError("教学明文必须位于 [0, n) 内")
    return mod_pow(message, key.public_exponent, key.modulus)


def decrypt(ciphertext: int, key: RsaKeyPair) -> int:
    if not 0 <= ciphertext < key.modulus:
        raise ValueError("教学密文必须位于 [0, n) 内")
    return mod_pow(ciphertext, key.private_exponent, key.modulus)


def raw_rsa_properties(left: int, right: int, key: RsaKeyPair) -> dict[str, bool]:
    """Expose two unsafe raw-RSA algebraic properties for a lesson only.

    The function does not construct an attack or padding scheme. Its purpose is
    to make deterministic and multiplicative structure visible, explaining why
    real systems need audited OAEP/PSS implementations.
    """
    first = encrypt(left, key)
    second = encrypt(right, key)
    return {
        "deterministic": first == encrypt(left, key),
        "multiplicative": encrypt((left * right) % key.modulus, key) == (first * second) % key.modulus,
    }


def rsa_round_trip_report(messages: list[int], key: RsaKeyPair) -> dict[str, object]:
    """Audit raw-RSA recovery on selected classroom messages.

    The report intentionally includes representatives sharing a factor with
    ``n`` so the CRT part of the correctness argument is checked in code too.
    It is a finite example audit, not a proof or a security test.
    """
    if not messages:
        raise ValueError("至少提供一个教学明文")
    checks = [
        (message, encrypt(message, key), decrypt(encrypt(message, key), key))
        for message in messages
    ]
    return {
        "all_recovered": all(original == recovered for original, _, recovered in checks),
        "non_coprime_messages": [original for original, _, _ in checks if gcd(original, key.modulus) != 1],
        "checks": checks,
    }


def toy_rsa_sign(representative: int, key: RsaKeyPair) -> int:
    """Sign a small integer representative with the toy private exponent.

    This exposes the RSA verification equation for teaching only.  It is not a
    signature scheme: it has no hash-to-signature encoding, padding, key-size
    requirements, or side-channel protection.
    """
    if not 0 <= representative < key.modulus:
        raise ValueError("teaching representative must be in [0, n)")
    return mod_pow(representative, key.private_exponent, key.modulus)


def toy_rsa_verify(representative: int, signature: int, key: RsaKeyPair) -> bool:
    """Verify s**e == representative mod n for the teaching key pair."""
    if not 0 <= representative < key.modulus or not 0 <= signature < key.modulus:
        return False
    return mod_pow(signature, key.public_exponent, key.modulus) == representative


if __name__ == "__main__":
    key = toy_rsa_keypair(61, 53, 17)
    message = 65
    ciphertext = encrypt(message, key)
    print(f"n={key.modulus}, e={key.public_exponent}, d={key.private_exponent}")
    print(f"明文={message}, 密文={ciphertext}, 解密={decrypt(ciphertext, key)}")
