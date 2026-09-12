"""Finite binary relations and their adjacency-matrix representations for teaching."""
from __future__ import annotations


CONTRACT = "finite-relation-matrix/v1"


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
