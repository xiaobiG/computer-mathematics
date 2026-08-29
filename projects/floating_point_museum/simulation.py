"""可复现的蒙特卡洛实验：分离抽样波动与浮点运算。"""

from __future__ import annotations

from math import sqrt
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


if __name__ == "__main__":
    print(simulation_report(10_000, seeds=(2026, 2027, 2028, 2029)))
