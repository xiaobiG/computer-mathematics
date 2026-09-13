"""Reproducible two-sample permutation tests for teaching, not product decisions."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
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


@dataclass(frozen=True)
class ExactPermutationTestResult:
    """An exhaustive conditional permutation result for a small fixed table."""

    observed_difference: float
    p_value: float
    extreme_assignments: int
    total_assignments: int


def _validated_observations(control: list[float], treatment: list[float]) -> tuple[list[float], int, float]:
    if not isinstance(control, list) or not isinstance(treatment, list) or not control or not treatment:
        raise ValueError("control and treatment must be non-empty lists")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)
           for value in control + treatment):
        raise ValueError("observations must be finite")
    pooled = [float(value) for value in control + treatment]
    control_size = len(control)
    return pooled, control_size, fmean(treatment) - fmean(control)


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
    pooled, control_size, observed = _validated_observations(control, treatment)
    rng = Random(seed)
    extreme = 0
    for _ in range(rounds):
        shuffled = pooled.copy()
        rng.shuffle(shuffled)
        simulated = fmean(shuffled[control_size:]) - fmean(shuffled[:control_size])
        if abs(simulated) >= abs(observed):
            extreme += 1
    return PermutationTestResult(observed, (extreme + 1) / (rounds + 1), extreme, rounds, seed)


def exact_two_sided_permutation_test(
    control: list[float], treatment: list[float], *, max_assignments: int = 50_000,
) -> ExactPermutationTestResult:
    """Enumerate every fixed-size label assignment for a deliberately small sample.

    Unlike Monte-Carlo shuffling, this conditional p-value has no seed or
    sampling variation.  The explicit cap keeps the teaching helper from
    quietly pretending exhaustive enumeration is practical for real A/B data.
    """
    if (isinstance(max_assignments, bool) or not isinstance(max_assignments, int)
            or max_assignments <= 0):
        raise ValueError("max_assignments must be a positive integer")
    pooled, control_size, observed = _validated_observations(control, treatment)
    total_assignments = 0
    extreme = 0
    all_indices = set(range(len(pooled)))
    for control_indices_tuple in combinations(range(len(pooled)), control_size):
        total_assignments += 1
        if total_assignments > max_assignments:
            raise ValueError("exact permutation enumeration exceeds max_assignments")
        control_indices = set(control_indices_tuple)
        simulated_control = [pooled[index] for index in control_indices]
        simulated_treatment = [pooled[index] for index in all_indices - control_indices]
        simulated = fmean(simulated_treatment) - fmean(simulated_control)
        if abs(simulated) >= abs(observed):
            extreme += 1
    return ExactPermutationTestResult(
        observed, extreme / total_assignments, extreme, total_assignments,
    )


def exact_permutation_test_certificate(
    control: list[float], treatment: list[float], report: object,
) -> bool:
    """Replay a small exhaustive report and reject altered counts or p-values."""
    if not isinstance(report, ExactPermutationTestResult):
        return False
    try:
        expected = exact_two_sided_permutation_test(
            control, treatment, max_assignments=report.total_assignments,
        )
    except (TypeError, ValueError):
        return False
    return report == expected


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
