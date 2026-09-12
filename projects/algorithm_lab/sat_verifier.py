"""一个可审计的 3-SAT 验证器与穷举搜索器，仅用于复杂度教学。"""

from __future__ import annotations

from itertools import combinations, product

Literal = int
Clause = tuple[Literal, ...]
Formula = tuple[Clause, ...]
Assignment = dict[int, bool]
INDEPENDENT_SET_CNF_CONTRACT = "independent-set-to-cnf-sat/v1"


def validate_formula(formula: Formula) -> None:
    """拒绝变量 0 与空子句，避免把格式错误误作不可满足实例。"""
    for clause in formula:
        if not clause:
            raise ValueError("空子句使公式立即不可满足；请显式作为边界讨论")
        if any(literal == 0 for literal in clause):
            raise ValueError("文字必须是非零整数；正负号表示是否取反")


def variables(formula: Formula) -> tuple[int, ...]:
    validate_formula(formula)
    return tuple(sorted({abs(literal) for clause in formula for literal in clause}))


def verify_assignment(formula: Formula, assignment: Assignment) -> bool:
    """在线性于文字总数的时间验证一个候选赋值。"""
    required = variables(formula)
    if set(assignment) != set(required):
        raise ValueError("赋值必须恰好包含公式中全部变量")
    if any(type(value) is not bool for value in assignment.values()):
        raise ValueError("每个变量必须映射到 bool")
    return all(any(assignment[abs(literal)] == (literal > 0) for literal in clause) for clause in formula)


def find_satisfying_assignment(formula: Formula, *, max_variables: int = 20) -> Assignment | None:
    """Enumerate assignments under an explicit teaching-resource budget.

    The bound is an API safety contract, not a claim about SAT's theoretical
    complexity.  It prevents an accidental classroom call from silently
    requesting an infeasible ``2**n`` search.
    """
    names = variables(formula)
    if not isinstance(max_variables, int) or isinstance(max_variables, bool) or max_variables < 0:
        raise ValueError("max_variables must be a non-negative integer")
    if len(names) > max_variables:
        raise ValueError("formula exceeds the teaching exhaustive-search variable limit")
    for values in product((False, True), repeat=len(names)):
        candidate = dict(zip(names, values))
        if verify_assignment(formula, candidate):
            return candidate
    return None


def _normalize_independent_set_instance(vertices, edges, size):
    if (not isinstance(vertices, (list, tuple)) or not vertices
            or any(not isinstance(vertex, str) or not vertex for vertex in vertices)
            or len(set(vertices)) != len(vertices)):
        raise ValueError("vertices must be a non-empty sequence of unique non-empty strings")
    if not isinstance(size, int) or isinstance(size, bool) or not 0 <= size <= len(vertices):
        raise ValueError("size must be an integer between zero and the vertex count")
    if not isinstance(edges, (list, tuple)):
        raise ValueError("edges must be a sequence of endpoint pairs")
    order = {vertex: index for index, vertex in enumerate(vertices)}
    normalized = set()
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError("each edge must contain exactly two endpoints")
        left, right = edge
        if left not in order or right not in order or left == right:
            raise ValueError("edges must join two distinct declared vertices")
        normalized.add(tuple(sorted((left, right), key=order.__getitem__)))
    return tuple(vertices), tuple(sorted(normalized, key=lambda edge: (order[edge[0]], order[edge[1]]))), size


def independent_set_to_cnf(vertices, edges, size: int) -> Formula:
    """Reduce independent-set decision to CNF-SAT using ordered selection slots.

    Literal ``x(slot, vertex)`` means that slot selects that vertex.  The
    construction is polynomial: it has ``size * |V|`` variables and a
    quadratic number of pairwise exclusion clauses.  It intentionally targets
    general CNF-SAT; a separate gadget construction is needed to make every
    clause have exactly three literals.
    """
    vertices, edges, size = _normalize_independent_set_instance(vertices, edges, size)
    count = len(vertices)

    def literal(slot, vertex_index):
        return slot * count + vertex_index + 1

    clauses = []
    # Every slot chooses at least one vertex, and no slot chooses two.
    for slot in range(size):
        clauses.append(tuple(literal(slot, index) for index in range(count)))
        for left, right in combinations(range(count), 2):
            clauses.append((-literal(slot, left), -literal(slot, right)))
    # Different slots may not repeat a vertex or choose adjacent vertices.
    for first_slot, second_slot in combinations(range(size), 2):
        for vertex_index in range(count):
            clauses.append((-literal(first_slot, vertex_index), -literal(second_slot, vertex_index)))
        for left, right in edges:
            left_index, right_index = vertices.index(left), vertices.index(right)
            clauses.append((-literal(first_slot, left_index), -literal(second_slot, right_index)))
            clauses.append((-literal(first_slot, right_index), -literal(second_slot, left_index)))
    return tuple(clauses)


def _decode_slots(vertices, size, assignment):
    count = len(vertices)
    selected = []
    for slot in range(size):
        choices = [vertices[index] for index in range(count) if assignment[slot * count + index + 1]]
        if len(choices) != 1:
            raise ValueError("assignment does not choose exactly one vertex per slot")
        selected.append(choices[0])
    return tuple(selected)


def _has_independent_set(vertices, edges, size):
    edge_set = {frozenset(edge) for edge in edges}
    return any(all(frozenset(pair) not in edge_set for pair in combinations(candidate, 2))
               for candidate in combinations(vertices, size))


def independent_set_cnf_report(vertices, edges, size: int, *, max_variables: int = 20) -> dict[str, object]:
    """Build and small-scale-audit the independent-set-to-CNF reduction.

    The exhaustive SAT call and subset oracle are deliberately bounded teaching
    evidence.  The reduction proof itself is the slot construction and the
    two directions explained in the lesson, not a claim that brute force proves
    NP-completeness for arbitrary graphs.
    """
    vertices, edges, size = _normalize_independent_set_instance(vertices, edges, size)
    formula = independent_set_to_cnf(vertices, edges, size)
    assignment = find_satisfying_assignment(formula, max_variables=max_variables)
    selected = None if assignment is None else _decode_slots(vertices, size, assignment)
    oracle = _has_independent_set(vertices, edges, size)
    return {
        "contract": INDEPENDENT_SET_CNF_CONTRACT,
        "vertices": vertices,
        "edges": edges,
        "size": size,
        "formula": formula,
        "variable_count": len(vertices) * size,
        "clause_count": len(formula),
        "cnf_satisfiable": assignment is not None,
        "decoded_independent_set": selected,
        "small_instance_independent_set_oracle": oracle,
        "yes_no_agree": (assignment is not None) == oracle,
        "interpretation": "bounded_exhaustive_audit_of_independent_set_to_cnf_sat_reduction",
    }


def independent_set_cnf_certificate(vertices, edges, size: int, report: object) -> bool:
    """Replay construction, SAT enumeration, decoding, and the small oracle."""
    if not isinstance(report, dict) or report.get("contract") != INDEPENDENT_SET_CNF_CONTRACT:
        return False
    try:
        # The variable budget is derivable from the formula, so the certificate
        # can replay exactly the report's declared construction without taking
        # an untrusted budget field from the report.
        return report == independent_set_cnf_report(
            vertices, edges, size, max_variables=report["variable_count"],
        )
    except (KeyError, TypeError, ValueError):
        return False


if __name__ == "__main__":
    example: Formula = ((1, -2, 3), (-1, 2), (3,))
    witness = find_satisfying_assignment(example)
    print(f"候选解: {witness}")
    print(f"验证结果: {verify_assignment(example, witness) if witness else False}")
