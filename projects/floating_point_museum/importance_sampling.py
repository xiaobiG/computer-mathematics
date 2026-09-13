"""Reproducible importance-sampling benchmark on a bounded one-dimensional integral."""
from __future__ import annotations

from fractions import Fraction
from math import exp, isfinite, log, sqrt
from random import Random


CONTRACT = "importance-sampling-x8/v1"
EXACT = 1.0 / 9.0
LOG_WEIGHT_CONTRACT = "log-weight-diagnostics/v1"
ADAPTIVE_SPLIT_CONTRACT = "adaptive-importance-sampling-split/v1"


def _integer(value, name, minimum, maximum):
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
    return value


def _summary(values):
    estimate = sum(values) / len(values)
    variance = max(0.0, sum(value * value for value in values) / len(values) - estimate * estimate)
    return {"estimate": estimate, "absolute_error": abs(estimate - EXACT), "estimated_standard_error": sqrt(variance / len(values))}


def importance_sampling_report(samples, seed):
    """Compare uniform integration of x^8 with proposal q(x)=2x on [0,1]."""
    count, random_seed = _integer(samples, "samples", 2, 100_000), _integer(seed, "seed", 0, 2**31 - 1)
    rng = Random(random_seed)
    uniform_values = [rng.random() ** 8 for _ in range(count)]
    rng = Random(random_seed)
    # X=sqrt(U) has q(x)=2x; f(x)/q(x)=x^7/2 for x>0.
    weighted = []
    weights = []
    for _ in range(count):
        uniform_draw = rng.random()
        while uniform_draw == 0.0:
            uniform_draw = rng.random()
        x = sqrt(uniform_draw)
        weight = 1.0 / (2.0 * x)
        weights.append(weight)
        weighted.append(x ** 8 * weight)
    ess = sum(weights) ** 2 / sum(weight * weight for weight in weights)
    return {"contract": CONTRACT, "integral": "integral_0_1_x_to_8", "exact_value": EXACT, "proposal": "q(x)=2x on (0,1]", "samples": count, "seed": random_seed, "uniform": _summary(uniform_values), "importance": {**_summary(weighted), "effective_sample_size": ess, "max_normalized_weight": max(weights) / sum(weights)}, "interpretation": "fixed benchmark; ESS diagnoses this chosen proposal only and is not an error bound"}


def importance_sampling_certificate(samples, seed, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == importance_sampling_report(samples, seed)
    except ValueError:
        return False


def log_weight_diagnostics(log_weights):
    """Normalize finite log weights using a max shift, without estimating an integral.

    This exposes numerical weight concentration only.  It cannot demonstrate
    proposal support, finite variance, convergence, or a valid adaptive policy.
    """
    if not isinstance(log_weights, list) or len(log_weights) < 2:
        raise ValueError("log_weights must contain at least two values")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) for value in log_weights):
        raise ValueError("log_weights must be finite real values")
    values = [float(value) for value in log_weights]
    shift = max(values)
    shifted = [exp(value - shift) for value in values]
    normalizer = sum(shifted)
    normalized = [value / normalizer for value in shifted]
    ess = 1.0 / sum(value * value for value in normalized)
    return {
        "contract": LOG_WEIGHT_CONTRACT,
        "log_weight_shift": shift,
        "log_sum_weights": shift + log(normalizer),
        "normalized_weights": normalized,
        "effective_sample_size": ess,
        "max_normalized_weight": max(normalized),
        "interpretation": "floating_point_weight_diagnostic_only; not_an_error_bound_or_proposal_validation",
    }


def log_weight_diagnostics_certificate(log_weights, report):
    """Recompute stable log-weight diagnostics and reject altered fields."""
    if not isinstance(report, dict):
        return False
    try:
        return report == log_weight_diagnostics(log_weights)
    except ValueError:
        return False


def _draw_discrete(proposal, rng):
    """Draw one of the two declared support points from a finite proposal."""
    return 0 if rng.random() < proposal[0] else 1


def _single_sample_estimate(contributions, proposal, point):
    return contributions[point] / proposal[point]


def _adaptive_split_expectations(contributions, proposals):
    """Exactly enumerate the two pilot draws and the independent estimate draw.

    The deliberately bad selection policy chooses the larger one-sample pilot
    estimate.  Enumeration makes its selection bias visible without claiming
    anything from one pseudorandom seed.
    """
    exact_contributions = [Fraction(str(value)) for value in contributions]
    target = sum(exact_contributions)
    reuse_expectation = Fraction(0)
    split_expectation = Fraction(0)
    for first_point, first_probability in enumerate(proposals[0]["probabilities"]):
        first_probability = Fraction(str(first_probability))
        first_estimate = exact_contributions[first_point] / Fraction(str(proposals[0]["probabilities"][first_point]))
        for second_point, second_probability in enumerate(proposals[1]["probabilities"]):
            second_probability = Fraction(str(second_probability))
            second_estimate = exact_contributions[second_point] / Fraction(str(proposals[1]["probabilities"][second_point]))
            selected_index = 0 if first_estimate >= second_estimate else 1
            selected = proposals[selected_index]["probabilities"]
            joint_probability = first_probability * second_probability
            reuse_expectation += joint_probability * (first_estimate if selected_index == 0 else second_estimate)
            for estimate_point, estimate_probability in enumerate(selected):
                split_expectimation_probability = Fraction(str(estimate_probability))
                split_expectation += joint_probability * split_expectimation_probability * (
                    exact_contributions[estimate_point] / split_expectimation_probability
                )
    return {
        "target": float(target),
        "reused_pilot_expectation": float(reuse_expectation),
        "split_estimate_expectation": float(split_expectation),
    }


def adaptive_importance_sampling_split_report(seed):
    """Show why an adaptive pilot must be separated from its final estimate.

    This is a finite two-point teaching construction, not an adaptive sampler.
    It compares two valid proposals for the same target sum.  A deliberately
    invalid policy selects the larger noisy pilot estimate; reusing that pilot
    is selected upward, whereas a fresh draw from the selected proposal has
    the target expectation conditional on every pilot outcome.
    """
    random_seed = _integer(seed, "seed", 0, 2**31 - 1)
    support = ["low", "high"]
    contributions = [0.2, 0.8]
    proposals = [
        {"name": "uniform", "probabilities": [0.5, 0.5]},
        {"name": "tilted_to_low", "probabilities": [0.8, 0.2]},
    ]
    rng = Random(random_seed)
    pilots = []
    for proposal in proposals:
        point = _draw_discrete(proposal["probabilities"], rng)
        pilots.append({
            "proposal": proposal["name"],
            "point": support[point],
            "proposal_probability": proposal["probabilities"][point],
            "pilot_estimate": _single_sample_estimate(contributions, proposal["probabilities"], point),
        })
    selected_index = 0 if pilots[0]["pilot_estimate"] >= pilots[1]["pilot_estimate"] else 1
    selected = proposals[selected_index]
    estimate_point = _draw_discrete(selected["probabilities"], rng)
    expectations = _adaptive_split_expectations(contributions, proposals)
    return {
        "contract": ADAPTIVE_SPLIT_CONTRACT,
        "target": {"support": support, "contributions": contributions, "exact_sum": expectations["target"]},
        "proposals": proposals,
        "seed": random_seed,
        "pilot_batch": pilots,
        "selection_rule": "choose_larger_single_pilot_estimate_tie_to_uniform",
        "selected_proposal": selected["name"],
        "unsafe_reused_pilot_estimate": pilots[selected_index]["pilot_estimate"],
        "independent_estimation_batch": {
            "point": support[estimate_point],
            "proposal_probability": selected["probabilities"][estimate_point],
            "estimate": _single_sample_estimate(contributions, selected["probabilities"], estimate_point),
        },
        "exact_policy_analysis": {
            **expectations,
            "reused_pilot_is_upward_selected": expectations["reused_pilot_expectation"] > expectations["target"],
            "split_expectation_matches_target": expectations["split_estimate_expectation"] == expectations["target"],
        },
        "interpretation": (
            "finite_two_point_selection_example; the pilot selects a proposal but is not final-estimate evidence; "
            "a fresh draw is conditionally unbiased for the declared target under either selected proposal"
        ),
        "boundary": (
            "not_a_general_adaptive_importance_sampler_or_unbiasedness_proof; does_not_establish_convergence, "
            "tail_conditions, support_checks_beyond_declared_finite_proposals, or_validity_of_this_selection_rule"
        ),
    }


def adaptive_importance_sampling_split_certificate(seed, report):
    """Replay every pilot, selection and independent draw in the teaching trace."""
    if not isinstance(report, dict):
        return False
    try:
        return report == adaptive_importance_sampling_split_report(seed)
    except ValueError:
        return False
