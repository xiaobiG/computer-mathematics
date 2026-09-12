"""Reproducible two-sample permutation tests for teaching, not product decisions."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from statistics import fmean


@dataclass(frozen=True)
class PermutationTestResult:
    observed_difference: float
    p_value: float
    extreme_permutations: int
    rounds: int


def two_sided_permutation_test(
    control: list[float], treatment: list[float], *, rounds: int = 10_000, seed: int = 0
) -> PermutationTestResult:
    """Estimate P(|T*| >= |T_obs|) under exchangeable group labels.

    The +1 correction includes the observed allocation conceptually and avoids
    reporting a Monte-Carlo p-value of exactly zero.
    """
    if not control or not treatment or rounds <= 0:
        raise ValueError("control, treatment and a positive round count are required")
    observed = fmean(treatment) - fmean(control)
    pooled = [float(value) for value in control + treatment]
    if any(value != value or value in (float("inf"), float("-inf")) for value in pooled):
        raise ValueError("observations must be finite")
    rng = Random(seed)
    control_size = len(control)
    extreme = 0
    for _ in range(rounds):
        shuffled = pooled.copy()
        rng.shuffle(shuffled)
        simulated = fmean(shuffled[control_size:]) - fmean(shuffled[:control_size])
        if abs(simulated) >= abs(observed):
            extreme += 1
    return PermutationTestResult(observed, (extreme + 1) / (rounds + 1), extreme, rounds)
