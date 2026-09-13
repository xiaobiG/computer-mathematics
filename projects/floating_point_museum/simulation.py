"""可复现的蒙特卡洛实验：分离抽样波动与浮点运算。"""

from __future__ import annotations

from math import isfinite, pi, sqrt
from random import Random
from statistics import fmean


def estimate_pi(samples: int, *, seed: int) -> float:
    """用单位正方形采样估计圆周率；固定 seed 使每次轨迹可复现。"""
    if samples <= 0:
        raise ValueError("samples must be positive")
    rng = Random(seed)
    inside = sum(rng.random() ** 2 + rng.random() ** 2 <= 1.0 for _ in range(samples))
    return 4.0 * inside / samples


def simulation_report(samples: int, *, seeds: tuple[int, ...]) -> dict[str, float | int]:
    """报告重复独立运行的均值、样本标准差和均值标准误。"""
    if not seeds:
        raise ValueError("at least one seed is required")
    estimates = [estimate_pi(samples, seed=seed) for seed in seeds]
    mean = fmean(estimates)
    sample_std = sqrt(sum((value - mean) ** 2 for value in estimates) / (len(estimates) - 1)) if len(estimates) > 1 else 0.0
    return {
        "runs": len(estimates),
        "samples_per_run": samples,
        "mean": mean,
        "sample_std": sample_std,
        "standard_error": sample_std / sqrt(len(estimates)),
    }


def simulation_report_certificate(samples: int, *, seeds: tuple[int, ...], report: object) -> bool:
    """Recompute fixed-seed summary statistics instead of trusting a report."""
    if not isinstance(report, dict):
        return False
    try:
        return report == simulation_report(samples, seeds=seeds)
    except (TypeError, ValueError):
        return False


def truth_target_stopping_report(
    samples_per_stage: int, stages: int, *, seed: int, tolerance: float, reference_value: float = pi,
) -> dict[str, object]:
    """Expose a bad teaching stopping rule: stop when an estimate nears a known truth.

    One local pseudo-random stream is extended stage by stage, so each value is
    a prefix estimate rather than an independent retry.  This report does not
    supply a confidence interval or a valid sequential inference procedure: a
    reference-value target is intentionally a selection-bias counterexample.
    """
    if (not isinstance(samples_per_stage, int) or isinstance(samples_per_stage, bool)
            or samples_per_stage <= 0):
        raise ValueError("samples_per_stage must be a positive integer")
    if not isinstance(stages, int) or isinstance(stages, bool) or stages <= 0:
        raise ValueError("stages must be a positive integer")
    if (not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool)
            or not isfinite(tolerance) or tolerance < 0.0):
        raise ValueError("tolerance must be a finite non-negative number")
    if (not isinstance(reference_value, (int, float)) or isinstance(reference_value, bool)
            or not isfinite(reference_value)):
        raise ValueError("reference_value must be finite")
    rng = Random(seed)
    inside = 0
    stage_samples, estimates, absolute_errors = [], [], []
    for stage in range(1, stages + 1):
        inside += sum(
            rng.random() ** 2 + rng.random() ** 2 <= 1.0
            for _ in range(samples_per_stage)
        )
        total = stage * samples_per_stage
        estimate = 4.0 * inside / total
        stage_samples.append(total)
        estimates.append(estimate)
        absolute_errors.append(abs(estimate - float(reference_value)))
    first = next((index for index, error in enumerate(absolute_errors) if error <= tolerance), None)
    return {
        "contract": "truth-target-stopping-counterexample/v1",
        "samples_per_stage": samples_per_stage,
        "stages": stages,
        "seed": seed,
        "reference_value": float(reference_value),
        "tolerance": float(tolerance),
        "stage_samples": tuple(stage_samples),
        "estimates": tuple(estimates),
        "absolute_errors": tuple(absolute_errors),
        "first_within_tolerance_stage": None if first is None else first + 1,
        "stopping_status": "stopped_by_truth_target" if first is not None else "truth_target_not_met",
        "automatic_action": "none",
    }


def truth_target_stopping_report_certificate(
    samples_per_stage: int, stages: int, *, seed: int, tolerance: float,
    report: object, reference_value: float = pi,
) -> bool:
    """Recreate every prefix and reject a changed stopping stage or status."""
    if not isinstance(report, dict):
        return False
    try:
        return report == truth_target_stopping_report(
            samples_per_stage, stages, seed=seed, tolerance=tolerance,
            reference_value=reference_value,
        )
    except (TypeError, ValueError):
        return False


if __name__ == "__main__":
    print(simulation_report(10_000, seeds=(2026, 2027, 2028, 2029)))
