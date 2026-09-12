"""Tiny Diffie--Hellman transcripts for algebra lessons; never protocol code."""

from __future__ import annotations

from dataclasses import dataclass

from projects.crypto_toybox.finite_group import is_prime, multiplicative_order


def _validate_parameters(generator: int, prime: int, private: int) -> None:
    if not is_prime(prime) or not 1 < generator < prime or not 0 < private < prime - 1:
        raise ValueError("use a tiny prime modulus, nontrivial generator, and private exponent in range")


def dh_public(generator: int, private: int, prime: int) -> int:
    """Return g^private mod p in a deliberately tiny prime-field example."""
    _validate_parameters(generator, prime, private)
    return pow(generator, private, prime)


def dh_shared(peer_public: int, private: int, prime: int) -> int:
    """Compute a raw teaching shared element after only a minimal range check.

    Real DH requires standard parameters, subgroup/point validation, a KDF,
    authenticated transcript binding and constant-time implementations.
    """
    if not is_prime(prime) or not 0 < private < prime - 1 or not 1 < peer_public < prime - 1:
        raise ValueError("private and peer public values are outside this teaching contract")
    return pow(peer_public, private, prime)


@dataclass(frozen=True)
class HonestExchange:
    alice_public: int
    bob_public: int
    alice_shared: int
    bob_shared: int


def honest_exchange(generator: int, prime: int, alice_private: int, bob_private: int) -> HonestExchange:
    """Expose B^a=A^b in a small group for a directly testable transcript."""
    alice_public = dh_public(generator, alice_private, prime)
    bob_public = dh_public(generator, bob_private, prime)
    return HonestExchange(
        alice_public,
        bob_public,
        dh_shared(bob_public, alice_private, prime),
        dh_shared(alice_public, bob_private, prime),
    )


def honest_exchange_certificate(
    generator: int, prime: int, alice_private: int, bob_private: int, exchange: HonestExchange,
) -> dict[str, bool]:
    """Replay a classroom DH transcript rather than trusting its shared value."""
    empty = {
        "public_values_match_exponents": False,
        "alice_shared_matches_bob_public": False,
        "bob_shared_matches_alice_public": False,
        "shared_elements_agree": False,
        "valid": False,
    }
    try:
        if not isinstance(exchange, HonestExchange):
            return empty
        expected_alice_public = dh_public(generator, alice_private, prime)
        expected_bob_public = dh_public(generator, bob_private, prime)
        public_values_match = (exchange.alice_public == expected_alice_public
                               and exchange.bob_public == expected_bob_public)
        alice_shared_matches = exchange.alice_shared == dh_shared(exchange.bob_public, alice_private, prime)
        bob_shared_matches = exchange.bob_shared == dh_shared(exchange.alice_public, bob_private, prime)
        shared_agree = exchange.alice_shared == exchange.bob_shared
        return {
            "public_values_match_exponents": public_values_match,
            "alice_shared_matches_bob_public": alice_shared_matches,
            "bob_shared_matches_alice_public": bob_shared_matches,
            "shared_elements_agree": shared_agree,
            "valid": public_values_match and alice_shared_matches and bob_shared_matches and shared_agree,
        }
    except (TypeError, ValueError):
        return empty


@dataclass(frozen=True)
class MitmExchange:
    alice_shared_with_mallory: int
    bob_shared_with_mallory: int
    mallory_with_alice: int
    mallory_with_bob: int


def mitm_exchange(generator: int, prime: int, alice_private: int, bob_private: int, mallory_to_alice: int, mallory_to_bob: int) -> MitmExchange:
    """Show two matching attacker sessions, not a secure-message implementation."""
    honest = honest_exchange(generator, prime, alice_private, bob_private)
    replacement_for_alice = dh_public(generator, mallory_to_alice, prime)
    replacement_for_bob = dh_public(generator, mallory_to_bob, prime)
    return MitmExchange(
        dh_shared(replacement_for_alice, alice_private, prime),
        dh_shared(replacement_for_bob, bob_private, prime),
        dh_shared(honest.alice_public, mallory_to_alice, prime),
        dh_shared(honest.bob_public, mallory_to_bob, prime),
    )


def mitm_exchange_certificate(
    generator: int, prime: int, alice_private: int, bob_private: int,
    mallory_to_alice: int, mallory_to_bob: int, exchange: MitmExchange,
) -> dict[str, bool]:
    """Replay the two substituted DH sessions and expose their identity failure."""
    empty = {
        "alice_session_matches_mallory": False,
        "bob_session_matches_mallory": False,
        "endpoints_lack_one_common_session": False,
        "valid": False,
    }
    try:
        if not isinstance(exchange, MitmExchange):
            return empty
        expected = mitm_exchange(
            generator, prime, alice_private, bob_private, mallory_to_alice, mallory_to_bob,
        )
        alice_session = (exchange.alice_shared_with_mallory == expected.alice_shared_with_mallory
                         and exchange.mallory_with_alice == expected.mallory_with_alice
                         and exchange.alice_shared_with_mallory == exchange.mallory_with_alice)
        bob_session = (exchange.bob_shared_with_mallory == expected.bob_shared_with_mallory
                       and exchange.mallory_with_bob == expected.mallory_with_bob
                       and exchange.bob_shared_with_mallory == exchange.mallory_with_bob)
        endpoints_differ = exchange.alice_shared_with_mallory != exchange.bob_shared_with_mallory
        return {
            "alice_session_matches_mallory": alice_session,
            "bob_session_matches_mallory": bob_session,
            "endpoints_lack_one_common_session": endpoints_differ,
            "valid": alice_session and bob_session and endpoints_differ,
        }
    except (TypeError, ValueError):
        return empty


def generator_order(generator: int, prime: int) -> int:
    """Expose group order only to make the tiny-parameter warning testable."""
    return multiplicative_order(generator, prime)
