"""Finite joint-distribution primitives for the probability lessons."""

from __future__ import annotations

from math import isclose, isfinite
from typing import Hashable


Outcome = Hashable
JointTable = dict[tuple[Outcome, Outcome], float]


def _validate_joint(table: JointTable) -> None:
    if not isinstance(table, dict) or not table:
        raise ValueError("joint table must be a non-empty dictionary")
    for outcome, probability in table.items():
        if not isinstance(outcome, tuple) or len(outcome) != 2:
            raise ValueError("each joint outcome must be a pair")
        if (not isinstance(probability, (int, float)) or isinstance(probability, bool)
                or not isfinite(probability) or probability < 0.0):
            raise ValueError("joint probabilities must be finite and non-negative")
    if not isclose(sum(table.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("joint probabilities must sum to one")


def marginal_first(table: JointTable) -> dict[Outcome, float]:
    """Sum out the second variable: P(X=x) = sum_y P(X=x, Y=y)."""
    _validate_joint(table)
    result: dict[Outcome, float] = {}
    for (first, _), probability in table.items():
        result[first] = result.get(first, 0.0) + probability
    return result


def marginal_second(table: JointTable) -> dict[Outcome, float]:
    """Sum out the first variable: P(Y=y) = sum_x P(X=x, Y=y)."""
    _validate_joint(table)
    result: dict[Outcome, float] = {}
    for (_, second), probability in table.items():
        result[second] = result.get(second, 0.0) + probability
    return result


def conditional_second_given_first(table: JointTable, given: Outcome) -> dict[Outcome, float]:
    """Return P(Y=y | X=given), rejecting a zero-probability condition."""
    first_marginal = marginal_first(table)
    evidence = first_marginal.get(given, 0.0)
    if evidence == 0.0:
        raise ValueError("conditioning event has probability zero")
    return {second: probability / evidence
            for (first, second), probability in table.items() if first == given}


def independence_residual(table: JointTable) -> float:
    """Return max |P(x,y)-P(x)P(y)|; zero certifies finite-table independence."""
    first_marginal = marginal_first(table)
    second_marginal = marginal_second(table)
    return max(abs(probability - first_marginal[first] * second_marginal[second])
               for (first, second), probability in table.items())
