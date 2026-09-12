"""Paired cluster-trajectory bootstrap for a deliberately narrow longitudinal lesson."""

from __future__ import annotations

import random
from math import isfinite

from projects.naive_bayes_spam.bootstrap_support import percentile, require_integer
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION, normalize_labeled_window
from projects.naive_bayes_spam.subgroup_calibration import _calibration_metrics
from projects.naive_bayes_spam.window_calibration_comparison import window_calibration_comparison_report


CONTRACT = "paired-longitudinal-cluster-calibration-bootstrap/v1"


def _normalize_trajectories(value: object) -> tuple[list[dict[str, object]], list[str]]:
    """Require whole, equally shaped user/device trajectories before sampling."""
    if not isinstance(value, list) or len(value) < 2:
        raise ValueError("trajectories must contain at least two predefined paired clusters")
    normalized: list[dict[str, object]] = []
    identifiers: set[str] = set()
    expected_strata: list[str] | None = None
    for item in value:
        if not isinstance(item, dict) or set(item) != {"cluster_id", "time_strata"}:
            raise ValueError("each trajectory must contain exactly cluster_id and time_strata")
        cluster_id = item["cluster_id"]
        if not isinstance(cluster_id, str) or not cluster_id or cluster_id in identifiers:
            raise ValueError("trajectory cluster_id values must be unique non-empty strings")
        strata = item["time_strata"]
        if not isinstance(strata, list) or len(strata) < 2:
            raise ValueError("each trajectory must contain at least two ordered time strata")
        seen: set[str] = set()
        normalized_strata = []
        for stratum in strata:
            required = {"time_stratum_id", "reference_window", "current_window"}
            if not isinstance(stratum, dict) or set(stratum) != required:
                raise ValueError("each time stratum must contain id, reference_window, and current_window")
            identifier = stratum["time_stratum_id"]
            if not isinstance(identifier, str) or not identifier or identifier in seen:
                raise ValueError("time_stratum_id values must be unique non-empty strings")
            seen.add(identifier)
            normalized_strata.append({
                "time_stratum_id": identifier,
                "reference_window": normalize_labeled_window(stratum["reference_window"]),
                "current_window": normalize_labeled_window(stratum["current_window"]),
            })
        ids = [stratum["time_stratum_id"] for stratum in normalized_strata]
        if expected_strata is None:
            expected_strata = ids
        elif ids != expected_strata:
            raise ValueError("every paired trajectory must use the same ordered time strata")
        identifiers.add(cluster_id)
        normalized.append({"cluster_id": cluster_id, "time_strata": normalized_strata})
    return normalized, expected_strata or []


def _flatten(trajectories: list[dict[str, object]], stratum_index: int, window_name: str) -> dict[str, object]:
    return {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": [
            probability
            for trajectory in trajectories
            for probability in trajectory["time_strata"][stratum_index][window_name]["probabilities"]  # type: ignore[index]
        ],
        "labels": [
            label
            for trajectory in trajectories
            for label in trajectory["time_strata"][stratum_index][window_name]["labels"]  # type: ignore[index]
        ],
    }


def _ece_delta(trajectories: list[dict[str, object]], index: int, bins: int) -> float:
    reference = _flatten(trajectories, index, "reference_window")
    current = _flatten(trajectories, index, "current_window")
    return (
        _calibration_metrics(current["probabilities"], current["labels"], bins, 1.96)["expected_calibration_error"]
        - _calibration_metrics(reference["probabilities"], reference["labels"], bins, 1.96)["expected_calibration_error"]
    )


def paired_longitudinal_cluster_calibration_bootstrap_report(
    reference_name: object, current_name: object, trajectories: object, *, bins: int = 5,
    minimum_window_size: int = 20, ece_delta_review_threshold: float = .05,
    repeats: int = 400, seed: int = 0, confidence_level: float = .95,
) -> dict[str, object]:
    """Resample full paired cluster trajectories, retaining all time positions.

    This is a finite descriptive bootstrap. It preserves the supplied pairing
    and stratum order; it neither estimates a time-series model nor attributes
    changes to an intervention.
    """
    repeats, seed = require_integer(repeats, "repeats", 20), require_integer(seed, "seed", 0)
    if (isinstance(confidence_level, bool) or not isinstance(confidence_level, (int, float))
            or not isfinite(confidence_level) or not 0 < confidence_level < 1):
        raise ValueError("confidence_level must be in (0, 1)")
    paired, stratum_ids = _normalize_trajectories(trajectories)
    point_reports = []
    point_deltas = []
    for index, stratum_id in enumerate(stratum_ids):
        point = window_calibration_comparison_report(
            reference_name, _flatten(paired, index, "reference_window"),
            current_name, _flatten(paired, index, "current_window"), bins=bins,
            minimum_window_size=minimum_window_size,
            ece_delta_review_threshold=ece_delta_review_threshold,
        )
        point_reports.append({"time_stratum_id": stratum_id, "point_report": point})
        point_deltas.append(point["comparison"]["expected_calibration_error_delta"])
    generator = random.Random(seed)
    samples = [[] for _ in stratum_ids]
    trend_samples = []
    for _ in range(repeats):
        sampled = [paired[generator.randrange(len(paired))] for _ in paired]
        deltas = [_ece_delta(sampled, index, bins) for index in range(len(stratum_ids))]
        for index, delta in enumerate(deltas):
            samples[index].append(delta)
        trend_samples.append(deltas[-1] - deltas[0])
    alpha = (1 - float(confidence_level)) / 2
    return {
        "contract": CONTRACT,
        "point_reports": point_reports,
        "bootstrap_policy": {
            "repeats": repeats, "seed": seed, "confidence_level": float(confidence_level),
            "resampling_unit": "whole_paired_cluster_trajectory_across_frozen_time_strata",
            "automatic_action": "none",
        },
        "trajectory_shape": [{
            "cluster_id": trajectory["cluster_id"],
            "time_strata": [{
                "time_stratum_id": stratum["time_stratum_id"],
                "reference_observations": len(stratum["reference_window"]["labels"]),
                "current_observations": len(stratum["current_window"]["labels"]),
            } for stratum in trajectory["time_strata"]],
        } for trajectory in paired],
        "per_time_stratum_ece_delta_intervals": [{
            "time_stratum_id": stratum_id,
            "point_estimate": point_deltas[index],
            "percentile_interval": [percentile(samples[index], alpha), percentile(samples[index], 1 - alpha)],
        } for index, stratum_id in enumerate(stratum_ids)],
        "first_to_last_time_trend": {
            "from_time_stratum_id": stratum_ids[0], "to_time_stratum_id": stratum_ids[-1],
            "point_estimate": point_deltas[-1] - point_deltas[0],
            "percentile_interval": [percentile(trend_samples, alpha), percentile(trend_samples, 1 - alpha)],
        },
        "causal_interpretation": "not_established",
        "interpretation": "sampling_uncertainty_under_paired_cluster_trajectory_resampling",
    }


def paired_longitudinal_cluster_calibration_bootstrap_certificate(
    reference_name: object, current_name: object, trajectories: object, report: object,
) -> bool:
    """Rebuild the whole trajectory bootstrap and reject changed pairing or trend fields."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        policy = report["bootstrap_policy"]
        point_policy = report["point_reports"][0]["point_report"]["policy"]
        expected = paired_longitudinal_cluster_calibration_bootstrap_report(
            reference_name, current_name, trajectories, bins=point_policy["bins"],
            minimum_window_size=point_policy["minimum_window_size"],
            ece_delta_review_threshold=point_policy["ece_delta_review_threshold"],
            repeats=policy["repeats"], seed=policy["seed"], confidence_level=policy["confidence_level"],
        )
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
