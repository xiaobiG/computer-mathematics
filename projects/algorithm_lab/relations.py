"""Finite relation checks for equivalence classes and partial-order lessons."""

from __future__ import annotations

from typing import Hashable


Item = Hashable
Relation = set[tuple[Item, Item]]


def _validate(items: set[Item], relation: Relation) -> None:
    if not isinstance(items, set):
        raise ValueError("items must be a set")
    if not isinstance(relation, set) or any(not isinstance(pair, tuple) or len(pair) != 2
                                            or pair[0] not in items or pair[1] not in items
                                            for pair in relation):
        raise ValueError("relation must contain only item pairs")


def relation_report(items: set[Item], relation: Relation) -> dict[str, bool]:
    """Check finite relation properties directly from their quantified definitions."""
    _validate(items, relation)
    reflexive = all((item, item) in relation for item in items)
    symmetric = all((right, left) in relation for left, right in relation)
    antisymmetric = all(left == right or (right, left) not in relation for left, right in relation)
    transitive = all((left, last) in relation
                     for left, middle in relation for middle_again, last in relation
                     if middle == middle_again)
    return {
        "reflexive": reflexive,
        "symmetric": symmetric,
        "antisymmetric": antisymmetric,
        "transitive": transitive,
        "equivalence": reflexive and symmetric and transitive,
        "partial_order": reflexive and antisymmetric and transitive,
    }


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
