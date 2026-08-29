"""Auditable binary Bayes updates for small teaching examples."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BayesUpdate:
    """One evidence observation, including the normalising evidence probability."""

    prior: float
    likelihood_if_event: float
    likelihood_if_not_event: float
    evidence: float
    posterior: float


def _probability(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]")


def posterior(prior: float, likelihood_if_event: float, likelihood_if_not_event: float) -> BayesUpdate:
    """Apply P(A|E)=P(E|A)P(A)/P(E) for one binary observation."""
    _probability(prior, "prior")
    _probability(likelihood_if_event, "likelihood_if_event")
    _probability(likelihood_if_not_event, "likelihood_if_not_event")
    evidence = likelihood_if_event * prior + likelihood_if_not_event * (1.0 - prior)
    if evidence == 0.0:
        raise ValueError("evidence has zero probability under both hypotheses")
    return BayesUpdate(
        prior,
        likelihood_if_event,
        likelihood_if_not_event,
        evidence,
        likelihood_if_event * prior / evidence,
    )


def posterior_trace(prior: float, observations: list[tuple[float, float]]) -> tuple[float, list[BayesUpdate]]:
    """Sequentially update conditionally independent binary evidence.

    Each pair is ``(P(E_i|A), P(E_i|not A))``.  Reusing the previous
    posterior is valid only under the stated conditional-independence model.
    """
    updates: list[BayesUpdate] = []
    current = prior
    for likelihood_if_event, likelihood_if_not_event in observations:
        update = posterior(current, likelihood_if_event, likelihood_if_not_event)
        updates.append(update)
        current = update.posterior
    return current, updates
