"""Compare vector rankings when the task values direction or absolute distance."""

from __future__ import annotations

from math import isfinite, sqrt


def _vector(values, field):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError(f"{field} must be a non-empty vector")
    normalized = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{field} entries must be finite numbers")
        normalized.append(float(value))
    return tuple(normalized)


def compare_similarity_metrics(query, candidates):
    """Rank labeled vectors by cosine alignment and Euclidean closeness.

    The function intentionally does not pick a universally "correct" ranking.
    Its result makes the task assumption visible: cosine ignores scale, while
    Euclidean distance treats scale difference as part of the mismatch.
    """
    query = _vector(query, "query")
    query_norm = sqrt(sum(value * value for value in query))
    if query_norm == 0.0:
        raise ValueError("query must be non-zero because cosine is undefined")
    if not isinstance(candidates, list) or len(candidates) < 2:
        raise ValueError("candidates must contain at least two labeled vectors")
    seen, rows = set(), []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict) or set(candidate) != {"label", "vector"}:
            raise ValueError("each candidate must contain exactly label and vector")
        label = candidate["label"]
        if not isinstance(label, str) or not label or label in seen:
            raise ValueError("candidate labels must be unique non-empty strings")
        vector = _vector(candidate["vector"], f"candidate {label}")
        if len(vector) != len(query):
            raise ValueError("all candidate vectors must match query dimension")
        norm = sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            raise ValueError("candidate vectors must be non-zero because cosine is undefined")
        dot = sum(left * right for left, right in zip(query, vector))
        rows.append({
            "label": label,
            "cosine_similarity": dot / (query_norm * norm),
            "euclidean_distance": sqrt(sum((left - right) ** 2 for left, right in zip(query, vector))),
            "input_index": index,
        })
        seen.add(label)
    cosine_ranking = [row["label"] for row in sorted(rows, key=lambda row: (-row["cosine_similarity"], row["input_index"]))]
    distance_ranking = [row["label"] for row in sorted(rows, key=lambda row: (row["euclidean_distance"], row["input_index"]))]
    return {
        "query": query,
        "candidates": rows,
        "cosine_ranking": cosine_ranking,
        "euclidean_ranking": distance_ranking,
        "same_top_choice": cosine_ranking[0] == distance_ranking[0],
        "decision_boundary": "choose_cosine_for_direction_only; choose_euclidean_when_magnitude_is_meaningful",
    }


def similarity_metrics_certificate(query, candidates, report):
    """Independently rebuild a finite ranking comparison and its scope label.

    A valid result means only that the displayed rankings and decision boundary
    follow the declared vectors and tie policy.  It deliberately does not
    decide which metric a product should use.
    """
    if not isinstance(report, dict):
        return False
    try:
        return report == compare_similarity_metrics(query, candidates)
    except (KeyError, TypeError, ValueError):
        return False
