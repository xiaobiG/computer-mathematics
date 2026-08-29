"""Finite probability spaces and auditable event algebra for teaching."""

from dataclasses import dataclass
from math import isclose, isfinite


@dataclass(frozen=True)
class FiniteEventReport:
    outcomes: int
    left_probability: float
    right_probability: float
    intersection_probability: float
    union_probability: float
    complement_left_probability: float
    conditional_right_given_left: float
    independence_residual: float


def _validate_space(space, tolerance=1e-12):
    if not isinstance(space, dict) or not space:
        raise ValueError("space must be a non-empty outcome-to-probability mapping")
    total = 0.0
    for probability in space.values():
        if not isinstance(probability, (int, float)) or isinstance(probability, bool) or not isfinite(probability) or probability < 0:
            raise ValueError("outcome probabilities must be finite and non-negative")
        total += float(probability)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=tolerance):
        raise ValueError("outcome probabilities must sum to one")


def _event(space, event):
    try:
        selected = frozenset(event)
    except TypeError as error:
        raise ValueError("event must be an iterable of hashable outcomes") from error
    unknown = selected.difference(space)
    if unknown:
        raise ValueError("event contains outcomes outside the sample space")
    return selected


def event_probability(space, event):
    """Return P(event) after validating a finite probability space."""
    _validate_space(space)
    selected = _event(space, event)
    return sum(float(space[outcome]) for outcome in selected)


def finite_event_report(space, left, right):
    """Compute set identities, conditioning and an independence residual."""
    _validate_space(space)
    left_event, right_event = _event(space, left), _event(space, right)
    left_probability = event_probability(space, left_event)
    right_probability = event_probability(space, right_event)
    intersection_probability = event_probability(space, left_event.intersection(right_event))
    if left_probability == 0.0:
        raise ValueError("cannot condition on a zero-probability finite event")
    universe = frozenset(space)
    return FiniteEventReport(
        outcomes=len(space),
        left_probability=left_probability,
        right_probability=right_probability,
        intersection_probability=intersection_probability,
        union_probability=event_probability(space, left_event.union(right_event)),
        complement_left_probability=event_probability(space, universe.difference(left_event)),
        conditional_right_given_left=intersection_probability / left_probability,
        independence_residual=abs(intersection_probability - left_probability * right_probability),
    )


def finite_event_certificate(space, left, right, report, tolerance=1e-12):
    """Recompute event identities and reject an altered report."""
    if not isinstance(report, FiniteEventReport):
        return False
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or tolerance < 0:
        return False
    try:
        expected = finite_event_report(space, left, right)
    except ValueError:
        return False
    return report.outcomes == expected.outcomes and all(
        isclose(actual, target, rel_tol=tolerance, abs_tol=tolerance)
        for actual, target in zip(
            (report.left_probability, report.right_probability, report.intersection_probability,
             report.union_probability, report.complement_left_probability,
             report.conditional_right_given_left, report.independence_residual),
            (expected.left_probability, expected.right_probability, expected.intersection_probability,
             expected.union_probability, expected.complement_left_probability,
             expected.conditional_right_given_left, expected.independence_residual),
        )
    )
