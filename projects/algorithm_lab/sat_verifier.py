"""一个可审计的 3-SAT 验证器与穷举搜索器，仅用于复杂度教学。"""

from __future__ import annotations

from itertools import product

Literal = int
Clause = tuple[Literal, ...]
Formula = tuple[Clause, ...]
Assignment = dict[int, bool]


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


def find_satisfying_assignment(formula: Formula) -> Assignment | None:
    """枚举所有赋值；这是教学用指数时间基线，不是 SAT 求解器。"""
    names = variables(formula)
    for values in product((False, True), repeat=len(names)):
        candidate = dict(zip(names, values))
        if verify_assignment(formula, candidate):
            return candidate
    return None


if __name__ == "__main__":
    example: Formula = ((1, -2, 3), (-1, 2), (3,))
    witness = find_satisfying_assignment(example)
    print(f"候选解: {witness}")
    print(f"验证结果: {verify_assignment(example, witness) if witness else False}")
