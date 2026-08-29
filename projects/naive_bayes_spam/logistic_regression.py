"""A tiny batch logistic-regression implementation for teaching.

It intentionally favours an auditable gradient calculation over production
features such as regularisation, sparse inputs, or an adaptive optimiser.
"""

from __future__ import annotations

from math import exp, log


def sigmoid(score: float) -> float:
    """Return 1 / (1 + exp(-score)) without overflowing for large scores."""
    if score >= 0:
        return 1 / (1 + exp(-score))
    exponent = exp(score)
    return exponent / (1 + exponent)


def binary_cross_entropy(probability: float, target: bool) -> float:
    """Return -log likelihood for one Bernoulli observation.

    A probability of exactly zero or one makes the logarithm undefined.  That
    is a useful teaching signal: callers should use sigmoid outputs, not raw
    hard classifications, when optimising this loss.
    """
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must be strictly between zero and one")
    return -(float(target) * log(probability) + (1 - float(target)) * log(1 - probability))


class LogisticRegression:
    """Binary logistic regression trained with full-batch gradient descent."""

    def fit(
        self,
        samples: list[tuple[list[float], bool]],
        learning_rate: float = 0.5,
        steps: int = 500,
    ) -> "LogisticRegression":
        if not samples:
            raise ValueError("training data must not be empty")
        if learning_rate <= 0 or steps <= 0:
            raise ValueError("learning_rate and steps must be positive")
        dimension = len(samples[0][0])
        if dimension == 0 or any(len(features) != dimension for features, _ in samples):
            raise ValueError("every sample needs the same nonzero feature dimension")

        self.weights = [0.0] * (dimension + 1)  # intercept, then one coefficient per feature
        for _ in range(steps):
            gradient = [0.0] * len(self.weights)
            for features, target in samples:
                residual = self.predict_proba(features) - float(target)
                gradient[0] += residual
                for index, feature in enumerate(features, start=1):
                    gradient[index] += residual * feature
            for index, value in enumerate(gradient):
                self.weights[index] -= learning_rate * value / len(samples)
        return self

    def predict_proba(self, features: list[float]) -> float:
        if not hasattr(self, "weights"):
            raise ValueError("call fit before prediction")
        if len(features) != len(self.weights) - 1:
            raise ValueError("feature dimension does not match fitted model")
        return sigmoid(self.weights[0] + sum(weight * feature for weight, feature in zip(self.weights[1:], features)))

    def predict(self, features: list[float]) -> bool:
        return self.predict_proba(features) >= 0.5

    def loss(self, samples: list[tuple[list[float], bool]]) -> float:
        if not samples:
            raise ValueError("evaluation data must not be empty")
        return sum(binary_cross_entropy(self.predict_proba(features), target) for features, target in samples) / len(samples)
