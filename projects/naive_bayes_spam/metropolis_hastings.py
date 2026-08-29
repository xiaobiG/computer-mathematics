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


def empirical_probabilities(samples: list[State]) -> dict[State, float]:
    """Return observed state frequencies; burn-in/thinning decisions stay explicit."""
    if not samples:
        raise ValueError("samples must not be empty")
    return {state: samples.count(state) / len(samples) for state in set(samples)}
