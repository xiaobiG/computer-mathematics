"""Finite-population randomization arithmetic for a causal-design lesson.

The module enumerates a deliberately tiny complete-randomization design.  It
does not infer missing potential outcomes from observed data, fit an effect
model, or make a real-world causal claim.
"""

from __future__ import annotations

from itertools import combinations
from math import isfinite


CONTRACT = "finite-complete-randomization/v1"
INTERFERENCE_CONTRACT = "two-unit-interference-randomization/v1"


def _potential_outcomes(value: object) -> list[tuple[float, float]]:
    if not isinstance(value, list) or not 2 <= len(value) <= 12:
        raise ValueError("potential_outcomes must contain from 2 to 12 units")
    normalized = []
    for pair in value:
        if (not isinstance(pair, (list, tuple)) or len(pair) != 2
                or any(not isinstance(outcome, (int, float)) or isinstance(outcome, bool)
                       or not isfinite(outcome) for outcome in pair)):
            raise ValueError("each potential-outcomes row must be two finite numeric values")
        normalized.append((float(pair[0]), float(pair[1])))
    return normalized


def assignment_mean_difference(potential_outcomes: object, treated_indices: object) -> float:
    """Return treated-minus-control means for one declared complete assignment."""
    outcomes = _potential_outcomes(potential_outcomes)
    if (not isinstance(treated_indices, (list, tuple))
            or any(not isinstance(index, int) or isinstance(index, bool) for index in treated_indices)):
        raise ValueError("treated_indices must be integer indexes")
    treated = set(treated_indices)
    if len(treated) != len(treated_indices) or not 1 <= len(treated) < len(outcomes) or any(
            index < 0 or index >= len(outcomes) for index in treated):
        raise ValueError("treated_indices must be unique, in range, and leave at least one control")
    treated_mean = sum(outcomes[index][1] for index in treated) / len(treated)
    controls = [outcomes[index][0] for index in range(len(outcomes)) if index not in treated]
    return treated_mean - sum(controls) / len(controls)


def complete_randomization_report(potential_outcomes: object, treated_count: object) -> dict[str, object]:
    """Enumerate uniform fixed-size assignments and compare expectation to ATE.

    The equality in the output is a finite-design identity conditional on the
    supplied table and uniform complete randomization, not evidence that a
    real study had random assignment, no attrition, no interference, or a
    target population beyond these units.
    """
    outcomes = _potential_outcomes(potential_outcomes)
    if (not isinstance(treated_count, int) or isinstance(treated_count, bool)
            or not 1 <= treated_count < len(outcomes)):
        raise ValueError("treated_count must leave at least one treated and one control unit")
    assignments = list(combinations(range(len(outcomes)), treated_count))
    differences = [assignment_mean_difference(outcomes, assignment) for assignment in assignments]
    average_treatment_effect = sum(treated - control for control, treated in outcomes) / len(outcomes)
    expected_difference = sum(differences) / len(differences)
    return {
        "contract": CONTRACT,
        "units": len(outcomes),
        "treated_count": treated_count,
        "assignment_count": len(assignments),
        "finite_population_average_treatment_effect": average_treatment_effect,
        "expected_difference_in_means": expected_difference,
        "expectation_minus_effect": expected_difference - average_treatment_effect,
        "assignment_difference_range": [min(differences), max(differences)],
        "assignment_mechanism": "uniform_complete_randomization_over_fixed_treated_count",
        "interpretation": "finite_design_identity_not_observational_or_population_causal_claim",
    }


def complete_randomization_certificate(potential_outcomes: object, treated_count: object, report: object) -> bool:
    """Rebuild the finite randomization calculation and reject altered claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == complete_randomization_report(potential_outcomes, treated_count)
    except ValueError:
        return False


def _two_unit_interference_outcomes(value: object) -> list[tuple[float, float, float, float]]:
    """Normalize Y_i(0,0), Y_i(0,1), Y_i(1,0), Y_i(1,1) for two units."""
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("interference_potential_outcomes must contain exactly two units")
    normalized = []
    for row in value:
        if (not isinstance(row, (list, tuple)) or len(row) != 4
                or any(not isinstance(outcome, (int, float)) or isinstance(outcome, bool)
                       or not isfinite(outcome) for outcome in row)):
            raise ValueError("each interference row must contain four finite numeric outcomes")
        normalized.append(tuple(float(outcome) for outcome in row))
    return normalized


def two_unit_interference_report(interference_potential_outcomes: object) -> dict[str, object]:
    """Enumerate one-treated assignments when each unit can affect its peer.

    The report deliberately uses exactly two units and a fixed one-treated
    design so that every observable assignment can be enumerated.  It does
    not estimate interference from data or validate a real randomization.
    """
    outcomes = _two_unit_interference_outcomes(interference_potential_outcomes)
    # Index order is (own treatment, peer treatment): 00, 01, 10, 11.
    assignment_differences = []
    for treated in range(2):
        control = 1 - treated
        treated_outcome = outcomes[treated][2]
        control_outcome = outcomes[control][1]
        assignment_differences.append({
            "treated_unit": treated,
            "control_unit": control,
            "treated_outcome_y_10": treated_outcome,
            "control_outcome_y_01": control_outcome,
            "treated_minus_control": treated_outcome - control_outcome,
        })
    direct_effects = [row[2] - row[0] for row in outcomes]
    peer_effects_when_control = [row[1] - row[0] for row in outcomes]
    expected_difference = sum(item["treated_minus_control"] for item in assignment_differences) / 2
    average_direct_effect = sum(direct_effects) / 2
    no_interference = all(row[0] == row[1] and row[2] == row[3] for row in outcomes)
    return {
        "contract": INTERFERENCE_CONTRACT,
        "units": 2,
        "assignment_mechanism": "uniform_complete_randomization_with_exactly_one_treated_unit",
        "potential_outcome_order": ["Y_i(0,0)", "Y_i(0,1)", "Y_i(1,0)", "Y_i(1,1)"],
        "assignment_differences": assignment_differences,
        "average_direct_effect_when_peer_control": average_direct_effect,
        "average_peer_effect_when_self_control": sum(peer_effects_when_control) / 2,
        "expected_treated_minus_control": expected_difference,
        "expectation_minus_direct_effect": expected_difference - average_direct_effect,
        "no_interference_condition_holds": no_interference,
        "interpretation": (
            "finite_interference_counterexample; random_assignment_alone_does_not_make_treated_control_difference "
            "equal_a_direct_effect_when_peer_outcomes_change"
        ),
        "boundary": (
            "not_an_interference_estimator_or_real_causal_claim; no_missing_outcomes, network, spillover_model, "
            "attrition, noncompliance_or_external_validity_are_established"
        ),
    }


def two_unit_interference_certificate(interference_potential_outcomes: object, report: object) -> bool:
    """Replay finite assignment outcomes and reject altered interference claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == two_unit_interference_report(interference_potential_outcomes)
    except ValueError:
        return False
