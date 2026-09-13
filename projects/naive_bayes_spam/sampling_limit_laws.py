"""Reproducible diagnostics for sample-mean concentration and normal approximation."""

from __future__ import annotations

from math import isfinite, sqrt
from random import Random


def _validate(probability: float, sample_size: int, trials: int) -> None:
    if not isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError("probability must be finite and strictly between zero and one")
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 1 for value in (sample_size, trials)):
        raise ValueError("sample_size and trials must be integers greater than one")


def _normal_coverage_inputs(
    true_mean: object, standard_deviation: object, sample_size: object,
    trials: object, seed: object, z_value: object,
) -> tuple[float, float, int, int, int, float]:
    if (isinstance(true_mean, bool) or not isinstance(true_mean, (int, float))
            or not isfinite(true_mean)):
        raise ValueError("true_mean must be finite")
    if (isinstance(standard_deviation, bool) or not isinstance(standard_deviation, (int, float))
            or not isfinite(standard_deviation) or standard_deviation <= 0):
        raise ValueError("standard_deviation must be finite and positive")
    if (any(not isinstance(value, int) or isinstance(value, bool) or value <= 1
            for value in (sample_size, trials))):
        raise ValueError("sample_size and trials must be integers greater than one")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    if (isinstance(z_value, bool) or not isinstance(z_value, (int, float))
            or not isfinite(z_value) or z_value <= 0):
        raise ValueError("z_value must be finite and positive")
    return (
        float(true_mean), float(standard_deviation), sample_size, trials,
        seed, float(z_value),
    )


def normal_mean_coverage_report(
    true_mean: float = 10.0, standard_deviation: float = 4.0,
    sample_size: int = 80, trials: int = 1000, seed: int = 7, z_value: float = 1.96,
) -> dict[str, float | int | dict[str, bool]]:
    """Replay a finite normal-mean coverage experiment with sample SD intervals.

    This fixed-seed simulation illustrates the long-run interpretation of an
    interval rule.  It does not prove nominal coverage outside the declared
    normal, independent-observation classroom model.
    """
    mean, deviation, size, repetitions, random_seed, z = _normal_coverage_inputs(
        true_mean, standard_deviation, sample_size, trials, seed, z_value,
    )
    rng, covered, total_width = Random(random_seed), 0, 0.0
    for _ in range(repetitions):
        sample = [rng.gauss(mean, deviation) for _ in range(size)]
        sample_mean = sum(sample) / size
        sample_deviation = sqrt(sum((value - sample_mean) ** 2 for value in sample) / (size - 1))
        margin = z * sample_deviation / sqrt(size)
        covered += sample_mean - margin <= mean <= sample_mean + margin
        total_width += 2 * margin
    coverage = covered / repetitions
    return {
        "true_mean": mean,
        "standard_deviation": deviation,
        "sample_size": size,
        "trials": repetitions,
        "seed": random_seed,
        "z_value": z,
        "covered_intervals": covered,
        "normal_mean_interval_coverage": coverage,
        "average_interval_width": total_width / repetitions,
        "model": "iid_normal_observations_with_sample_standard_deviation",
        "certificate": {
            "coverage_is_plausible_for_declared_normal_model": .90 <= coverage <= .99,
            "interval_width_is_positive": total_width > 0.0,
        },
    }


def normal_mean_coverage_report_certificate(
    true_mean: object, standard_deviation: object, sample_size: object,
    trials: object, seed: object, z_value: object, report: object,
) -> bool:
    """Rebuild the fixed-seed sample-SD intervals and reject changed claims."""
    if not isinstance(report, dict):
        return False
    try:
        expected = normal_mean_coverage_report(
            true_mean, standard_deviation, sample_size, trials, seed, z_value,
        )
    except (TypeError, ValueError):
        return False
    return report == expected


def bernoulli_mean_report(
    probability: float, sample_size: int, trials: int = 3000, seed: int = 0,
) -> dict[str, float | int | dict[str, bool]]:
    """Simulate repeated Bernoulli sample means and compare their known scale.

    This is an empirical, seeded diagnostic.  It illustrates consequences of
    the LLN/CLT; it neither proves them nor licenses a normal approximation
    for arbitrary distributions or dependent samples.
    """
    _validate(probability, sample_size, trials)
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    rng = Random(seed)
    means = [sum(rng.random() < probability for _ in range(sample_size)) / sample_size for _ in range(trials)]
    empirical_mean = sum(means) / trials
    empirical_standard_error = sqrt(sum((mean - empirical_mean) ** 2 for mean in means) / (trials - 1))
    theoretical_standard_error = sqrt(probability * (1.0 - probability) / sample_size)
    interval_coverage = sum(
        abs(mean - probability) <= 1.96 * theoretical_standard_error for mean in means
    ) / trials
    relative_se_error = abs(empirical_standard_error - theoretical_standard_error) / theoretical_standard_error
    return {
        "probability": probability,
        "sample_size": sample_size,
        "trials": trials,
        "empirical_mean": empirical_mean,
        "empirical_standard_error": empirical_standard_error,
        "theoretical_standard_error": theoretical_standard_error,
        "normal_interval_coverage": interval_coverage,
        "certificate": {
            "mean_is_close_on_repeated_trials": abs(empirical_mean - probability) <= 5 * theoretical_standard_error / sqrt(trials),
            "empirical_standard_error_matches_theory": relative_se_error <= 0.15,
            "normal_coverage_is_plausible_for_this_bernoulli_setting": 0.90 <= interval_coverage <= 0.99,
        },
    }


def sample_size_scaling_report(
    probability: float, small_sample_size: int, large_sample_size: int, trials: int = 3000, seed: int = 0,
) -> dict[str, object]:
    """Compare two sample sizes against the 1/sqrt(n) standard-error law."""
    _validate(probability, small_sample_size, trials)
    _validate(probability, large_sample_size, trials)
    if large_sample_size <= small_sample_size:
        raise ValueError("large_sample_size must exceed small_sample_size")
    small = bernoulli_mean_report(probability, small_sample_size, trials, seed)
    large = bernoulli_mean_report(probability, large_sample_size, trials, seed + 1)
    observed_ratio = small["empirical_standard_error"] / large["empirical_standard_error"]
    expected_ratio = sqrt(large_sample_size / small_sample_size)
    return {
        "small": small,
        "large": large,
        "observed_standard_error_ratio": observed_ratio,
        "expected_standard_error_ratio": expected_ratio,
        "certificate": {
            "larger_sample_has_smaller_empirical_standard_error": observed_ratio > 1.0,
            "observed_ratio_matches_inverse_sqrt_scaling": abs(observed_ratio / expected_ratio - 1.0) <= 0.20,
        },
    }


def duplicated_bernoulli_mean_report(
    probability: float, independent_draws: int, duplicates_per_draw: int = 2,
    trials: int = 3000, seed: int = 0,
) -> dict[str, float | int | dict[str, bool]]:
    """Show why duplicated records do not create independent information.

    Each latent Bernoulli draw is repeated ``duplicates_per_draw`` times.  The
    recorded mean is therefore exactly the mean of ``independent_draws``
    draws, even though the log contains more rows.  This is a deliberately
    transparent dependence counterexample, not a general cluster-robust SE.
    """
    _validate(probability, independent_draws, trials)
    if (not isinstance(duplicates_per_draw, int) or isinstance(duplicates_per_draw, bool)
            or duplicates_per_draw < 2):
        raise ValueError("duplicates_per_draw must be an integer of at least two")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    rng = Random(seed)
    means = [
        sum(rng.random() < probability for _ in range(independent_draws)) / independent_draws
        for _ in range(trials)
    ]
    empirical_mean = sum(means) / trials
    empirical_standard_error = sqrt(sum((mean - empirical_mean) ** 2 for mean in means) / (trials - 1))
    record_count = independent_draws * duplicates_per_draw
    naive_iid_standard_error = sqrt(probability * (1.0 - probability) / record_count)
    cluster_aware_standard_error = sqrt(probability * (1.0 - probability) / independent_draws)
    observed_inflation = empirical_standard_error / naive_iid_standard_error
    expected_inflation = sqrt(duplicates_per_draw)
    return {
        "probability": probability,
        "independent_draws": independent_draws,
        "duplicates_per_draw": duplicates_per_draw,
        "record_count": record_count,
        "trials": trials,
        "empirical_mean": empirical_mean,
        "empirical_standard_error": empirical_standard_error,
        "naive_iid_standard_error": naive_iid_standard_error,
        "cluster_aware_standard_error": cluster_aware_standard_error,
        "observed_standard_error_inflation": observed_inflation,
        "expected_standard_error_inflation": expected_inflation,
        "certificate": {
            "duplicating_records_does_not_change_the_mean_definition": record_count > independent_draws,
            "cluster_aware_standard_error_exceeds_naive_iid": cluster_aware_standard_error > naive_iid_standard_error,
            "observed_inflation_matches_duplicate_structure": abs(observed_inflation / expected_inflation - 1.0) <= 0.15,
        },
    }


def duplicated_bernoulli_mean_report_certificate(
    probability: float, independent_draws: int, duplicates_per_draw: int, trials: int, seed: int, report: object,
) -> bool:
    """Replay the fixed-seed dependence counterexample and reject changed claims."""
    if not isinstance(report, dict):
        return False
    try:
        expected = duplicated_bernoulli_mean_report(
            probability, independent_draws, duplicates_per_draw, trials, seed,
        )
    except (TypeError, ValueError):
        return False
    return report == expected
