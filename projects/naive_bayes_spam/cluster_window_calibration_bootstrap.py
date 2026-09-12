"""Fixed-seed cluster bootstrap for pre-defined labeled calibration windows."""
from __future__ import annotations

import random
from math import isfinite

from projects.naive_bayes_spam.block_window_calibration_bootstrap import _integer, _quantile
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION, normalize_labeled_window
from projects.naive_bayes_spam.subgroup_calibration import _calibration_metrics
from projects.naive_bayes_spam.window_calibration_comparison import window_calibration_comparison_report


CONTRACT = "cluster-window-calibration-bootstrap/v1"


def _normalize_clusters(clusters, field):
    if not isinstance(clusters, list) or len(clusters) < 2:
        raise ValueError(f"{field} must contain at least two pre-defined non-empty clusters")
    normalized, identifiers = [], set()
    for cluster in clusters:
        if not isinstance(cluster, dict) or set(cluster) != {"cluster_id", "window"}:
            raise ValueError(f"{field} clusters must contain exactly cluster_id and window")
        identifier = cluster["cluster_id"]
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError(f"{field} cluster_id values must be unique non-empty strings")
        window = normalize_labeled_window(cluster["window"])
        identifiers.add(identifier)
        normalized.append({"cluster_id": identifier, "window": window})
    return normalized


def _flatten(clusters):
    return {
        "contract_version": LABELED_WINDOW_CONTRACT_VERSION,
        "probabilities": [value for cluster in clusters for value in cluster["window"]["probabilities"]],
        "labels": [value for cluster in clusters for value in cluster["window"]["labels"]],
    }


def cluster_window_calibration_bootstrap_report(
    reference_name, reference_clusters, current_name, current_clusters, *, bins=5,
    minimum_window_size=20, ece_delta_review_threshold=.05, repeats=400, seed=0,
    confidence_level=.95,
):
    """Resample whole user/device clusters under an explicit frozen contract."""
    repeats, seed = _integer(repeats, "repeats", 20), _integer(seed, "seed", 0)
    if (isinstance(confidence_level, bool) or not isinstance(confidence_level, (int, float))
            or not isfinite(confidence_level) or not 0 < confidence_level < 1):
        raise ValueError("confidence_level must be in (0, 1)")
    reference = _normalize_clusters(reference_clusters, "reference_clusters")
    current = _normalize_clusters(current_clusters, "current_clusters")
    point = window_calibration_comparison_report(
        reference_name, _flatten(reference), current_name, _flatten(current), bins=bins,
        minimum_window_size=minimum_window_size,
        ece_delta_review_threshold=ece_delta_review_threshold,
    )
    generator, deltas = random.Random(seed), []
    for _ in range(repeats):
        reference_sample = _flatten([reference[generator.randrange(len(reference))] for _ in reference])
        current_sample = _flatten([current[generator.randrange(len(current))] for _ in current])
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
            "resampling_unit": "predefined_labeled_user_or_device_cluster", "automatic_action": "none",
        },
        "cluster_sizes": {
            "reference": [{"cluster_id": cluster["cluster_id"], "observations": len(cluster["window"]["labels"])} for cluster in reference],
            "current": [{"cluster_id": cluster["cluster_id"], "observations": len(cluster["window"]["labels"])} for cluster in current],
        },
        "ece_delta_percentile_interval": [_quantile(deltas, alpha), _quantile(deltas, 1 - alpha)],
        "causal_interpretation": "not_established",
        "interpretation": "sampling_uncertainty_under_predefined_cluster_resampling",
    }


def cluster_window_calibration_bootstrap_certificate(reference_name, reference_clusters, current_name, current_clusters, report):
    """Rebuild a cluster-bootstrap report; reject changed policy or conclusion."""
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        policy, point_policy = report["bootstrap_policy"], report["point_report"]["policy"]
        expected = cluster_window_calibration_bootstrap_report(
            reference_name, reference_clusters, current_name, current_clusters,
            bins=point_policy["bins"], minimum_window_size=point_policy["minimum_window_size"],
            ece_delta_review_threshold=point_policy["ece_delta_review_threshold"],
            repeats=policy["repeats"], seed=policy["seed"], confidence_level=policy["confidence_level"],
        )
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
