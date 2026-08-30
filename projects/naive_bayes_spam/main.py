"""A small, auditable multinomial Naive Bayes classifier for teaching."""

from __future__ import annotations

from collections import Counter
from math import exp, isfinite, log, sqrt
from re import findall


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]", text)]


class NaiveBayesSpam:
    def fit(self, samples: list[tuple[str, bool]]):
        if not samples or not any(label for _, label in samples) or not any(not label for _, label in samples):
            raise ValueError("training data needs both spam and ham samples")
        self.document_count = Counter(label for _, label in samples)
        self.words = {True: Counter(), False: Counter()}
        self.total_words = Counter()
        self.vocabulary = set()
        for text, label in samples:
            tokens = tokenize(text)
            self.words[label].update(tokens)
            self.total_words[label] += len(tokens)
            self.vocabulary.update(tokens)
        return self

    def log_scores(self, text: str) -> dict[bool, float]:
        if not hasattr(self, "document_count"):
            raise ValueError("call fit before prediction")
        total_documents = sum(self.document_count.values())
        vocabulary_size = len(self.vocabulary) + 1
        scores = {}
        for label in (False, True):
            score = log(self.document_count[label] / total_documents)
            denominator = self.total_words[label] + vocabulary_size
            for token in tokenize(text):
                score += log((self.words[label][token] + 1) / denominator)
            scores[label] = score
        return scores

    def predict(self, text: str) -> bool:
        return self.predict_proba(text) >= 0.5

    def predict_proba(self, text: str) -> float:
        """Return the model's spam posterior under its naive assumptions.

        The two log scores are unnormalised log posteriors.  Subtracting them
        before applying the logistic function avoids exponentiating two very
        small numbers independently.
        """
        scores = self.log_scores(text)
        difference = scores[True] - scores[False]
        if difference >= 0:
            return 1 / (1 + exp(-difference))
        odds = exp(difference)
        return odds / (1 + odds)


def confusion_matrix(model: NaiveBayesSpam, samples: list[tuple[str, bool]]) -> dict[str, int]:
    result = Counter()
    for text, actual in samples:
        predicted = model.predict(text)
        result[("tp" if actual else "fp") if predicted else ("fn" if actual else "tn")] += 1
    return {name: result[name] for name in ("tp", "fp", "tn", "fn")}


def classification_metrics(model: NaiveBayesSpam, samples: list[tuple[str, bool]]) -> dict[str, float]:
    """Return threshold-0.5 precision, recall, F1 and Brier score.

    Brier score is the mean squared error of probability forecasts, so unlike
    accuracy it continues to distinguish a hesitant 0.51 forecast from 0.99.
    """
    if not samples:
        raise ValueError("evaluation data must not be empty")
    matrix = confusion_matrix(model, samples)
    precision_denominator = matrix["tp"] + matrix["fp"]
    recall_denominator = matrix["tp"] + matrix["fn"]
    precision = matrix["tp"] / precision_denominator if precision_denominator else 0.0
    recall = matrix["tp"] / recall_denominator if recall_denominator else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    brier = sum((model.predict_proba(text) - float(actual)) ** 2 for text, actual in samples) / len(samples)
    return {"precision": precision, "recall": recall, "f1": f1, "brier": brier}


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Return the Wilson score interval for a Bernoulli proportion.

    Unlike the symmetric Wald interval, this stays inside ``[0, 1]`` and is
    meaningful at the boundary counts ``0`` and ``total``.  The default
    ``z=1.96`` is the usual approximately 95% normal critical value; it is a
    reporting convention, not a proof that a model is calibrated.
    """
    if not isinstance(successes, int) or isinstance(successes, bool) or not isinstance(total, int) or isinstance(total, bool):
        raise ValueError("successes and total must be integers")
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("require 0 <= successes <= total and total > 0")
    if not isinstance(z, (int, float)) or isinstance(z, bool) or not isfinite(z) or z <= 0:
        raise ValueError("z must be a positive finite number")
    proportion = successes / total
    z_squared = z * z
    denominator = 1.0 + z_squared / total
    center = (proportion + z_squared / (2.0 * total)) / denominator
    radius = z * sqrt((proportion * (1.0 - proportion) + z_squared / (4.0 * total)) / total) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def reliability_bins(
    model: NaiveBayesSpam, samples: list[tuple[str, bool]], bins: int = 10
) -> list[dict[str, float | int]]:
    """Group forecasts into equal-width bins for a reliability diagram.

    Each returned row contains the mean predicted probability and empirical
    positive rate.  Empty bins are omitted: treating them as zero-positive
    observations would fabricate evidence.
    """
    if bins <= 0:
        raise ValueError("bins must be positive")
    grouped: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for text, actual in samples:
        probability = model.predict_proba(text)
        index = min(int(probability * bins), bins - 1)
        grouped[index].append((probability, actual))

    result = []
    for index, group in enumerate(grouped):
        if not group:
            continue
        count = len(group)
        positive_count = sum(actual for _, actual in group)
        wilson_low, wilson_high = wilson_interval(positive_count, count)
        result.append({
            "lower": index / bins,
            "upper": (index + 1) / bins,
            "count": count,
            "mean_prediction": sum(probability for probability, _ in group) / count,
            "positive_count": positive_count,
            "positive_rate": positive_count / count,
            "wilson_low": wilson_low,
            "wilson_high": wilson_high,
        })
    return result
