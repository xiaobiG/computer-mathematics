"""Small, explicit error-analysis formulas for numerical-computing lessons."""

from __future__ import annotations

from math import inf, isfinite


def _finite(value: float, name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise ValueError(f"{name} must be finite")


def absolute_error(reference: float, approximation: float) -> float:
    """Return |approximation - reference| after rejecting non-finite inputs."""
    _finite(reference, "reference")
    _finite(approximation, "approximation")
    return abs(approximation - reference)


def relative_error(reference: float, approximation: float) -> float:
    """Return relative error; it is undefined when the reference is zero."""
    _finite(reference, "reference")
    _finite(approximation, "approximation")
    if reference == 0.0:
        raise ValueError("relative error is undefined for a zero reference")
    return absolute_error(reference, approximation) / abs(reference)


def product_relative_error_bound(left_relative: float, right_relative: float) -> float:
    """Return (1+e_left)(1+e_right)-1 for non-negative relative bounds."""
    _finite(left_relative, "left_relative")
    _finite(right_relative, "right_relative")
    if left_relative < 0.0 or right_relative < 0.0:
        raise ValueError("relative error bounds must be non-negative")
    return (1.0 + left_relative) * (1.0 + right_relative) - 1.0


def first_order_absolute_change_scale(partials: list[float], input_absolute_errors: list[float]) -> float:
    """Return sum_i |df/dx_i| * |delta x_i| for a local linearisation.

    This is a first-order sensitivity scale, not an exact finite-perturbation
    bound: nonlinear second- and higher-order terms can make the actual change
    larger.  Keeping that distinction in the API name prevents a common
    numerical-analysis mistake in teaching code.
    """
    if not isinstance(partials, list) or not isinstance(input_absolute_errors, list):
        raise ValueError("partials and input_absolute_errors must be lists")
    if not partials or len(partials) != len(input_absolute_errors):
        raise ValueError("partials and input_absolute_errors need the same nonzero length")
    for index, (partial, error) in enumerate(zip(partials, input_absolute_errors)):
        _finite(partial, f"partial[{index}]")
        _finite(error, f"input_absolute_errors[{index}]")
        if error < 0.0:
            raise ValueError("input absolute errors must be non-negative")
    return sum(abs(partial) * error for partial, error in zip(partials, input_absolute_errors))


def subtraction_condition_number(left: float, right: float) -> float:
    """Return (|a|+|b|)/|a-b|, exposing cancellation sensitivity."""
    _finite(left, "left")
    _finite(right, "right")
    difference = left - right
    return inf if difference == 0.0 else (abs(left) + abs(right)) / abs(difference)


def product_linearisation_report(
    left: float, right: float, left_perturbation: float, right_perturbation: float,
) -> dict[str, object]:
    """Replay a finite product perturbation beside its first-order model.

    The absolute first-order scale is deliberately kept separate from the
    signed linear term.  It is a local worst-direction *scale*, not a bound
    for a finite nonlinear perturbation; the retained cross term makes that
    distinction inspectable on one small, exactly representable example.
    """
    for value, name in (
        (left, "left"), (right, "right"),
        (left_perturbation, "left_perturbation"),
        (right_perturbation, "right_perturbation"),
    ):
        _finite(value, name)
    baseline = left * right
    perturbed = (left + left_perturbation) * (right + right_perturbation)
    signed_linear_change = right * left_perturbation + left * right_perturbation
    cross_term = left_perturbation * right_perturbation
    actual_change = perturbed - baseline
    for value, name in (
        (baseline, "baseline_product"), (perturbed, "perturbed_product"),
        (signed_linear_change, "signed_linear_change"),
        (cross_term, "second_order_cross_term"), (actual_change, "actual_signed_change"),
    ):
        _finite(value, name)
    first_order_scale = first_order_absolute_change_scale(
        [right, left], [abs(left_perturbation), abs(right_perturbation)],
    )
    return {
        "contract": "product-linearisation-report/v1",
        "left": left,
        "right": right,
        "left_perturbation": left_perturbation,
        "right_perturbation": right_perturbation,
        "baseline_product": baseline,
        "perturbed_product": perturbed,
        "signed_linear_change": signed_linear_change,
        "second_order_cross_term": cross_term,
        "actual_signed_change": actual_change,
        "absolute_first_order_scale": first_order_scale,
        "exact_decomposition_holds": actual_change == signed_linear_change + cross_term,
        "finite_change_exceeds_first_order_scale": abs(actual_change) > first_order_scale,
        "interpretation": (
            "the first-order scale is a local sensitivity quantity, not a universal "
            "finite-perturbation bound"
        ),
    }


def product_linearisation_report_certificate(
    left: float, right: float, left_perturbation: float, right_perturbation: float,
    report: object,
) -> bool:
    """Reject a report unless every finite-perturbation field replays exactly."""
    if not isinstance(report, dict):
        return False
    try:
        return report == product_linearisation_report(
            left, right, left_perturbation, right_perturbation,
        )
    except (TypeError, ValueError):
        return False
