"""Small, auditable probability recalibration tools for teaching.

The calibrator deliberately accepts probabilities and labels instead of a
classifier object.  This keeps the train/validation/test split visible to the
caller: fitting it on a final test set would be data leakage, not a feature.
"""

from __future__ import annotations

from math import exp, isfinite, log


_EPSILON = 1e-12


def _probability(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("probabilities must be finite numbers")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError("probabilities must lie in [0, 1]")
    return value


def _label(value: bool | int | float) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int) and value in (0, 1):
        return float(value)
    if isinstance(value, float) and value in (0.0, 1.0):
        return value
    raise ValueError("labels must be booleans or 0/1 integers")


def _validated_pairs(probabilities: list[float], labels: list[bool | int | float]) -> list[tuple[float, float]]:
    if len(probabilities) != len(labels) or not probabilities:
        raise ValueError("probabilities and labels must be non-empty and have equal length")
    return [(_probability(probability), _label(label)) for probability, label in zip(probabilities, labels)]


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        return 1.0 / (1.0 + exp(-value))
    exponent = exp(value)
    return exponent / (1.0 + exponent)


def _logit(probability: float) -> float:
    clipped = min(max(probability, _EPSILON), 1.0 - _EPSILON)
    return log(clipped / (1.0 - clipped))


def brier_score(probabilities: list[float], labels: list[bool | int | float]) -> float:
    """Return the mean squared probability error on one fixed evaluation set."""
    pairs = _validated_pairs(probabilities, labels)
    return sum((probability - label) ** 2 for probability, label in pairs) / len(pairs)


def log_loss(probabilities: list[float], labels: list[bool | int | float]) -> float:
    """Return binary negative log likelihood with finite endpoint handling."""
    pairs = _validated_pairs(probabilities, labels)
    return -sum(
        label * log(min(max(probability, _EPSILON), 1.0 - _EPSILON))
        + (1.0 - label) * log(1.0 - min(max(probability, _EPSILON), 1.0 - _EPSILON))
        for probability, label in pairs
    ) / len(pairs)


class PlattCalibrator:
    """Fit ``sigmoid(a * logit(p) + b)`` on an independent validation set.

    Backtracking makes the teaching implementation deterministic and ensures
    that every accepted full-batch update does not increase the regularised
    validation objective.  It is intentionally not a substitute for a mature
    production calibration library.
    """

    def __init__(self, learning_rate: float = 0.1, max_steps: int = 500, l2: float = 1e-6):
        if (isinstance(learning_rate, bool) or not isinstance(learning_rate, (int, float))
                or not isfinite(learning_rate) or learning_rate <= 0.0):
            raise ValueError("learning_rate must be a positive finite number")
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        if isinstance(l2, bool) or not isinstance(l2, (int, float)) or not isfinite(l2) or l2 < 0.0:
            raise ValueError("l2 must be a non-negative finite number")
        self.learning_rate = float(learning_rate)
        self.max_steps = max_steps
        self.l2 = float(l2)

    def _objective(self, logits: list[float], labels: list[float], slope: float, intercept: float) -> float:
        probabilities = [_sigmoid(slope * value + intercept) for value in logits]
        return log_loss(probabilities, labels) + 0.5 * self.l2 * slope * slope

    def fit(self, probabilities: list[float], labels: list[bool | int]) -> "PlattCalibrator":
        pairs = _validated_pairs(probabilities, labels)
        if len(pairs) < 2 or len({label for _, label in pairs}) < 2:
            raise ValueError("validation data needs at least two examples and both classes")
        logits = [_logit(probability) for probability, _ in pairs]
        targets = [label for _, label in pairs]
        slope, intercept = 1.0, 0.0
        objective = self._objective(logits, targets, slope, intercept)
        self.objective_trace = [objective]

        for _ in range(self.max_steps):
            fitted = [_sigmoid(slope * value + intercept) for value in logits]
            slope_gradient = sum(
                (prediction - target) * value
                for prediction, target, value in zip(fitted, targets, logits)
            ) / len(targets)
            slope_gradient += self.l2 * slope
            intercept_gradient = sum(prediction - target for prediction, target in zip(fitted, targets)) / len(targets)
            step = self.learning_rate
            accepted = False
            while step >= self.learning_rate / 2**20:
                candidate_slope = slope - step * slope_gradient
                candidate_intercept = intercept - step * intercept_gradient
                candidate_objective = self._objective(logits, targets, candidate_slope, candidate_intercept)
                if candidate_objective <= objective:
                    slope, intercept, objective = candidate_slope, candidate_intercept, candidate_objective
                    self.objective_trace.append(objective)
                    accepted = True
                    break
                step /= 2.0
            if not accepted:
                break
            if abs(self.objective_trace[-2] - objective) < 1e-12:
                break

        self.slope = slope
        self.intercept = intercept
        return self

    def predict_proba(self, probabilities: list[float]) -> list[float]:
        """Transform held-out scores after ``fit``; this must not fit again."""
        if not hasattr(self, "slope"):
            raise ValueError("call fit on an independent validation set before prediction")
        return [_sigmoid(self.slope * _logit(_probability(probability)) + self.intercept) for probability in probabilities]
