"""Reproducible two-sample permutation tests for teaching, not product decisions."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random
from statistics import fmean


@dataclass(frozen=True)
class PermutationTestResult:
    observed_difference: float
    p_value: float
    extreme_permutations: int
    rounds: int
    seed: int


def two_sided_permutation_test(
    control: list[float], treatment: list[float], *, rounds: int = 10_000, seed: int = 0
) -> PermutationTestResult:
    """Estimate P(|T*| >= |T_obs|) under exchangeable group labels.

    The +1 correction includes the observed allocation conceptually and avoids
    reporting a Monte-Carlo p-value of exactly zero.
    """
    if (isinstance(rounds, bool) or not isinstance(rounds, int) or rounds <= 0
            or isinstance(seed, bool) or not isinstance(seed, int)):
        raise ValueError("control, treatment and a positive round count are required")
    if not isinstance(control, list) or not isinstance(treatment, list) or not control or not treatment:
        raise ValueError("control and treatment must be non-empty lists")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)
           for value in control + treatment):
        raise ValueError("observations must be finite")
    pooled = [float(value) for value in control + treatment]
    observed = fmean(treatment) - fmean(control)
    rng = Random(seed)
    control_size = len(control)
    extreme = 0
    for _ in range(rounds):
        shuffled = pooled.copy()
        rng.shuffle(shuffled)
        simulated = fmean(shuffled[control_size:]) - fmean(shuffled[:control_size])
        if abs(simulated) >= abs(observed):
            extreme += 1
    return PermutationTestResult(observed, (extreme + 1) / (rounds + 1), extreme, rounds, seed)


def permutation_test_certificate(control: list[float], treatment: list[float], report: object) -> bool:
    """Replay a reported fixed-seed Monte-Carlo p-value and reject changes.

    This proves that the statistic, extreme-count correction and reported
    p-value come from the declared rows, rounds and seed.  It deliberately
    cannot prove the null hypothesis, label exchangeability, independence or
    that the analysis plan was fixed before observing the data.
    """
    if not isinstance(report, PermutationTestResult):
        return False
    try:
        expected = two_sided_permutation_test(
            control, treatment, rounds=report.rounds, seed=report.seed,
        )
    except (TypeError, ValueError):
        return False
    return report == expected
