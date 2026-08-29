"""Rank-one alternating least squares for a tiny, incomplete ratings matrix.

This is a deterministic teaching implementation, not a production recommender.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt


Rating = float | None


@dataclass(frozen=True)
class AlsEvent:
    """One full user-then-item alternating-least-squares update."""

    iteration: int
    user_factors: tuple[float, ...]
    item_factors: tuple[float, ...]
    observed_squared_error: float


@dataclass(frozen=True)
class RankOneAlsReport:
    """Factors, all predictions and a replayable fitting trace."""

    user_factors: tuple[float, ...]
    item_factors: tuple[float, ...]
    predictions: tuple[tuple[float, ...], ...]
    observed_rmse: float
    events: tuple[AlsEvent, ...]


def _validate(ratings: list[list[Rating]], iterations: int, regularization: float) -> tuple[int, int]:
    if (not ratings or not ratings[0] or any(len(row) != len(ratings[0]) for row in ratings)
            or not isinstance(iterations, int) or isinstance(iterations, bool) or iterations <= 0
            or not isfinite(regularization) or regularization <= 0):
        raise ValueError("ratings must be rectangular; iterations and regularization must be positive")
    users, items = len(ratings), len(ratings[0])
    for row in ratings:
        for value in row:
            if value is not None and (not isinstance(value, (int, float)) or not isfinite(value)):
                raise ValueError("observed ratings must be finite numbers or None")
    if any(all(value is None for value in row) for row in ratings):
        raise ValueError("cold-start users need side information outside this rank-one model")
    if any(all(ratings[user][item] is None for user in range(users)) for item in range(items)):
        raise ValueError("cold-start items need side information outside this rank-one model")
    return users, items


def _squared_error(ratings: list[list[Rating]], users: list[float], items: list[float]) -> tuple[float, int]:
    squared_error = 0.0
    observations = 0
    for user, row in enumerate(ratings):
        for item, rating in enumerate(row):
            if rating is not None:
                squared_error += (float(rating) - users[user] * items[item]) ** 2
                observations += 1
    return squared_error, observations


def rank_one_als_report(
    ratings: list[list[Rating]], *, iterations: int = 12, regularization: float = 0.1,
) -> RankOneAlsReport:
    """Fit ``rating[user,item] ≈ user_factor[user] * item_factor[item]``.

    Each scalar update is the closed-form ridge least-squares minimizer while
    the opposite factor vector is held fixed. The global nonconvex problem can
    still have scale ambiguity and local behaviour; this model is deliberately
    small enough to inspect every update.
    """
    users_count, items_count = _validate(ratings, iterations, regularization)
    users = [1.0] * users_count
    items = [1.0] * items_count
    events: list[AlsEvent] = []
    for iteration in range(1, iterations + 1):
        for user, row in enumerate(ratings):
            numerator = sum(float(rating) * items[item] for item, rating in enumerate(row) if rating is not None)
            denominator = regularization + sum(items[item] ** 2 for item, rating in enumerate(row) if rating is not None)
            users[user] = numerator / denominator
        for item in range(items_count):
            numerator = sum(float(ratings[user][item]) * users[user]
                            for user in range(users_count) if ratings[user][item] is not None)
            denominator = regularization + sum(users[user] ** 2
                                             for user in range(users_count) if ratings[user][item] is not None)
            items[item] = numerator / denominator
        squared_error, _ = _squared_error(ratings, users, items)
        events.append(AlsEvent(iteration, tuple(users), tuple(items), squared_error))
    squared_error, observations = _squared_error(ratings, users, items)
    predictions = tuple(tuple(user_factor * item_factor for item_factor in items) for user_factor in users)
    return RankOneAlsReport(tuple(users), tuple(items), predictions, sqrt(squared_error / observations), tuple(events))


def rank_one_als_trace_certificate(
    ratings: list[list[Rating]], report: RankOneAlsReport, *, iterations: int = 12, regularization: float = 0.1,
) -> bool:
    """Replay all coordinate minimizers and reject a tampered ALS report."""
    try:
        users_count, items_count = _validate(ratings, iterations, regularization)
        if not isinstance(report, RankOneAlsReport) or len(report.events) != iterations:
            return False
        users = [1.0] * users_count
        items = [1.0] * items_count
        for iteration, event in enumerate(report.events, start=1):
            for user, row in enumerate(ratings):
                numerator = sum(float(rating) * items[item] for item, rating in enumerate(row) if rating is not None)
                denominator = regularization + sum(items[item] ** 2 for item, rating in enumerate(row) if rating is not None)
                users[user] = numerator / denominator
            for item in range(items_count):
                numerator = sum(float(ratings[user][item]) * users[user]
                                for user in range(users_count) if ratings[user][item] is not None)
                denominator = regularization + sum(users[user] ** 2
                                                 for user in range(users_count) if ratings[user][item] is not None)
                items[item] = numerator / denominator
            squared_error, _ = _squared_error(ratings, users, items)
            if event != AlsEvent(iteration, tuple(users), tuple(items), squared_error):
                return False
        squared_error, observations = _squared_error(ratings, users, items)
        predictions = tuple(tuple(user_factor * item_factor for item_factor in items) for user_factor in users)
        return report == RankOneAlsReport(
            tuple(users), tuple(items), predictions, sqrt(squared_error / observations), tuple(report.events),
        )
    except (ArithmeticError, TypeError, ValueError):
        return False
