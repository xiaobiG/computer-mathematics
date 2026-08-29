"""教学用割线法：无需导数，但保留有限迭代和分母保护。"""

from __future__ import annotations

from math import isfinite
from typing import Callable


def secant_root(
    function: Callable[[float], float], left: float, right: float, *,
    residual_tol: float = 1e-12, step_tol: float = 1e-12, max_steps: int = 80,
) -> float:
    """Find a root from two distinct function values, or report a failed contract."""
    if max_steps <= 0 or residual_tol <= 0 or step_tol <= 0:
        raise ValueError("tolerances and max_steps must be positive")
    f_left, f_right = function(left), function(right)
    if not isfinite(f_left) or not isfinite(f_right):
        raise ValueError("initial function values must be finite")
    for _ in range(max_steps):
        if abs(f_right) <= residual_tol:
            return right
        denominator = f_right - f_left
        if denominator == 0:
            raise RuntimeError("secant slope vanished")
        candidate = right - f_right * (right - left) / denominator
        if not isfinite(candidate):
            raise RuntimeError("secant step became non-finite")
        if abs(candidate - right) <= step_tol * max(1.0, abs(candidate)):
            if abs(function(candidate)) <= residual_tol:
                return candidate
            raise RuntimeError("secant iteration stagnated away from a root")
        left, f_left = right, f_right
        right, f_right = candidate, function(candidate)
        if not isfinite(f_right):
            raise RuntimeError("function became non-finite during iteration")
    raise RuntimeError("secant method did not converge within max_steps")
