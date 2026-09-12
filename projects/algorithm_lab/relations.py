"""Finite relation checks for equivalence classes and partial-order lessons."""

from __future__ import annotations

from typing import Hashable


Item = Hashable
Relation = set[tuple[Item, Item]]
RELATION_DIAGNOSTIC_CONTRACT = "finite-relation-diagnostic/v1"


def _validate(items: set[Item], relation: Relation) -> None:
    if not isinstance(items, set):
        raise ValueError("items must be a set")
    if not isinstance(relation, set) or any(not isinstance(pair, tuple) or len(pair) != 2
                                            or pair[0] not in items or pair[1] not in items
                                            for pair in relation):
        raise ValueError("relation must contain only item pairs")


def _ordered(values):
    """Give classroom reports a repeatable order without restricting hashables."""
    return sorted(values, key=lambda value: (type(value).__name__, repr(value)))


def relation_report(items: set[Item], relation: Relation) -> dict[str, object]:
    """Check finite properties and preserve a concrete witness for every failure."""
    _validate(items, relation)
    ordered_items = _ordered(items)
    ordered_relation = _ordered(relation)
    missing_reflexive = next((item for item in ordered_items if (item, item) not in relation), None)
    missing_symmetric = next(((left, right) for left, right in ordered_relation
                              if (right, left) not in relation), None)
    antisymmetric_pair = next(((left, right) for left, right in ordered_relation
                               if left != right and (right, left) in relation), None)
    missing_transitive = next(((left, middle, last) for left, middle in ordered_relation
                               for middle_again, last in ordered_relation
                               if middle == middle_again and (left, last) not in relation), None)
    reflexive = missing_reflexive is None
    symmetric = missing_symmetric is None
    antisymmetric = antisymmetric_pair is None
    transitive = missing_transitive is None
    return {
        "contract": RELATION_DIAGNOSTIC_CONTRACT,
        "reflexive": reflexive,
        "symmetric": symmetric,
        "antisymmetric": antisymmetric,
        "transitive": transitive,
        "equivalence": reflexive and symmetric and transitive,
        "partial_order": reflexive and antisymmetric and transitive,
        "counterexamples": {
            "missing_reflexive_pair": None if missing_reflexive is None else (missing_reflexive, missing_reflexive),
            "missing_symmetric_reverse": missing_symmetric,
            "antisymmetry_conflict": antisymmetric_pair,
            "missing_transitive_pair": missing_transitive,
        },
    }


def relation_report_certificate(items: set[Item], relation: Relation, report: object) -> bool:
    """Rebuild diagnostic booleans and witnesses rather than trusting either."""
    if not isinstance(report, dict) or report.get("contract") != RELATION_DIAGNOSTIC_CONTRACT:
        return False
    try:
        return report == relation_report(items, relation)
    except (TypeError, ValueError):
        return False


def equivalence_classes(items: set[Item], relation: Relation) -> list[set[Item]]:
    """Partition items into classes, rejecting a relation that is not equivalent."""
    if not relation_report(items, relation)["equivalence"]:
        raise ValueError("relation must be an equivalence relation")
    unseen = set(items)
    classes = []
    while unseen:
        representative = next(iter(unseen))
        current = {item for item in items if (representative, item) in relation}
        classes.append(current)
        unseen -= current
    return classes
