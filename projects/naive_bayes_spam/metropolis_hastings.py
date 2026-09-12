"""Finite-state Metropolis--Hastings with an auditable acceptance trace."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Hashable


State = Hashable


@dataclass(frozen=True)
class McmcEvent:
    previous: State
    proposed: State
    current: State
    accepted: bool
    acceptance_probability: float


def _validate(target: dict[State, float], proposal: dict[State, dict[State, float]]) -> None:
    if not target or set(target) != set(proposal) or any(weight <= 0 for weight in target.values()):
        raise ValueError("target and proposal need the same nonempty states and positive target weights")
    for state, probabilities in proposal.items():
        if not probabilities or any(candidate not in target or chance <= 0 for candidate, chance in probabilities.items()):
            raise ValueError("proposal transitions must target known states with positive probabilities")
        if abs(sum(probabilities.values()) - 1.0) > 1e-12:
            raise ValueError("each proposal row must sum to one")
        if any(state not in proposal[candidate] for candidate in probabilities):
            raise ValueError("every proposal edge needs a reverse probability for MH correction")


def metropolis_hastings(
    target: dict[State, float], proposal: dict[State, dict[State, float]], initial: State, *, steps: int, seed: int = 0
) -> tuple[list[State], list[McmcEvent]]:
    """Sample target weights with MH; return post-transition states and diagnostics.

    Target weights may be unnormalised.  Unlike a simplified random-walk demo,
    the acceptance ratio includes q(current | proposed) / q(proposed | current),
    so an asymmetric proposal still targets the intended distribution.
    """
    _validate(target, proposal)
    if initial not in target or steps <= 0:
        raise ValueError("initial must be a target state and steps must be positive")
    rng, current = Random(seed), initial
    samples: list[State] = []
    trace: list[McmcEvent] = []
    for _ in range(steps):
        choices, probabilities = zip(*proposal[current].items())
        proposed = rng.choices(choices, weights=probabilities, k=1)[0]
        ratio = target[proposed] * proposal[proposed][current] / (target[current] * proposal[current][proposed])
        acceptance_probability = min(1.0, ratio)
        previous = current
        accepted = rng.random() < acceptance_probability
        if accepted:
            current = proposed
        trace.append(McmcEvent(previous, proposed, current, accepted, acceptance_probability))
        samples.append(current)
    return samples, trace


def metropolis_hastings_trace_certificate(
    target: dict[State, float], proposal: dict[State, dict[State, float]], initial: State,
    samples: list[State], trace: list[McmcEvent], *, seed: int = 0,
) -> bool:
    """Replay an MH run from its public seed and verify every recorded update.

    The verifier intentionally reproduces both pseudorandom draws, then checks
    the asymmetric Hastings correction before comparing the full event. It is
    a reproducibility certificate for a finite classroom run, not evidence
    that the chain has mixed or that its Monte Carlo estimate is accurate.
    """
    try:
        _validate(target, proposal)
        if initial not in target or len(samples) != len(trace) or not isinstance(seed, int):
            return False
        rng, current = Random(seed), initial
        for sample, event in zip(samples, trace):
            choices, probabilities = zip(*proposal[current].items())
            proposed = rng.choices(choices, weights=probabilities, k=1)[0]
            ratio = target[proposed] * proposal[proposed][current] / (target[current] * proposal[current][proposed])
            acceptance_probability = min(1.0, ratio)
            previous = current
            accepted = rng.random() < acceptance_probability
            if accepted:
                current = proposed
            expected = McmcEvent(previous, proposed, current, accepted, acceptance_probability)
            if event != expected or sample != current:
                return False
        return True
    except (ArithmeticError, TypeError, ValueError):
        return False


def _transition_kernel(
    target: dict[State, float], proposal: dict[State, dict[State, float]]
) -> dict[State, dict[State, float]]:
    """Build the exact finite-state MH transition matrix, including rejection."""
    kernel = {state: {candidate: 0.0 for candidate in target} for state in target}
    for current, candidates in proposal.items():
        for proposed, proposal_probability in candidates.items():
            ratio = target[proposed] * proposal[proposed][current] / (
                target[current] * proposal[current][proposed]
            )
            acceptance = min(1.0, ratio)
            if proposed == current:
                kernel[current][current] += proposal_probability
            else:
                kernel[current][proposed] += proposal_probability * acceptance
                kernel[current][current] += proposal_probability * (1.0 - acceptance)
    return kernel


def detailed_balance_report(
    target: dict[State, float], proposal: dict[State, dict[State, float]]
) -> dict[str, object]:
    """Expose a finite MH kernel and all detailed-balance flow checks.

    This is practical only for the deliberately small classroom state spaces.
    It verifies stationarity of the *kernel*, not the mixing time of a sampled
    trajectory.
    """
    _validate(target, proposal)
    total_weight = sum(target.values())
    normalized_target = {state: weight / total_weight for state, weight in target.items()}
    kernel = _transition_kernel(target, proposal)
    row_sums = {state: sum(row.values()) for state, row in kernel.items()}
    flows = {
        (left, right): normalized_target[left] * kernel[left][right]
        for left in target for right in target
    }
    detailed_balance = all(
        abs(flows[left, right] - flows[right, left]) <= 1e-12
        for left in target for right in target
    )
    report: dict[str, object] = {
        "normalized_target": normalized_target,
        "kernel": kernel,
        "row_sums": row_sums,
        "detailed_balance_holds": detailed_balance,
    }
    report["certificate"] = detailed_balance_certificate(target, proposal, report)
    return report


def detailed_balance_certificate(
    target: dict[State, float], proposal: dict[State, dict[State, float]], report: dict[str, object]
) -> dict[str, bool]:
    """Recompute a finite detailed-balance report and reject edited fields."""
    try:
        _validate(target, proposal)
        total_weight = sum(target.values())
        expected_target = {state: weight / total_weight for state, weight in target.items()}
        expected_kernel = _transition_kernel(target, proposal)
        expected_rows = {state: sum(row.values()) for state, row in expected_kernel.items()}
        fields_match = (
            report.get("normalized_target") == expected_target
            and report.get("kernel") == expected_kernel
            and report.get("row_sums") == expected_rows
        )
        rows_are_stochastic = all(abs(value - 1.0) <= 1e-12 for value in expected_rows.values())
        flows_match = all(
            abs(
                expected_target[left] * expected_kernel[left][right]
                - expected_target[right] * expected_kernel[right][left]
            ) <= 1e-12
            for left in target for right in target
        )
        return {
            "fields_match_recomputed_kernel": fields_match,
            "rows_are_stochastic": fields_match and rows_are_stochastic,
            "detailed_balance_holds": fields_match and flows_match,
            "valid": fields_match and rows_are_stochastic and flows_match,
        }
    except (ArithmeticError, TypeError, ValueError):
        return {
            "fields_match_recomputed_kernel": False,
            "rows_are_stochastic": False,
            "detailed_balance_holds": False,
            "valid": False,
        }


def empirical_probabilities(samples: list[State]) -> dict[State, float]:
    """Return observed state frequencies; burn-in/thinning decisions stay explicit."""
    if not samples:
        raise ValueError("samples must not be empty")
    return {state: samples.count(state) / len(samples) for state in set(samples)}
