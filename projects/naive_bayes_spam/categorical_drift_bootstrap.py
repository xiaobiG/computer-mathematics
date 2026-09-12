"""Fixed-seed bootstrap intervals for categorical input-drift teaching reports.

This deliberately resamples individual categorical observations.  It therefore
describes uncertainty only under the declared i.i.d. observation-unit model;
time, user, device, and longitudinal dependence need their own designs.
"""

from __future__ import annotations

import random
from math import isfinite

from projects.naive_bayes_spam.block_window_calibration_bootstrap import _integer, _quantile
from projects.naive_bayes_spam.drift_monitoring import _categorical_drift_report, _categories, _positive_finite


CONTRACT = "categorical-drift-bootstrap/v1"


def _confidence_level(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not 0 < value < 1:
        raise ValueError("confidence_level must be in (0, 1)")
    return float(value)


def categorical_drift_bootstrap_report(
    reference: list[str], current: list[str], *, smoothing: float = 1e-6,
    psi_threshold: float = .1, repeats: int = 400, seed: int = 0,
    confidence_level: float = .95,
) -> dict[str, object]:
    """Resample complete observations while keeping the observed category support fixed.

    The percentile intervals quantify finite-sample variation *conditional on*
    this i.i.d. categorical resampling design.  They neither test a null
    hypothesis nor identify the cause of a distribution change.
    """
    reference = _categories(reference, "reference")
    current = _categories(current, "current")
    smoothing = _positive_finite(smoothing, "smoothing")
    psi_threshold = _positive_finite(psi_threshold, "psi_threshold")
    repeats, seed = _integer(repeats, "repeats", 20), _integer(seed, "seed", 0)
    confidence_level = _confidence_level(confidence_level)
    category_universe = sorted(set(reference) | set(current))
    point_report = _categorical_drift_report(
        reference, current, smoothing, psi_threshold, category_universe,
    )
    generator, psi_values, tv_values = random.Random(seed), [], []
    for _ in range(repeats):
        reference_sample = [reference[generator.randrange(len(reference))] for _ in reference]
        current_sample = [current[generator.randrange(len(current))] for _ in current]
        sample = _categorical_drift_report(
            reference_sample, current_sample, smoothing, psi_threshold, category_universe,
        )
        psi_values.append(sample["psi"])
        tv_values.append(sample["total_variation"])
    alpha = (1 - confidence_level) / 2
    return {
        "contract": CONTRACT,
        "point_report": point_report,
        "category_universe": category_universe,
        "sample_sizes": {"reference": len(reference), "current": len(current)},
        "bootstrap_policy": {
            "repeats": repeats,
            "seed": seed,
            "confidence_level": confidence_level,
            "resampling_unit": "iid_categorical_observation",
            "automatic_action": "none",
        },
        "psi_percentile_interval": [_quantile(psi_values, alpha), _quantile(psi_values, 1 - alpha)],
        "total_variation_percentile_interval": [_quantile(tv_values, alpha), _quantile(tv_values, 1 - alpha)],
        "causal_interpretation": "not_established",
        "interpretation": "sampling_uncertainty_under_iid_categorical_observation_resampling",
    }


def categorical_drift_bootstrap_certificate(
    reference: list[str], current: list[str], report: dict[str, object],
) -> bool:
    """Independently rebuild the full report, including its sampling policy."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        policy, point = report["bootstrap_policy"], report["point_report"]
        expected = categorical_drift_bootstrap_report(
            reference, current, smoothing=point["smoothing"], psi_threshold=point["psi_threshold"],
            repeats=policy["repeats"], seed=policy["seed"], confidence_level=policy["confidence_level"],
        )
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
