"""A small, auditable multinomial Naive Bayes classifier for teaching."""

from __future__ import annotations

from collections import Counter
from math import log
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
        scores = self.log_scores(text)
        return scores[True] > scores[False]


def confusion_matrix(model: NaiveBayesSpam, samples: list[tuple[str, bool]]) -> dict[str, int]:
    result = Counter()
    for text, actual in samples:
        predicted = model.predict(text)
        result[("tp" if actual else "fp") if predicted else ("fn" if actual else "tn")] += 1
    return {name: result[name] for name in ("tp", "fp", "tn", "fn")}
