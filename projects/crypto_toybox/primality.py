"""Auditable Miller--Rabin rounds for classroom-sized integer examples only."""

from __future__ import annotations

from dataclasses import dataclass

from projects.crypto_toybox.main import mod_pow


def _require_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")


def decompose_power_of_two(value: int) -> tuple[int, int]:
    """Return s,d with positive even ``value == 2**s * d`` and odd d."""
    _require_integer(value, "value")
    if value <= 0 or value % 2:
        raise ValueError("value must be a positive even integer")
    twos = 0
    odd_part = value
    while odd_part % 2 == 0:
        twos += 1
        odd_part //= 2
    return twos, odd_part


@dataclass(frozen=True)
class MillerRabinRound:
    base: int
    twos: int
    odd_part: int
    square_chain: tuple[int, ...]
    passes: bool


def miller_rabin_round(candidate: int, base: int) -> MillerRabinRound:
    """Run one odd-candidate Miller--Rabin round and retain its square chain."""
    _require_integer(candidate, "candidate")
    _require_integer(base, "base")
    if candidate <= 3 or candidate % 2 == 0:
        raise ValueError("candidate must be an odd integer greater than three")
    if not 2 <= base <= candidate - 2:
        raise ValueError("base must lie in [2, candidate - 2]")
    twos, odd_part = decompose_power_of_two(candidate - 1)
    values = [mod_pow(base, odd_part, candidate)]
    for _ in range(twos - 1):
        values.append((values[-1] * values[-1]) % candidate)
    passes = values[0] == 1 or candidate - 1 in values
    return MillerRabinRound(base, twos, odd_part, tuple(values), passes)


def miller_rabin_round_certificate(candidate: int, event: MillerRabinRound) -> bool:
    """Recompute a recorded round, including every square-chain transition."""
    try:
        expected = miller_rabin_round(candidate, event.base)
    except (ValueError, AttributeError):
        return False
    return event == expected


def miller_rabin_report(candidate: int, bases: list[int] | tuple[int, ...]) -> dict[str, object]:
    """Audit explicit bases; ``probably_prime`` never claims a primality proof.

    The caller supplies bases deliberately.  Selecting random bases or choosing
    production security parameters is out of scope for this teaching module.
    """
    _require_integer(candidate, "candidate")
    if candidate in (2, 3):
        return {"probably_prime": True, "rounds": [], "witnesses": [], "certificate": {"valid": True}}
    if candidate < 2 or candidate % 2 == 0:
        return {"probably_prime": False, "rounds": [], "witnesses": [], "certificate": {"valid": True}}
    if not isinstance(bases, (list, tuple)) or not bases:
        raise ValueError("provide at least one explicit Miller-Rabin base")
    rounds = [miller_rabin_round(candidate, base) for base in bases]
    witnesses = [round_.base for round_ in rounds if not round_.passes]
    return {
        "probably_prime": not witnesses,
        "rounds": rounds,
        "witnesses": witnesses,
        "certificate": {
            "all_rounds_replay": all(miller_rabin_round_certificate(candidate, round_) for round_ in rounds),
            "witnesses_prove_composite": bool(witnesses),
            "valid": all(miller_rabin_round_certificate(candidate, round_) for round_ in rounds),
        },
    }
