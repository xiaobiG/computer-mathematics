"""Fixed-seed block bootstrap for pre-partitioned calibration windows."""
from __future__ import annotations

import random
from math import isfinite

from projects.naive_bayes_spam.bootstrap_support import percentile, require_integer
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION, normalize_labeled_window
from projects.naive_bayes_spam.subgroup_calibration import _calibration_metrics
from projects.naive_bayes_spam.window_calibration_comparison import window_calibration_comparison_report


CONTRACT = "block-window-calibration-bootstrap/v1"


def _normalize_blocks(blocks, field):
    if not isinstance(blocks, list) or len(blocks) < 2:
        raise ValueError(f"{field} must contain at least two pre-defined non-empty blocks")
    normalized = [normalize_labeled_window(block) for block in blocks]
    if any(not block["labels"] for block in normalized):
        raise ValueError(f"{field} blocks must be non-empty")
    return normalized


def _flatten(blocks):
    probabilities = [value for block in blocks for value in block["probabilities"]]
    labels = [value for block in blocks for value in block["labels"]]
    return {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": probabilities, "labels": labels}


def block_window_calibration_bootstrap_report(reference_name, reference_blocks, current_name, current_blocks, *, bins=5, minimum_window_size=20, ece_delta_review_threshold=.05, repeats=400, seed=0, confidence_level=.95):
    """Resample complete pre-defined blocks; never infer causality or actions."""
    repeats, seed = require_integer(repeats, "repeats", 20), require_integer(seed, "seed", 0)
    if isinstance(confidence_level, bool) or not isinstance(confidence_level, (int, float)) or not isfinite(confidence_level) or not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be in (0, 1)")
    reference, current = _normalize_blocks(reference_blocks, "reference_blocks"), _normalize_blocks(current_blocks, "current_blocks")
    reference_window, current_window = _flatten(reference), _flatten(current)
    point = window_calibration_comparison_report(reference_name, reference_window, current_name, current_window, bins=bins, minimum_window_size=minimum_window_size, ece_delta_review_threshold=ece_delta_review_threshold)
    generator, deltas = random.Random(seed), []
    for _ in range(repeats):
        ref_sample = _flatten([reference[generator.randrange(len(reference))] for _ in reference])
        cur_sample = _flatten([current[generator.randrange(len(current))] for _ in current])
        ref_ece = _calibration_metrics(ref_sample["probabilities"], ref_sample["labels"], bins, 1.96)["expected_calibration_error"]
        cur_ece = _calibration_metrics(cur_sample["probabilities"], cur_sample["labels"], bins, 1.96)["expected_calibration_error"]
        deltas.append(cur_ece - ref_ece)
    alpha = (1 - float(confidence_level)) / 2
    return {"contract": CONTRACT, "point_report": point, "bootstrap_policy": {"repeats": repeats, "seed": seed, "confidence_level": float(confidence_level), "resampling_unit": "predefined_labeled_time_block", "automatic_action": "none"}, "block_sizes": {"reference": [len(block["labels"]) for block in reference], "current": [len(block["labels"]) for block in current]}, "ece_delta_percentile_interval": [percentile(deltas, alpha), percentile(deltas, 1 - alpha)], "causal_interpretation": "not_established", "interpretation": "sampling_uncertainty_under_predefined_block_resampling"}


def block_window_calibration_bootstrap_certificate(reference_name, reference_blocks, current_name, current_blocks, report):
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        policy, point_policy = report["bootstrap_policy"], report["point_report"]["policy"]
        expected = block_window_calibration_bootstrap_report(reference_name, reference_blocks, current_name, current_blocks, bins=point_policy["bins"], minimum_window_size=point_policy["minimum_window_size"], ece_delta_review_threshold=point_policy["ece_delta_review_threshold"], repeats=policy["repeats"], seed=policy["seed"], confidence_level=policy["confidence_level"])
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
