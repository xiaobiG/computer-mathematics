"""Time-stratified cluster bootstrap for a deliberately narrow calibration contract."""

from __future__ import annotations

import random
from math import isfinite

from projects.naive_bayes_spam.block_window_calibration_bootstrap import _integer, _quantile
from projects.naive_bayes_spam.cluster_window_calibration_bootstrap import _flatten, _normalize_clusters
from projects.naive_bayes_spam.subgroup_calibration import _calibration_metrics
from projects.naive_bayes_spam.window_calibration_comparison import window_calibration_comparison_report


CONTRACT = "time-stratified-cluster-calibration-bootstrap/v1"


def _normalize_time_strata(strata, field):
    """Require frozen, ordered time strata with clusters unique across strata.

    Cluster identifiers may not recur in a window.  This makes every sampled
    cluster belong to exactly one time stratum; longitudinal users spanning
    several strata need a paired longitudinal design, which this lesson
    intentionally does not claim to implement.
    """
    if not isinstance(strata, list) or len(strata) < 2:
        raise ValueError(f"{field} must contain at least two predefined time strata")
    normalized, stratum_ids, cluster_ids = [], set(), set()
    for stratum in strata:
        if not isinstance(stratum, dict) or set(stratum) != {"time_stratum_id", "clusters"}:
            raise ValueError(f"{field} strata must contain exactly time_stratum_id and clusters")
        identifier = stratum["time_stratum_id"]
        if not isinstance(identifier, str) or not identifier or identifier in stratum_ids:
            raise ValueError(f"{field} time_stratum_id values must be unique non-empty strings")
        clusters = _normalize_clusters(stratum["clusters"], f"{field}.{identifier}.clusters")
        repeated = cluster_ids.intersection(cluster["cluster_id"] for cluster in clusters)
        if repeated:
            raise ValueError(f"{field} cluster_id values must not span time strata")
        stratum_ids.add(identifier)
        cluster_ids.update(cluster["cluster_id"] for cluster in clusters)
        normalized.append({"time_stratum_id": identifier, "clusters": clusters})
    return normalized


def _flatten_strata(strata):
    return _flatten([cluster for stratum in strata for cluster in stratum["clusters"]])


def _sample_strata(strata, generator):
    sampled = []
    for stratum in strata:
        clusters = stratum["clusters"]
        sampled.extend(clusters[generator.randrange(len(clusters))] for _ in clusters)
    return _flatten(sampled)


def _stratum_shape(strata):
    return [
        {
            "time_stratum_id": stratum["time_stratum_id"],
            "clusters": [
                {"cluster_id": cluster["cluster_id"], "observations": len(cluster["window"]["labels"])}
                for cluster in stratum["clusters"]
            ],
        }
        for stratum in strata
    ]


def time_stratified_cluster_calibration_bootstrap_report(
    reference_name, reference_time_strata, current_name, current_time_strata, *, bins=5,
    minimum_window_size=20, ece_delta_review_threshold=.05, repeats=400, seed=0,
    confidence_level=.95,
):
    """Resample whole clusters within their frozen time strata.

    The procedure preserves the number and ordering of time strata and never
    moves a cluster from one stratum to another.  It is a pedagogical design
    for disjoint clusters, not a generic solution for serial dependence.
    """
    repeats, seed = _integer(repeats, "repeats", 20), _integer(seed, "seed", 0)
    if (isinstance(confidence_level, bool) or not isinstance(confidence_level, (int, float))
            or not isfinite(confidence_level) or not 0 < confidence_level < 1):
        raise ValueError("confidence_level must be in (0, 1)")
    reference = _normalize_time_strata(reference_time_strata, "reference_time_strata")
    current = _normalize_time_strata(current_time_strata, "current_time_strata")
    point = window_calibration_comparison_report(
        reference_name, _flatten_strata(reference), current_name, _flatten_strata(current),
        bins=bins, minimum_window_size=minimum_window_size,
        ece_delta_review_threshold=ece_delta_review_threshold,
    )
    generator, deltas = random.Random(seed), []
    for _ in range(repeats):
        reference_sample = _sample_strata(reference, generator)
        current_sample = _sample_strata(current, generator)
        reference_ece = _calibration_metrics(
            reference_sample["probabilities"], reference_sample["labels"], bins, 1.96,
        )["expected_calibration_error"]
        current_ece = _calibration_metrics(
            current_sample["probabilities"], current_sample["labels"], bins, 1.96,
        )["expected_calibration_error"]
        deltas.append(current_ece - reference_ece)
    alpha = (1 - float(confidence_level)) / 2
    return {
        "contract": CONTRACT,
        "point_report": point,
        "bootstrap_policy": {
            "repeats": repeats, "seed": seed, "confidence_level": float(confidence_level),
            "resampling_unit": "predefined_cluster_within_frozen_time_stratum",
            "automatic_action": "none",
        },
        "time_stratum_cluster_sizes": {
            "reference": _stratum_shape(reference), "current": _stratum_shape(current),
        },
        "ece_delta_percentile_interval": [_quantile(deltas, alpha), _quantile(deltas, 1 - alpha)],
        "causal_interpretation": "not_established",
        "interpretation": "sampling_uncertainty_under_time_stratified_cluster_resampling",
    }


def time_stratified_cluster_calibration_bootstrap_certificate(
    reference_name, reference_time_strata, current_name, current_time_strata, report,
):
    """Rebuild the full fixed-seed report; reject policy, shape, or value changes."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        policy, point_policy = report["bootstrap_policy"], report["point_report"]["policy"]
        expected = time_stratified_cluster_calibration_bootstrap_report(
            reference_name, reference_time_strata, current_name, current_time_strata,
            bins=point_policy["bins"], minimum_window_size=point_policy["minimum_window_size"],
            ece_delta_review_threshold=point_policy["ece_delta_review_threshold"],
            repeats=policy["repeats"], seed=policy["seed"], confidence_level=policy["confidence_level"],
        )
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
