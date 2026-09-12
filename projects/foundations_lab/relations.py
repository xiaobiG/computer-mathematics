"""Finite binary relations and their adjacency-matrix representations for teaching."""
from __future__ import annotations


CONTRACT = "finite-relation-matrix/v1"
BOOLEAN_COMPOSITION_CONTRACT = "boolean-relation-composition/v1"


def _domain(value):
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value) or len(set(value)) != len(value):
        raise ValueError("domain must be a non-empty duplicate-free list of strings")
    return list(value)


def _pairs(value, domain):
    if not isinstance(value, list):
        raise ValueError("pairs must be a list")
    normalized = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2 or pair[0] not in domain or pair[1] not in domain:
            raise ValueError("each pair must contain two domain members")
        normalized.append(tuple(pair))
    if len(set(normalized)) != len(normalized):
        raise ValueError("pairs must not repeat")
    return normalized


def finite_relation_report(domain, pairs):
    """Report relation properties and its 0/1 matrix under the declared order."""
    members, edges = _domain(domain), _pairs(pairs, domain)
    edge_set = set(edges)
    matrix = [[1 if (left, right) in edge_set else 0 for right in members] for left in members]
    reflexive = all((member, member) in edge_set for member in members)
    symmetric = all((right, left) in edge_set for left, right in edge_set)
    transitive = all((left, final) in edge_set for left, middle in edge_set for middle2, final in edge_set if middle == middle2)
    return {"contract": CONTRACT, "domain": members, "pairs": [list(pair) for pair in edges], "adjacency_matrix": matrix, "properties": {"reflexive": reflexive, "symmetric": symmetric, "transitive": transitive, "equivalence_relation": reflexive and symmetric and transitive}, "matrix_order": members}


def finite_relation_certificate(domain, pairs, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == finite_relation_report(domain, pairs)
    except ValueError:
        return False


def relation_reachability_report(domain, pairs):
    """Compute transitive closure by adding one allowed intermediate at a time."""
    members, edges = _domain(domain), _pairs(pairs, domain)
    reach = set(edges)
    layers = []
    for middle in members:
        before = set(reach)
        reach |= {(left, right) for left, pivot in before for pivot2, right in before if pivot == middle == pivot2}
        layers.append({"intermediate": middle, "new_pairs": [list(pair) for pair in sorted(reach - before)]})
    return {"contract": "relation-reachability/v1", "domain": members, "pairs": [list(pair) for pair in edges], "closure_pairs": [list(pair) for pair in sorted(reach)], "layers": layers, "closure_matrix": [[1 if (left, right) in reach else 0 for right in members] for left in members]}


def relation_reachability_certificate(domain, pairs, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == relation_reachability_report(domain, pairs)
    except ValueError:
        return False


def boolean_relation_composition_report(domain, left_pairs, right_pairs):
    """Compare boolean-matrix composition with sparse adjacency-list traversal."""
    members = _domain(domain)
    left, right = _pairs(left_pairs, members), _pairs(right_pairs, members)
    left_set, right_set = set(left), set(right)
    dense_checks = 0
    composed = set()
    for source in members:
        for target in members:
            exists = False
            for middle in members:
                dense_checks += 1
                if (source, middle) in left_set and (middle, target) in right_set:
                    exists = True
                    break
            if exists:
                composed.add((source, target))
    outgoing = {member: [] for member in members}
    for middle, target in right:
        outgoing[middle].append(target)
    sparse_checks = 0
    sparse_composed = set()
    for source, middle in left:
        for target in outgoing[middle]:
            sparse_checks += 1
            sparse_composed.add((source, target))
    matrix = [[1 if (source, target) in composed else 0 for target in members] for source in members]
    return {
        "contract": BOOLEAN_COMPOSITION_CONTRACT,
        "domain": members,
        "left_pairs": [list(pair) for pair in left],
        "right_pairs": [list(pair) for pair in right],
        "composition_pairs": [list(pair) for pair in sorted(composed)],
        "boolean_product_matrix": matrix,
        "verification": {"dense_and_sparse_pairs_match": composed == sparse_composed},
        "work": {"dense_candidate_checks": dense_checks, "sparse_two_hop_scans": sparse_checks},
        "interpretation": "operation_counts_for_this_snapshot_not_a_general_performance_guarantee",
    }


def boolean_relation_composition_certificate(domain, left_pairs, right_pairs, report):
    if not isinstance(report, dict):
        return False
    try:
        return report == boolean_relation_composition_report(domain, left_pairs, right_pairs)
    except ValueError:
        return False
