"""Finite, auditable Kaplan--Meier calculations for a right-censored cohort.

This teaching module estimates a survival curve from declared observed times.
It cannot establish independent censoring, causal effects, or a population law.
"""

from dataclasses import dataclass
from math import isclose, isfinite


RIGHT_CENSORING_CONTRACT = "right-censored-kaplan-meier/v1"


@dataclass(frozen=True)
class RightCensoredObservation:
    identifier: str
    observed_time: float
    event_observed: bool


@dataclass(frozen=True)
class KaplanMeierStep:
    time: float
    at_risk: int
    events: int
    censored_at_time: int
    survival: float


@dataclass(frozen=True)
class RightCensoringReport:
    contract: str
    horizon: float
    observations: tuple[RightCensoredObservation, ...]
    steps: tuple[KaplanMeierStep, ...]
    event_count: int
    censor_count: int
    survival_at_horizon: float
    restricted_mean_survival_time: float
    mean_observed_time: float
    mean_observed_time_interpretation: str
    independent_censoring_assumption: str
    automatic_action: str


def _as_observation(value):
    if isinstance(value, RightCensoredObservation):
        observation = value
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        observation = RightCensoredObservation(value[0], value[1], value[2])
    else:
        raise ValueError("each observation must be (identifier, observed_time, event_observed)")
    if not isinstance(observation.identifier, str) or not observation.identifier:
        raise ValueError("observation identifiers must be non-empty strings")
    if (not isinstance(observation.observed_time, (int, float)) or isinstance(observation.observed_time, bool)
            or not isfinite(observation.observed_time) or observation.observed_time < 0.0):
        raise ValueError("observed times must be finite non-negative numbers")
    if not isinstance(observation.event_observed, bool):
        raise ValueError("event_observed must be boolean")
    return RightCensoredObservation(observation.identifier, float(observation.observed_time), observation.event_observed)


def right_censoring_report(observations, horizon):
    """Build the product-limit curve and RMST over a declared finite horizon.

    Censored observations are in each earlier risk set, but do not cause a
    survival drop and do not enter later risk sets.  At a tied time, all events
    use the risk set before same-time censoring is removed.
    """
    if (not isinstance(horizon, (int, float)) or isinstance(horizon, bool)
            or not isfinite(horizon) or horizon <= 0.0):
        raise ValueError("horizon must be a finite positive number")
    if not isinstance(observations, (list, tuple)) or not observations:
        raise ValueError("observations must be a non-empty sequence")
    horizon = float(horizon)
    parsed = tuple(_as_observation(value) for value in observations)
    if len({value.identifier for value in parsed}) != len(parsed):
        raise ValueError("observation identifiers must be unique")
    if any(value.observed_time > horizon for value in parsed):
        raise ValueError("observed times must not exceed horizon")

    event_times = sorted({value.observed_time for value in parsed if value.event_observed})
    survival = 1.0
    previous_time = 0.0
    restricted_mean = 0.0
    steps = []
    for time in event_times:
        restricted_mean += survival * (time - previous_time)
        at_risk = sum(value.observed_time >= time for value in parsed)
        events = sum(value.event_observed and value.observed_time == time for value in parsed)
        censored = sum(not value.event_observed and value.observed_time == time for value in parsed)
        survival *= 1.0 - events / at_risk
        steps.append(KaplanMeierStep(time, at_risk, events, censored, survival))
        previous_time = time
    restricted_mean += survival * (horizon - previous_time)
    mean_observed_time = sum(value.observed_time for value in parsed) / len(parsed)
    return RightCensoringReport(
        RIGHT_CENSORING_CONTRACT, horizon, parsed, tuple(steps),
        sum(value.event_observed for value in parsed), sum(not value.event_observed for value in parsed),
        survival, restricted_mean, mean_observed_time,
        "not_a_survival_estimate_when_right_censoring_is_present",
        "declared_not_verified", "none",
    )


def right_censoring_certificate(observations, horizon, report, tolerance=1e-12):
    """Rebuild a report from its observed cohort and reject altered evidence."""
    if not isinstance(report, RightCensoringReport):
        return False
    if (not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool)
            or not isfinite(tolerance) or tolerance < 0.0):
        return False
    try:
        expected = right_censoring_report(observations, horizon)
    except ValueError:
        return False
    if report.contract != expected.contract or report.horizon != expected.horizon or report.observations != expected.observations:
        return False
    if (report.event_count != expected.event_count or report.censor_count != expected.censor_count
            or report.mean_observed_time_interpretation != expected.mean_observed_time_interpretation
            or report.independent_censoring_assumption != expected.independent_censoring_assumption
            or report.automatic_action != expected.automatic_action or len(report.steps) != len(expected.steps)):
        return False
    if not all(left.time == right.time and left.at_risk == right.at_risk and left.events == right.events
               and left.censored_at_time == right.censored_at_time
               and isclose(left.survival, right.survival, rel_tol=tolerance, abs_tol=tolerance)
               for left, right in zip(report.steps, expected.steps)):
        return False
    return all(isclose(getattr(report, field), getattr(expected, field), rel_tol=tolerance, abs_tol=tolerance)
               for field in ("survival_at_horizon", "restricted_mean_survival_time", "mean_observed_time"))
