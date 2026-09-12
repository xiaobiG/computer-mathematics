"""Auditable binary Bayes updates for small teaching examples."""

from __future__ import annotations

from dataclasses import dataclass


CORRELATED_EVIDENCE_CONTRACT_VERSION = "correlated-evidence-comparison/v1"


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


def posterior_trace_respects_model(
    prior: float,
    observations: list[tuple[float, float]],
    final: float,
    updates: list[BayesUpdate],
    *,
    tolerance: float = 1e-12,
) -> bool:
    """Independently replay a sequential Bayes trace as a teaching certificate.

    This verifies every stored prior, normalising evidence and posterior against
    the supplied conditionally independent observation model.  It does not
    prove that the observations are actually conditionally independent in the
    real world; that is an assumption outside a finite execution trace.
    """
    try:
        _probability(prior, "prior")
        _probability(final, "final")
        if tolerance < 0.0:
            return False
        if len(observations) != len(updates):
            return False
        current = prior
        for (likelihood_if_event, likelihood_if_not_event), update in zip(observations, updates):
            _probability(likelihood_if_event, "likelihood_if_event")
            _probability(likelihood_if_not_event, "likelihood_if_not_event")
            evidence = likelihood_if_event * current + likelihood_if_not_event * (1.0 - current)
            if evidence == 0.0:
                return False
            expected_posterior = likelihood_if_event * current / evidence
            fields = (
                (update.prior, current),
                (update.likelihood_if_event, likelihood_if_event),
                (update.likelihood_if_not_event, likelihood_if_not_event),
                (update.evidence, evidence),
                (update.posterior, expected_posterior),
            )
            if any(abs(actual - expected) > tolerance for actual, expected in fields):
                return False
            current = expected_posterior
        return abs(final - current) <= tolerance
    except (TypeError, ValueError):
        return False


def _likelihood_pair(value: object, name: str) -> tuple[float, float]:
    """Validate a ``(P(E|A), P(E|not A))`` teaching-model pair."""
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError(f"{name} must be a pair of probabilities")
    event, not_event = value
    if not isinstance(event, (int, float)) or not isinstance(not_event, (int, float)):
        raise ValueError(f"{name} must contain numeric probabilities")
    event = float(event)
    not_event = float(not_event)
    _probability(event, f"{name}[0]")
    _probability(not_event, f"{name}[1]")
    return event, not_event


def _update_dict(update: BayesUpdate) -> dict[str, float]:
    return {
        "prior": update.prior,
        "likelihood_if_event": update.likelihood_if_event,
        "likelihood_if_not_event": update.likelihood_if_not_event,
        "evidence": update.evidence,
        "posterior": update.posterior,
    }


def correlated_evidence_comparison_report(
    prior: float,
    observations: list[tuple[float, float]],
    joint_likelihood: tuple[float, float],
) -> dict[str, object]:
    """Compare an independence calculation with an explicit two-evidence model.

    ``observations`` supplies the two marginal likelihood pairs for ``E1`` and
    ``E2``.  ``joint_likelihood`` supplies ``P(E1 and E2|A)`` and
    ``P(E1 and E2|not A)`` from a model that permits dependence.  The function
    does *not* infer correlation from a trace: it makes the two competing
    assumptions visible, checks that the supplied joint probabilities are
    compatible with the marginals, and reports their distinct posteriors.
    """
    _probability(prior, "prior")
    if len(observations) != 2:
        raise ValueError("comparison requires exactly two evidence observations")
    first = _likelihood_pair(observations[0], "observations[0]")
    second = _likelihood_pair(observations[1], "observations[1]")
    joint = _likelihood_pair(joint_likelihood, "joint_likelihood")
    for index, hypothesis in enumerate(("event", "not_event")):
        if joint[index] > min(first[index], second[index]):
            raise ValueError(f"joint_likelihood for {hypothesis} cannot exceed either marginal likelihood")

    independent_final, trace = posterior_trace(prior, [first, second])
    independent_joint = (first[0] * second[0], first[1] * second[1])
    joint_update = posterior(prior, *joint)
    return {
        "contract_version": CORRELATED_EVIDENCE_CONTRACT_VERSION,
        "prior": float(prior),
        "marginal_likelihoods": [
            {"event": first[0], "not_event": first[1]},
            {"event": second[0], "not_event": second[1]},
        ],
        "independence_model": {
            "joint_likelihood": {"event": independent_joint[0], "not_event": independent_joint[1]},
            "trace": [_update_dict(update) for update in trace],
            "posterior": independent_final,
        },
        "joint_model": {
            "joint_likelihood": {"event": joint[0], "not_event": joint[1]},
            "evidence": joint_update.evidence,
            "posterior": joint_update.posterior,
        },
        "posterior_gap": independent_final - joint_update.posterior,
        "interpretation": "model_comparison_only",
    }


def correlated_evidence_comparison_certificate(
    prior: float,
    observations: list[tuple[float, float]],
    joint_likelihood: tuple[float, float],
    report: object,
) -> bool:
    """Replay a two-evidence comparison and reject altered assumptions or output.

    A valid certificate says only that a report follows the explicitly supplied
    independence and joint models.  It cannot determine which model generated
    a real data set, nor does it establish a causal relationship between
    features.
    """
    if not isinstance(report, dict):
        return False
    try:
        expected = correlated_evidence_comparison_report(prior, observations, joint_likelihood)
    except (TypeError, ValueError):
        return False
    return report == expected
