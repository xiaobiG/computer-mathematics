"""Finite, replayable counting experiments for the combinatorics lesson."""

from __future__ import annotations

from itertools import combinations


INCLUSION_EXCLUSION_CONTRACT = "finite-inclusion-exclusion/v1"
PIGEONHOLE_CONTRACT = "finite-pigeonhole-collision/v1"


def _validate_universe_and_sets(universe: object, named_sets: object) -> tuple[tuple[str, ...], tuple[tuple[str, tuple[str, ...]], ...]]:
    if (not isinstance(universe, list) or not universe
            or any(not isinstance(item, str) for item in universe)
            or len(set(universe)) != len(universe)):
        raise ValueError("universe must be a nonempty list of distinct string labels")
    if (not isinstance(named_sets, dict) or not 2 <= len(named_sets) <= 5
            or any(not isinstance(name, str) or not isinstance(members, list)
                   for name, members in named_sets.items())):
        raise ValueError("named_sets must contain two to five string-keyed member lists")
    universe_tuple = tuple(universe)
    allowed = set(universe_tuple)
    normalized: list[tuple[str, tuple[str, ...]]] = []
    for name in sorted(named_sets):
        members = named_sets[name]
        if (any(not isinstance(member, str) or member not in allowed for member in members)
                or len(set(members)) != len(members)):
            raise ValueError("each set must list distinct members from the declared universe")
        member_set = set(members)
        normalized.append((name, tuple(item for item in universe_tuple if item in member_set)))
    return universe_tuple, tuple(normalized)


def inclusion_exclusion_report(universe: object, named_sets: object) -> dict[str, object]:
    """Count a finite union directly and through all inclusion--exclusion terms."""
    universe_values, normalized_sets = _validate_universe_and_sets(universe, named_sets)
    member_sets = {name: set(members) for name, members in normalized_sets}
    names = tuple(name for name, _ in normalized_sets)
    terms: list[dict[str, object]] = []
    for width in range(1, len(names) + 1):
        sign = 1 if width % 2 else -1
        for chosen in combinations(names, width):
            intersection = set(universe_values)
            for name in chosen:
                intersection &= member_sets[name]
            ordered_intersection = tuple(item for item in universe_values if item in intersection)
            terms.append({
                "selected_sets": chosen,
                "intersection": ordered_intersection,
                "size": len(ordered_intersection),
                "sign": sign,
                "signed_contribution": sign * len(ordered_intersection),
            })
    direct_union = tuple(
        item for item in universe_values if any(item in members for _, members in normalized_sets)
    )
    inclusion_exclusion_count = sum(term["signed_contribution"] for term in terms)
    return {
        "contract": INCLUSION_EXCLUSION_CONTRACT,
        "universe": universe_values,
        "sets": normalized_sets,
        "terms": tuple(terms),
        "direct_union": direct_union,
        "direct_union_count": len(direct_union),
        "inclusion_exclusion_count": inclusion_exclusion_count,
        "counts_match": len(direct_union) == inclusion_exclusion_count,
    }


def inclusion_exclusion_certificate(universe: object, named_sets: object, report: object) -> bool:
    """Replay every signed intersection instead of trusting a displayed count."""
    if not isinstance(report, dict):
        return False
    try:
        return report == inclusion_exclusion_report(universe, named_sets)
    except (TypeError, ValueError):
        return False


def pigeonhole_collision_report(assignments: object, bins: object) -> dict[str, object]:
    """Expose a concrete collision required when more items than bins are assigned."""
    if (not isinstance(assignments, dict) or not assignments
            or any(not isinstance(item, str) or not isinstance(bucket, str)
                   for item, bucket in assignments.items())):
        raise ValueError("assignments must be a nonempty string-item to string-bin mapping")
    if (not isinstance(bins, list) or not bins or any(not isinstance(bucket, str) for bucket in bins)
            or len(set(bins)) != len(bins) or any(bucket not in bins for bucket in assignments.values())):
        raise ValueError("bins must be a nonempty distinct string list covering every assignment")
    groups: dict[str, list[str]] = {}
    for item in sorted(assignments):
        groups.setdefault(assignments[item], []).append(item)
    normalized_groups = tuple((bucket, tuple(items)) for bucket, items in sorted(groups.items()))
    forced_collision = len(assignments) > len(bins)
    witness = next(((bucket, items) for bucket, items in normalized_groups if len(items) >= 2), None)
    return {
        "contract": PIGEONHOLE_CONTRACT,
        "assignments": tuple((item, assignments[item]) for item in sorted(assignments)),
        "item_count": len(assignments),
        "bins": tuple(bins),
        "bin_count": len(bins),
        "occupied_bin_count": len(groups),
        "groups": normalized_groups,
        "collision_is_forced": forced_collision,
        "collision_witness": witness,
        "forced_collision_has_witness": not forced_collision or witness is not None,
    }


def pigeonhole_collision_certificate(assignments: object, bins: object, report: object) -> bool:
    """Rebuild bucket groups and the forced-collision conclusion."""
    if not isinstance(report, dict):
        return False
    try:
        return report == pigeonhole_collision_report(assignments, bins)
    except (TypeError, ValueError):
        return False
