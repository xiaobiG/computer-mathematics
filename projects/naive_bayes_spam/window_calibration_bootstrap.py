"""Fixed-seed bootstrap intervals for a pre-named calibration comparison."""
from __future__ import annotations

import random
from math import isfinite

from projects.naive_bayes_spam.bootstrap_support import percentile, require_integer
from projects.naive_bayes_spam.labeled_window_monitoring import normalize_labeled_window
from projects.naive_bayes_spam.subgroup_calibration import _calibration_metrics
from projects.naive_bayes_spam.window_calibration_comparison import window_calibration_comparison_report

CONTRACT = "window-calibration-bootstrap/v1"


def window_calibration_bootstrap_report(reference_name, reference_window, current_name, current_window, *, bins=5, minimum_window_size=20, ece_delta_review_threshold=.05, repeats=400, seed=0, confidence_level=.95):
    """Describe bootstrap sampling variation; never infer cause or deployment action."""
    repeats, seed = require_integer(repeats, "repeats", 20), require_integer(seed, "seed", 0)
    if isinstance(confidence_level, bool) or not isinstance(confidence_level, (int, float)) or not isfinite(confidence_level) or not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be in (0, 1)")
    point = window_calibration_comparison_report(reference_name, reference_window, current_name, current_window, bins=bins, minimum_window_size=minimum_window_size, ece_delta_review_threshold=ece_delta_review_threshold)
    reference, current = normalize_labeled_window(reference_window), normalize_labeled_window(current_window)
    generator = random.Random(seed)
    deltas = []
    for _ in range(repeats):
        ref_indices = [generator.randrange(len(reference["labels"])) for _ in reference["labels"]]
        cur_indices = [generator.randrange(len(current["labels"])) for _ in current["labels"]]
        ref_ece = _calibration_metrics([reference["probabilities"][i] for i in ref_indices], [reference["labels"][i] for i in ref_indices], bins, 1.96)["expected_calibration_error"]
        cur_ece = _calibration_metrics([current["probabilities"][i] for i in cur_indices], [current["labels"][i] for i in cur_indices], bins, 1.96)["expected_calibration_error"]
        deltas.append(cur_ece - ref_ece)
    alpha = (1 - float(confidence_level)) / 2
    interval = [percentile(deltas, alpha), percentile(deltas, 1 - alpha)]
    return {"contract": CONTRACT, "point_report": point, "bootstrap_policy": {"repeats": repeats, "seed": seed, "confidence_level": float(confidence_level), "resampling_unit": "labeled_observation", "automatic_action": "none"}, "ece_delta_percentile_interval": interval, "causal_interpretation": "not_established", "interpretation": "sampling_uncertainty_for_frozen_descriptive_difference"}


def window_calibration_bootstrap_certificate(reference_name, reference_window, current_name, current_window, report):
    if not isinstance(report, dict) or report.get("contract") != CONTRACT:
        return False
    try:
        policy, point_policy = report["bootstrap_policy"], report["point_report"]["policy"]
        expected = window_calibration_bootstrap_report(reference_name, reference_window, current_name, current_window, bins=point_policy["bins"], minimum_window_size=point_policy["minimum_window_size"], ece_delta_review_threshold=point_policy["ece_delta_review_threshold"], repeats=policy["repeats"], seed=policy["seed"], confidence_level=policy["confidence_level"])
        return report == expected
    except (KeyError, TypeError, ValueError):
        return False
