"""A fixed-hyperparameter, two-level Beta--Binomial partial-pooling audit."""

from __future__ import annotations

from math import isfinite


CONTRACT = "hierarchical-beta-binomial-partial-pooling/v1"


def _positive(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return float(value)


def _count(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _normalize_groups(groups: object) -> list[dict[str, object]]:
    if not isinstance(groups, list) or len(groups) < 2:
        raise ValueError("groups must contain at least two predefined groups")
    normalized: list[dict[str, object]] = []
    seen: set[str] = set()
    for group in groups:
        if not isinstance(group, dict) or set(group) != {"group_id", "successes", "failures"}:
            raise ValueError("each group has exactly group_id, successes, and failures")
        identifier = group["group_id"]
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("group_id values must be unique non-empty strings")
        successes, failures = _count(group["successes"], "successes"), _count(group["failures"], "failures")
        normalized.append({"group_id": identifier, "successes": successes, "failures": failures})
        seen.add(identifier)
    if not any(group["successes"] + group["failures"] for group in normalized):
        raise ValueError("at least one group must contain an observation")
    return normalized


def hierarchical_beta_binomial_report(groups: object, alpha: object, beta: object) -> dict[str, object]:
    """Update exchangeable group rates under a declared shared Beta prior.

    Hyperparameters are intentionally fixed inputs. This is partial pooling,
    not empirical-Bayes fitting or a proof that real groups are exchangeable.
    """
    alpha_value, beta_value = _positive(alpha, "alpha"), _positive(beta, "beta")
    rows = _normalize_groups(groups)
    prior_strength = alpha_value + beta_value
    prior_mean = alpha_value / prior_strength
    posterior_groups = []
    for row in rows:
        successes, failures = int(row["successes"]), int(row["failures"])
        observations = successes + failures
        posterior_alpha, posterior_beta = alpha_value + successes, beta_value + failures
        mle = successes / observations if observations else None
        data_weight = observations / (prior_strength + observations)
        posterior_mean = posterior_alpha / (posterior_alpha + posterior_beta)
        posterior_groups.append({
            "group_id": row["group_id"], "successes": successes, "failures": failures,
            "observations": observations, "mle": mle,
            "posterior": {"alpha": posterior_alpha, "beta": posterior_beta, "mean": posterior_mean},
            "partial_pooling": {
                "data_weight": data_weight, "prior_weight": 1 - data_weight,
                "weighted_mean_identity": data_weight * (mle if mle is not None else prior_mean) + (1 - data_weight) * prior_mean,
                "posterior_variance": (posterior_alpha * posterior_beta) /
                    ((posterior_alpha + posterior_beta) ** 2 * (posterior_alpha + posterior_beta + 1)),
            },
        })
    total_successes = sum(int(row["successes"]) for row in rows)
    total_observations = sum(int(row["successes"]) + int(row["failures"]) for row in rows)
    return {
        "contract": CONTRACT,
        "model": {
            "group_rate_prior": "independent_given_fixed_hyperparameters Beta(alpha, beta)",
            "alpha": alpha_value, "beta": beta_value,
            "prior_mean": prior_mean, "prior_strength": prior_strength,
            "hyperparameters": "declared_fixed_not_estimated_from_groups",
        },
        "groups": posterior_groups,
        "pooled_descriptive_rate": total_successes / total_observations,
        "total_observations": total_observations,
        "automatic_action": "none",
        "boundary": (
            "partial pooling follows only from the declared exchangeable Beta--Binomial model; it does not verify group "
            "exchangeability, fit hyperparameters, model time dependence, correct missing outcomes, or establish a causal effect"
        ),
    }


def hierarchical_beta_binomial_certificate(groups: object, alpha: object, beta: object, report: object) -> bool:
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        return report == hierarchical_beta_binomial_report(groups, alpha, beta)
    except (TypeError, ValueError):
        return False
