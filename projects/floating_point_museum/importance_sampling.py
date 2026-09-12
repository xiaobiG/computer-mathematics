"""Reproducible importance-sampling benchmark on a bounded one-dimensional integral."""
from __future__ import annotations

from math import sqrt
from random import Random


CONTRACT = "importance-sampling-x8/v1"
EXACT = 1.0 / 9.0


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
