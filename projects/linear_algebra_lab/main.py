"""Teaching implementations for matrix multiplication, elimination and projection."""

from math import isfinite, sqrt


EPSILON = 1e-12


def matmul(left, right):
    """Return left @ right for non-empty rectangular nested lists."""
    if not left or not right or not left[0] or not right[0]:
        raise ValueError("matrices must be non-empty")
    left_width = len(left[0])
    right_width = len(right[0])
    if (any(len(row) != left_width for row in left)
            or any(len(row) != right_width for row in right)):
        raise ValueError("matrices must be rectangular")
    if left_width != len(right):
        raise ValueError("incompatible matrix shapes")
    output = []
    for row in range(len(left)):
        output_row = []
        for column in range(right_width):
            # Keep the textbook's left-to-right scalar accumulation explicit.
            # Built-in sum can apply runtime-specific compensation, which would
            # no longer model the pseudocode or its rounding-order lesson.
            total = 0
            for index in range(left_width):
                total += left[row][index] * right[index][column]
            output_row.append(total)
        output.append(output_row)
    return output


def matrix_composition_certificate(left, right, vector, product, tolerance=EPSILON):
    """Check that a recorded product represents applying ``right`` then ``left``.

    The matrix equality checks every row-column sum against ``matmul``.  The
    second check independently expands both ``left @ (right @ vector)`` and
    ``product @ vector``.  It makes the order of composition observable rather
    than treating the symbol ``AB`` as a memorised rule.
    """
    try:
        if tolerance <= 0 or not isfinite(tolerance):
            return False
        expected_product = matmul(left, right)
        if product != expected_product or len(vector) != len(right[0]):
            return False
        sequential = [
            sum(left[i][k] * sum(right[k][j] * vector[j] for j in range(len(vector)))
                for k in range(len(right)))
            for i in range(len(left))
        ]
        composed = [
            sum(product[i][j] * vector[j] for j in range(len(vector)))
            for i in range(len(product))
        ]
        return all(abs(first - second) <= tolerance * max(1.0, abs(first), abs(second))
                   for first, second in zip(sequential, composed))
    except (IndexError, TypeError, ValueError):
        return False


def _validate_linear_system(matrix, target, epsilon):
    size = len(matrix)
    if size == 0 or len(target) != size or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be square and match target")
    if epsilon <= 0 or not isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in target):
        raise ValueError("matrix and target must be finite")
    return size


def solve_with_pivot_trace(matrix, target, epsilon=EPSILON):
    """Solve Ax=b and record each partial-pivot choice and elimination multiplier.

    ``upper`` is the augmented matrix after each column has been cleared below
    its pivot, making the invariant "same solution set, more triangular form"
    directly inspectable.
    """
    size = _validate_linear_system(matrix, target, epsilon)
    augmented = [list(map(float, row)) + [float(target[i])] for i, row in enumerate(matrix)]
    trace = []
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= epsilon:
            raise ValueError("system does not have a unique solution")
        swapped = pivot != column
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        multipliers = []
        for row in range(column + 1, size):
            factor = augmented[row][column] / pivot_value
            multipliers.append(factor)
            for item in range(column, size + 1):
                augmented[row][item] -= factor * augmented[column][item]
        trace.append({"column": column, "pivot_row": pivot, "swapped": swapped,
                      "multipliers": multipliers, "upper": [row.copy() for row in augmented]})
    result = [0.0] * size
    for row in range(size - 1, -1, -1):
        result[row] = (augmented[row][size] - sum(
            augmented[row][column] * result[column] for column in range(row + 1, size)
        )) / augmented[row][row]
    return result, trace


def pivot_trace_certificate(matrix, target, solution, trace, epsilon=EPSILON):
    """Replay partial pivoting, elimination and back substitution exactly.

    This checks a finite floating-point execution against the stated algorithm.
    It does not prove a tiny residual means the original system is well
    conditioned; that is a separate property of the mathematical problem.
    """
    try:
        size = _validate_linear_system(matrix, target, epsilon)
        if not isinstance(solution, list) or len(solution) != size or not isinstance(trace, list) or len(trace) != size:
            return False
        augmented = [list(map(float, row)) + [float(target[i])] for i, row in enumerate(matrix)]
        for column, event in enumerate(trace):
            pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
            if abs(augmented[pivot][column]) <= epsilon:
                return False
            swapped = pivot != column
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
            pivot_value = augmented[column][column]
            multipliers = []
            for row in range(column + 1, size):
                factor = augmented[row][column] / pivot_value
                multipliers.append(factor)
                for item in range(column, size + 1):
                    augmented[row][item] -= factor * augmented[column][item]
            expected = {
                "column": column,
                "pivot_row": pivot,
                "swapped": swapped,
                "multipliers": multipliers,
                "upper": [row.copy() for row in augmented],
            }
            if event != expected:
                return False
        expected_solution = [0.0] * size
        for row in range(size - 1, -1, -1):
            expected_solution[row] = (augmented[row][size] - sum(
                augmented[row][column] * expected_solution[column] for column in range(row + 1, size)
            )) / augmented[row][row]
        return solution == expected_solution
    except (ArithmeticError, TypeError, ValueError):
        return False


def elimination_invariant_certificate(matrix, target, solution, trace, epsilon=EPSILON):
    """Expose the claims behind a recorded Gaussian-elimination run.

    A replayable trace says that the recorded operations are the ones selected
    by partial pivoting.  This companion certificate separates the teaching
    invariants: every pivot is usable, the final augmented matrix is upper
    triangular, and the returned vector satisfies both the original and final
    systems.  It is deliberately a finite floating-point audit, not a proof
    that a small residual implies a well-conditioned problem.
    """
    empty = {
        "trace_replays": False,
        "pivots_are_nonzero": False,
        "below_pivots_are_zero": False,
        "solution_satisfies_original_system": False,
        "solution_satisfies_upper_system": False,
        "valid": False,
    }
    try:
        size = _validate_linear_system(matrix, target, epsilon)
        if (not isinstance(solution, list) or len(solution) != size
                or not isinstance(trace, list) or len(trace) != size):
            return empty
        trace_replays = pivot_trace_certificate(matrix, target, solution, trace, epsilon)
        final_upper = trace[-1].get("upper") if trace else None
        if not isinstance(final_upper, list) or len(final_upper) != size:
            return empty
        pivots_are_nonzero = all(abs(final_upper[column][column]) > epsilon for column in range(size))
        below_pivots_are_zero = all(
            abs(final_upper[row][column]) <= epsilon
            for column in range(size) for row in range(column + 1, size)
        )
        solution_satisfies_original = all(
            abs(sum(float(value) * solution[column] for column, value in enumerate(row)) - float(target[index]))
            <= epsilon * max(1.0, abs(float(target[index])))
            for index, row in enumerate(matrix)
        )
        solution_satisfies_upper = all(
            abs(sum(final_upper[row][column] * solution[column] for column in range(size)) - final_upper[row][size])
            <= epsilon * max(1.0, abs(final_upper[row][size]))
            for row in range(size)
        )
        return {
            "trace_replays": trace_replays,
            "pivots_are_nonzero": pivots_are_nonzero,
            "below_pivots_are_zero": below_pivots_are_zero,
            "solution_satisfies_original_system": solution_satisfies_original,
            "solution_satisfies_upper_system": solution_satisfies_upper,
            "valid": trace_replays and pivots_are_nonzero and below_pivots_are_zero
            and solution_satisfies_original and solution_satisfies_upper,
        }
    except (ArithmeticError, IndexError, TypeError, ValueError):
        return empty


def solve(matrix, target, epsilon=EPSILON):
    """Solve a square dense system using Gaussian elimination with pivoting."""
    result, _ = solve_with_pivot_trace(matrix, target, epsilon)
    return result


def classify_linear_system(matrix, target, epsilon=EPSILON):
    """Classify a finite rectangular Ax=b as unique, none, or infinitely_many.

    This is a classification aid for small teaching inputs, not a rank-revealing
    production routine for ill-conditioned data.
    """
    if not matrix or len(target) != len(matrix) or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("matrix must be non-empty rectangular and match target")
    if epsilon <= 0 or not isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in target):
        raise ValueError("matrix and target must be finite")
    rows, columns = len(matrix), len(matrix[0])
    augmented = [list(map(float, row)) + [float(target[index])] for index, row in enumerate(matrix)]
    pivot_row = 0
    for column in range(columns):
        if pivot_row == rows:
            break
        pivot = max(range(pivot_row, rows), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= epsilon:
            continue
        augmented[pivot_row], augmented[pivot] = augmented[pivot], augmented[pivot_row]
        for row in range(pivot_row + 1, rows):
            factor = augmented[row][column] / augmented[pivot_row][column]
            for item in range(column, columns + 1):
                augmented[row][item] -= factor * augmented[pivot_row][item]
        pivot_row += 1
    if any(all(abs(value) <= epsilon for value in row[:columns]) and abs(row[columns]) > epsilon for row in augmented):
        return "none"
    return "unique" if pivot_row == columns else "infinitely_many"


def project(vector, direction):
    """Project vector onto a non-zero direction."""
    if len(vector) != len(direction):
        raise ValueError("vectors must have the same dimension")
    denominator = sum(value * value for value in direction)
    if denominator <= EPSILON:
        raise ValueError("direction must be non-zero")
    scale = sum(a * b for a, b in zip(vector, direction)) / denominator
    return [scale * value for value in direction]


def norm(vector):
    return sqrt(sum(value * value for value in vector))


def _validate_orthogonalization_columns(columns, epsilon):
    if (not isinstance(columns, list) or not columns or not isinstance(epsilon, (int, float))
            or isinstance(epsilon, bool) or not isfinite(epsilon) or epsilon <= 0.0):
        raise ValueError("columns must be non-empty and epsilon must be finite and positive")
    if (not all(isinstance(column, list) and column for column in columns)
            or len({len(column) for column in columns}) != 1
            or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value)
                   for column in columns for value in column)):
        raise ValueError("columns must be non-empty, equally sized finite numeric vectors")


def _gram_schmidt_columns(columns, *, modified, epsilon):
    _validate_orthogonalization_columns(columns, epsilon)
    basis, upper = [], [[0.0] * len(columns) for _ in columns]
    for column_index, original in enumerate(columns):
        work = [float(value) for value in original]
        for basis_index, direction in enumerate(basis):
            # Classical GS uses the original column in every coefficient;
            # modified GS updates the residual after each projection.
            source = work if modified else original
            upper[basis_index][column_index] = sum(left * right for left, right in zip(direction, source))
            work = [value - upper[basis_index][column_index] * direction[row]
                    for row, value in enumerate(work)]
        upper[column_index][column_index] = norm(work)
        if upper[column_index][column_index] <= epsilon:
            raise ValueError("columns are linearly dependent at this tolerance")
        basis.append([value / upper[column_index][column_index] for value in work])
    return basis, upper


def _qr_reconstruction_error(columns, basis, upper):
    squared_error = 0.0
    for column_index, column in enumerate(columns):
        for row, expected in enumerate(column):
            actual = sum(basis[basis_index][row] * upper[basis_index][column_index]
                         for basis_index in range(column_index + 1))
            squared_error += (actual - expected) ** 2
    return sqrt(squared_error)


def _orthogonality_defect(basis):
    return max(
        (abs(sum(left * right for left, right in zip(basis[left_index], basis[right_index])))
         for left_index in range(len(basis)) for right_index in range(left_index)),
        default=0.0,
    )


def gram_schmidt_stability_report(columns, epsilon=1e-15):
    """Compare classical and modified Gram--Schmidt on identical columns.

    Both paths return a finite QR reconstruction.  The report makes the
    separate floating-point question visible: how close are the computed Q
    columns to mutually orthogonal directions?
    """
    classical_basis, classical_upper = _gram_schmidt_columns(columns, modified=False, epsilon=epsilon)
    modified_basis, modified_upper = _gram_schmidt_columns(columns, modified=True, epsilon=epsilon)
    classical_defect = _orthogonality_defect(classical_basis)
    modified_defect = _orthogonality_defect(modified_basis)
    return {
        "classical": {
            "orthogonality_defect": classical_defect,
            "qr_reconstruction_error": _qr_reconstruction_error(columns, classical_basis, classical_upper),
        },
        "modified": {
            "orthogonality_defect": modified_defect,
            "qr_reconstruction_error": _qr_reconstruction_error(columns, modified_basis, modified_upper),
        },
        "modified_has_smaller_orthogonality_defect": modified_defect < classical_defect,
    }


def gram_schmidt_stability_certificate(columns, report, epsilon=1e-15):
    """Replay an explicit stability comparison and reject altered defect claims."""
    if not isinstance(report, dict):
        return False
    try:
        return report == gram_schmidt_stability_report(columns, epsilon)
    except (TypeError, ValueError):
        return False


def _integer_matrix_for_exact_arithmetic(matrix, name):
    if not isinstance(matrix, list) or not matrix or not isinstance(matrix[0], list) or not matrix[0]:
        raise ValueError(f"{name} must be a non-empty matrix")
    width = len(matrix[0])
    converted = []
    for row in matrix:
        if not isinstance(row, list) or len(row) != width:
            raise ValueError(f"{name} must be rectangular")
        converted_row = []
        for value in row:
            if (not isinstance(value, (int, float)) or isinstance(value, bool)
                    or not isfinite(value) or not float(value).is_integer()):
                raise ValueError(f"{name} must contain finite integer-valued entries")
            converted_row.append(int(value))
        converted.append(converted_row)
    return converted


def floating_associativity_report(left, middle, right):
    """Contrast one floating execution with exact integer matrix associativity.

    Inputs are integer-valued so the exact calculation describes the same
    mathematical matrices.  Floating products are deliberately evaluated in
    two parenthesizations; differing outputs witness rounding order, not a
    failure of the real-number associativity theorem.
    """
    exact_left = _integer_matrix_for_exact_arithmetic(left, "left")
    exact_middle = _integer_matrix_for_exact_arithmetic(middle, "middle")
    exact_right = _integer_matrix_for_exact_arithmetic(right, "right")
    floating_left_associated = matmul(matmul(left, middle), right)
    floating_right_associated = matmul(left, matmul(middle, right))
    exact_left_associated = matmul(matmul(exact_left, exact_middle), exact_right)
    exact_right_associated = matmul(exact_left, matmul(exact_middle, exact_right))
    return {
        "floating_left_associated": floating_left_associated,
        "floating_right_associated": floating_right_associated,
        "exact_left_associated": exact_left_associated,
        "exact_right_associated": exact_right_associated,
        "floating_associativity_holds": floating_left_associated == floating_right_associated,
        "exact_associativity_holds": exact_left_associated == exact_right_associated,
        "interpretation": "different_floating_parenthesizations_do_not_refute_exact_matrix_associativity",
    }


def floating_associativity_certificate(left, middle, right, report):
    """Recompute both arithmetic models before trusting an associativity claim."""
    if not isinstance(report, dict):
        return False
    try:
        return report == floating_associativity_report(left, middle, right)
    except (TypeError, ValueError):
        return False


def _validate_least_squares_input(matrix, target, epsilon):
    if (not matrix or not matrix[0] or len(target) != len(matrix)
            or any(len(row) != len(matrix[0]) for row in matrix)):
        raise ValueError("matrix must be non-empty rectangular and match target")
    if epsilon <= 0 or not isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in target):
        raise ValueError("matrix and target must be finite")
    rows, columns = len(matrix), len(matrix[0])
    if rows < columns:
        raise ValueError("least squares requires at least as many rows as columns")
    return rows, columns


def _least_squares_residual(matrix, target, solution):
    return [float(target[row]) - sum(matrix[row][column] * solution[column]
                                     for column in range(len(solution)))
            for row in range(len(matrix))]


def _normal_equation_residual(matrix, residual):
    """Return A^T r, which vanishes at a least-squares optimum."""
    return [sum(matrix[row][column] * residual[row] for row in range(len(matrix)))
            for column in range(len(matrix[0]))]


def diagnose_least_squares_case(matrix, target, epsilon=EPSILON):
    """Classify a reader-supplied linear-fit case before choosing a solver.

    The diagnosis separates three questions that are often collapsed: whether
    ``b`` is in the column space, whether the small QR teaching path has full
    column rank, and which invariant a reader should check next.  It is not a
    rank-revealing production solver and deliberately does not invent a
    minimum-norm solution for rank-deficient or underdetermined inputs.
    """
    if (not matrix or not matrix[0] or len(target) != len(matrix)
            or any(len(row) != len(matrix[0]) for row in matrix)):
        raise ValueError("matrix must be non-empty rectangular and match target")
    if epsilon <= 0 or not isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in target):
        raise ValueError("matrix and target must be finite")
    rows, columns = len(matrix), len(matrix[0])
    exact_system_status = classify_linear_system(matrix, target, epsilon)
    base = {
        "shape": (rows, columns),
        "exact_system_status": exact_system_status,
        "target_in_column_space": exact_system_status != "none",
        "full_column_rank_qr_available": False,
        "solution": None,
        "residual": None,
        "residual_norm": None,
        "normal_equation_residual": None,
    }
    if rows < columns:
        return base | {
            "fit_path": "underdetermined_model_requires_explicit_solution_rule",
            "reader_invariant": "state a minimum-norm, sparsity, or other solution rule before solving",
        }
    try:
        solution, residual = least_squares_qr(matrix, target, epsilon)
    except ValueError:
        return base | {
            "fit_path": "rank_revealing_qr_or_svd_required",
            "reader_invariant": "separate column dependence from target reachability before choosing a solution rule",
        }
    residual_norm = norm(residual)
    stationarity = _normal_equation_residual(matrix, residual)
    exact_fit = residual_norm <= epsilon * max(1.0, norm(target))
    return base | {
        "full_column_rank_qr_available": True,
        "solution": solution,
        "residual": residual,
        "residual_norm": residual_norm,
        "normal_equation_residual": stationarity,
        "fit_path": (
            "exact_full_rank_solution" if exact_fit else "qr_projection_for_unreachable_target"
        ),
        "reader_invariant": (
            "verify Ax=b" if exact_fit else "verify A^T(b-Ax)=0 while retaining the nonzero residual"
        ),
    }


def least_squares_normal_equations(matrix, target, epsilon=EPSILON):
    """Solve min ||Ax-b||_2 through A^T A x=A^T b for comparison only.

    Forming the normal equations is useful to expose the derivation, but may
    square conditioning. Prefer :func:`least_squares_qr` in numerical code.
    """
    rows, columns = _validate_least_squares_input(matrix, target, epsilon)
    normal_matrix = [[sum(matrix[row][left] * matrix[row][right] for row in range(rows))
                      for right in range(columns)]
                     for left in range(columns)]
    normal_target = [sum(matrix[row][column] * target[row] for row in range(rows))
                     for column in range(columns)]
    solution = solve(normal_matrix, normal_target, epsilon)
    return solution, _least_squares_residual(matrix, target, solution)


def least_squares_qr(matrix, target, epsilon=EPSILON):
    """Solve min ||Ax-b||_2 with modified Gram--Schmidt and back substitution.

    This small dense teaching implementation requires full column rank.  It
    avoids forming A^T A, whose condition number is roughly squared.
    """
    rows, columns = _validate_least_squares_input(matrix, target, epsilon)
    work_columns = [[float(matrix[row][column]) for row in range(rows)] for column in range(columns)]
    orthonormal, upper = [], [[0.0] * columns for _ in range(columns)]
    for column, work in enumerate(work_columns):
        for basis_index, basis in enumerate(orthonormal):
            upper[basis_index][column] = sum(left * right for left, right in zip(basis, work))
            work = [value - upper[basis_index][column] * basis[row] for row, value in enumerate(work)]
        upper[column][column] = norm(work)
        if upper[column][column] <= epsilon:
            raise ValueError("matrix columns are linearly dependent at this tolerance")
        orthonormal.append([value / upper[column][column] for value in work])
    projected = [sum(value * float(target[row]) for row, value in enumerate(basis)) for basis in orthonormal]
    solution = [0.0] * columns
    for row in range(columns - 1, -1, -1):
        solution[row] = (projected[row] - sum(upper[row][column] * solution[column]
                                               for column in range(row + 1, columns))) / upper[row][row]
    return solution, _least_squares_residual(matrix, target, solution)


def ridge_least_squares(matrix, target, regularization, epsilon=EPSILON):
    """Solve ``min ||Ax-b||^2 + λ||x||^2`` through its shifted normal system.

    This compact implementation makes the changed objective visible; it is not
    a production recommendation to form normal equations.  Unlike the QR
    teaching path, it accepts rank-deficient and wide matrices: for λ > 0 the
    shifted system is mathematically nonsingular.
    """
    if (not matrix or not matrix[0] or len(target) != len(matrix)
            or any(len(row) != len(matrix[0]) for row in matrix)):
        raise ValueError("matrix must be non-empty rectangular and match target")
    if (epsilon <= 0 or not isfinite(epsilon) or regularization <= epsilon
            or not isfinite(regularization)):
        raise ValueError("epsilon and regularization must be finite, with regularization above epsilon")
    if any(not isfinite(value) for row in matrix for value in row) or any(not isfinite(value) for value in target):
        raise ValueError("matrix and target must be finite")
    rows, columns = len(matrix), len(matrix[0])
    shifted_normal_matrix = [
        [sum(matrix[row][left] * matrix[row][right] for row in range(rows))
         + (regularization if left == right else 0.0)
         for right in range(columns)]
        for left in range(columns)
    ]
    normal_target = [sum(matrix[row][column] * target[row] for row in range(rows))
                     for column in range(columns)]
    solution = solve(shifted_normal_matrix, normal_target, epsilon)
    return solution, _least_squares_residual(matrix, target, solution)


def ridge_regularization_report(matrix, target, regularization, epsilon=EPSILON):
    """Expose the distinct objective and first-order condition of ridge fit."""
    solution, residual = ridge_least_squares(matrix, target, regularization, epsilon)
    residual_norm = norm(residual)
    coefficient_norm = norm(solution)
    # A^T(Ax-b) is the squared data-loss gradient, up to the common factor 2.
    data_gradient = [-value for value in _normal_equation_residual(matrix, residual)]
    penalty_gradient = [regularization * value for value in solution]
    regularized_gradient = [data + penalty for data, penalty in zip(data_gradient, penalty_gradient)]
    squared_residual_loss = residual_norm ** 2
    squared_coefficient_penalty = regularization * coefficient_norm ** 2
    return {
        "solution": solution,
        "residual": residual,
        "residual_norm": residual_norm,
        "coefficient_norm": coefficient_norm,
        "squared_residual_loss": squared_residual_loss,
        "squared_coefficient_penalty": squared_coefficient_penalty,
        "regularized_objective": squared_residual_loss + squared_coefficient_penalty,
        "data_gradient": data_gradient,
        "penalty_gradient": penalty_gradient,
        "regularized_gradient": regularized_gradient,
    }


def least_squares_comparison_report(matrix, target, epsilon=EPSILON):
    """Compare normal equations and QR using the same residual certificate."""
    normal_solution, normal_residual = least_squares_normal_equations(matrix, target, epsilon)
    qr_solution, qr_residual = least_squares_qr(matrix, target, epsilon)
    return {
        "normal_solution": normal_solution,
        "qr_solution": qr_solution,
        "normal_residual_norm": norm(normal_residual),
        "qr_residual_norm": norm(qr_residual),
        "normal_normal_equation_residual": _normal_equation_residual(matrix, normal_residual),
        "qr_normal_equation_residual": _normal_equation_residual(matrix, qr_residual),
        "solution_distance": norm([left - right for left, right in zip(normal_solution, qr_solution)]),
    }


def least_squares_report_certificate(matrix, target, report, epsilon=EPSILON):
    """Audit a finite least-squares comparison report.

    The certificate deliberately separates a faithfully replayed report from
    the mathematical first-order condition ``A^T(b-Ax)=0`` for each path.  It
    establishes neither that the data model is appropriate nor that normal
    equations are numerically preferable on an ill-conditioned input.
    """
    empty = {
        "fields_match_recomputed_report": False,
        "normal_solution_is_stationary": False,
        "qr_solution_is_stationary": False,
        "reported_norms_match_residuals": False,
        "valid": False,
    }
    try:
        _validate_least_squares_input(matrix, target, epsilon)
        if not isinstance(report, dict):
            return empty
        expected = least_squares_comparison_report(matrix, target, epsilon)
        if set(report) != set(expected):
            return empty
        fields_match = report == expected
        normal_stationary = all(abs(value) <= epsilon for value in report["normal_normal_equation_residual"])
        qr_stationary = all(abs(value) <= epsilon for value in report["qr_normal_equation_residual"])
        normal_norm = norm(_least_squares_residual(matrix, target, report["normal_solution"]))
        qr_norm = norm(_least_squares_residual(matrix, target, report["qr_solution"]))
        norms_match = (
            abs(report["normal_residual_norm"] - normal_norm) <= epsilon * max(1.0, normal_norm)
            and abs(report["qr_residual_norm"] - qr_norm) <= epsilon * max(1.0, qr_norm)
        )
        return {
            "fields_match_recomputed_report": fields_match,
            "normal_solution_is_stationary": normal_stationary,
            "qr_solution_is_stationary": qr_stationary,
            "reported_norms_match_residuals": norms_match,
            "valid": fields_match and normal_stationary and qr_stationary and norms_match,
        }
    except (ArithmeticError, IndexError, TypeError, ValueError):
        return empty


def dominant_right_singular_vector(matrix, iterations=80, epsilon=EPSILON):
    """Approximate the leading right singular vector by power iteration on A^T A.

    Intended for small dense teaching examples, not a replacement for a robust SVD.
    """
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    width = len(matrix[0])
    vector = [1.0 / sqrt(width)] * width
    for _ in range(iterations):
        av = [sum(value * vector[index] for index, value in enumerate(row)) for row in matrix]
        atav = [sum(row[column] * av[row_index] for row_index, row in enumerate(matrix))
                for column in range(width)]
        length = norm(atav)
        if length <= epsilon:
            raise ValueError("matrix has no non-zero singular direction")
        vector = [value / length for value in atav]
    return vector


def rank_one_approximation(matrix, iterations=80, epsilon=EPSILON):
    """Return sigma, left, right and sigma * left * right^T for a small matrix."""
    right = dominant_right_singular_vector(matrix, iterations, epsilon)
    projected = [sum(value * right[index] for index, value in enumerate(row)) for row in matrix]
    sigma = norm(projected)
    if sigma <= epsilon:
        raise ValueError("matrix has no non-zero singular value")
    left = [value / sigma for value in projected]
    approximation = [[sigma * left[row] * right[column]
                      for column in range(len(right))]
                     for row in range(len(left))]
    return sigma, left, right, approximation


def rank_k_approximation(matrix, rank, iterations=80, epsilon=EPSILON):
    """Use residual deflation to build a small teaching rank-k approximation.

    Each iteration extracts one dominant direction of the current residual.
    This is deliberately simple and only suitable for tiny dense matrices; a
    production image pipeline should use a robust truncated SVD.
    """
    if rank <= 0:
        raise ValueError("rank must be positive")
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    residual = [[float(value) for value in row] for row in matrix]
    approximation = [[0.0 for _ in matrix[0]] for _ in matrix]
    components = []
    for _ in range(rank):
        if frobenius_error(residual, [[0.0 for _ in row] for row in residual]) <= epsilon:
            break
        sigma, left, right, part = rank_one_approximation(residual, iterations, epsilon)
        components.append((sigma, left, right))
        for row in range(len(matrix)):
            for column in range(len(matrix[0])):
                approximation[row][column] += part[row][column]
                residual[row][column] -= part[row][column]
    return components, approximation


def compress_grayscale(matrix, rank, iterations=80, epsilon=EPSILON):
    """Return a low-rank grayscale reconstruction and its Frobenius error."""
    components, approximation = rank_k_approximation(matrix, rank, iterations, epsilon)
    return components, approximation, frobenius_error(matrix, approximation)


def truncated_svd_frobenius_error(singular_values, rank):
    """Return the exact Frobenius error of an exact rank-``rank`` SVD truncation.

    The input is a descending, finite singular spectrum.  Keeping this
    calculation separate from ``rank_k_approximation`` makes the distinction
    between the Eckart--Young theorem and the lab's finite-iteration teaching
    approximation explicit.
    """
    if not isinstance(singular_values, (list, tuple)):
        raise ValueError("singular values must be a sequence")
    if not isinstance(rank, int) or isinstance(rank, bool) or rank < 0:
        raise ValueError("rank must be a non-negative integer")
    if rank > len(singular_values):
        raise ValueError("rank cannot exceed the number of singular values")
    previous = float("inf")
    for value in singular_values:
        if not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
            raise ValueError("singular values must be finite and non-negative")
        if value > previous:
            raise ValueError("singular values must be in non-increasing order")
        previous = value
    return sqrt(sum(value * value for value in singular_values[rank:]))


def numerical_rank_report(singular_values, absolute_tolerance, relative_tolerance):
    """Separate exact rank from two explicitly declared numerical conventions.

    A nonzero singular value contributes to exact rank.  In floating-point
    work, however, treating a small value as usable needs a tolerance and is
    therefore not a scale-free mathematical fact.  This report keeps an
    absolute and a scale-relative convention visible instead of silently
    choosing one.
    """
    if not isinstance(singular_values, (list, tuple)) or not singular_values:
        raise ValueError("singular values must be a non-empty sequence")
    if (not isinstance(absolute_tolerance, (int, float)) or isinstance(absolute_tolerance, bool)
            or not isfinite(absolute_tolerance) or absolute_tolerance < 0
            or not isinstance(relative_tolerance, (int, float)) or isinstance(relative_tolerance, bool)
            or not isfinite(relative_tolerance) or relative_tolerance < 0):
        raise ValueError("rank tolerances must be finite non-negative numbers")
    values = tuple(float(value) for value in singular_values)
    if any(value < 0 or not isfinite(value) for value in values):
        raise ValueError("singular values must be finite and non-negative")
    if any(right > left for left, right in zip(values, values[1:])):
        raise ValueError("singular values must be in non-increasing order")
    absolute_tolerance = float(absolute_tolerance)
    relative_tolerance = float(relative_tolerance)
    scale = values[0]
    relative_threshold = relative_tolerance * scale
    return {
        "singular_values": values,
        "exact_rank": sum(value > 0.0 for value in values),
        "absolute_tolerance": absolute_tolerance,
        "relative_tolerance": relative_tolerance,
        "largest_singular_value": scale,
        "absolute_threshold": absolute_tolerance,
        "relative_threshold": relative_threshold,
        "absolute_numerical_rank": sum(value > absolute_tolerance for value in values),
        "relative_numerical_rank": sum(value > relative_threshold for value in values),
        "interpretation": "numerical_rank_requires_declared_tolerance_and_error_model",
    }


def numerical_rank_scale_comparison(singular_values, scale, absolute_tolerance, relative_tolerance):
    """Show which declared numerical-rank convention survives unit scaling."""
    if (not isinstance(scale, (int, float)) or isinstance(scale, bool)
            or not isfinite(scale) or scale <= 0.0):
        raise ValueError("scale must be a positive finite number")
    original = numerical_rank_report(singular_values, absolute_tolerance, relative_tolerance)
    scaled_values = tuple(value * float(scale) for value in original["singular_values"])
    scaled = numerical_rank_report(scaled_values, absolute_tolerance, relative_tolerance)
    return {
        "original": original,
        "scale": float(scale),
        "scaled": scaled,
        "exact_rank_is_scale_invariant": original["exact_rank"] == scaled["exact_rank"],
        "absolute_rank_is_scale_invariant": (
            original["absolute_numerical_rank"] == scaled["absolute_numerical_rank"]
        ),
        "relative_rank_is_scale_invariant": (
            original["relative_numerical_rank"] == scaled["relative_numerical_rank"]
        ),
    }


def numerical_rank_scale_comparison_certificate(
    singular_values, scale, absolute_tolerance, relative_tolerance, report,
):
    """Replay the spectrum, tolerances and scale before trusting its rank labels."""
    if not isinstance(report, dict):
        return False
    try:
        return report == numerical_rank_scale_comparison(
            singular_values, scale, absolute_tolerance, relative_tolerance,
        )
    except (TypeError, ValueError):
        return False


def low_rank_parameter_report(rows, columns, rank):
    """Compare dense and rank-k factor storage counts for a matrix shape."""
    if (not isinstance(rows, int) or isinstance(rows, bool) or rows <= 0
            or not isinstance(columns, int) or isinstance(columns, bool) or columns <= 0
            or not isinstance(rank, int) or isinstance(rank, bool) or rank < 0):
        raise ValueError("rows and columns must be positive integers and rank non-negative")
    dense = rows * columns
    factors = rank * (rows + columns + 1)
    return {
        "dense_parameters": dense,
        "low_rank_parameters": factors,
        "saved_parameters": dense - factors,
        "has_parameter_savings": factors < dense,
    }


def truncated_svd_report(singular_values, rank, rows, columns):
    """Join exact spectral loss and factor-storage tradeoffs in one lesson report.

    The spectrum describes an *exact* SVD.  It must not be used to certify the
    finite power-iteration approximation returned by ``rank_k_approximation``.
    """
    error = truncated_svd_frobenius_error(singular_values, rank)
    parameters = low_rank_parameter_report(rows, columns, rank)
    total_energy = sum(value * value for value in singular_values)
    retained_energy = sum(value * value for value in singular_values[:rank])
    discarded_energy = total_energy - retained_energy
    return {
        "rank": rank,
        "singular_value_count": len(singular_values),
        "total_spectral_energy": total_energy,
        "retained_spectral_energy": retained_energy,
        "discarded_spectral_energy": discarded_energy,
        "frobenius_error": error,
        "retained_energy_ratio": retained_energy / total_energy if total_energy else 1.0,
        **parameters,
    }


def truncated_svd_report_certificate(singular_values, rank, rows, columns, report, tolerance=EPSILON):
    """Recompute an exact truncation report and expose its independent claims."""
    empty = {
        "fields_match_recomputed_report": False,
        "spectral_energy_splits_into_retained_and_discarded": False,
        "discarded_energy_matches_squared_frobenius_error": False,
        "parameter_tradeoff_is_consistent": False,
        "valid": False,
    }
    try:
        if tolerance <= 0 or not isfinite(tolerance) or not isinstance(report, dict):
            return empty
        expected = truncated_svd_report(singular_values, rank, rows, columns)
        if set(report) != set(expected):
            return empty
        fields_match = all(
            report[key] == value if isinstance(value, (int, bool))
            else isinstance(report[key], (int, float)) and abs(report[key] - value) <= tolerance * max(1.0, abs(value))
            for key, value in expected.items()
        )
        energy_split = abs(report["total_spectral_energy"] - report["retained_spectral_energy"]
                           - report["discarded_spectral_energy"]) <= tolerance * max(1.0, report["total_spectral_energy"])
        error_matches = abs(report["discarded_spectral_energy"] - report["frobenius_error"] ** 2) <= tolerance * max(1.0, report["discarded_spectral_energy"])
        parameter_tradeoff = report["saved_parameters"] == report["dense_parameters"] - report["low_rank_parameters"]
        return {
            "fields_match_recomputed_report": fields_match,
            "spectral_energy_splits_into_retained_and_discarded": energy_split,
            "discarded_energy_matches_squared_frobenius_error": error_matches,
            "parameter_tradeoff_is_consistent": parameter_tradeoff,
            "valid": fields_match and energy_split and error_matches and parameter_tradeoff,
        }
    except (TypeError, ValueError):
        return empty


def image_cosine_similarity(left, right):
    """Compare same-shaped grayscale matrices as flattened vectors; zero images score 0."""
    if (not left or not right or len(left) != len(right)
            or any(len(row) != len(left[0]) for row in left)
            or any(len(row) != len(right[0]) for row in right)
            or len(left[0]) != len(right[0])):
        raise ValueError("images must be non-empty matrices with identical shapes")
    dot = sum(left[row][column] * right[row][column]
              for row in range(len(left)) for column in range(len(left[0])))
    left_length = sqrt(sum(value * value for row in left for value in row))
    right_length = sqrt(sum(value * value for row in right for value in row))
    return dot / (left_length * right_length) if left_length and right_length else 0.0


def rank_images(query, images):
    """Rank grayscale matrices by cosine similarity, preserving input order on ties."""
    return sorted(enumerate(image_cosine_similarity(query, image) for image in images),
                  key=lambda item: item[1], reverse=True)


def compressed_image_search(query, images, rank, iterations=80, epsilon=EPSILON):
    """Compress a query/gallery with the same rank, then audit cosine retrieval.

    This small teaching pipeline reports approximation error alongside rankings.
    It deliberately does not claim that low Frobenius error preserves semantic
    relevance: the scores only compare flattened grayscale matrices.
    """
    if not images:
        raise ValueError("images must be a non-empty list")
    original_ranking = rank_images(query, images)
    query_components, compressed_query, query_error = compress_grayscale(query, rank, iterations, epsilon)
    compressed_images = []
    image_errors = []
    component_counts = []
    for image in images:
        components, compressed, error = compress_grayscale(image, rank, iterations, epsilon)
        compressed_images.append(compressed)
        image_errors.append(error)
        component_counts.append(len(components))
    compressed_ranking = rank_images(compressed_query, compressed_images)
    original_order = [index for index, _ in original_ranking]
    compressed_order = [index for index, _ in compressed_ranking]
    return {
        "query_component_count": len(query_components),
        "query_error": query_error,
        "image_component_counts": component_counts,
        "image_errors": image_errors,
        "original_ranking": original_ranking,
        "compressed_ranking": compressed_ranking,
        "ranking": compressed_ranking,
        "certificate": {
            "original_ranking_is_a_permutation": sorted(original_order) == list(range(len(images))),
            "compressed_ranking_is_a_permutation": sorted(compressed_order) == list(range(len(images))),
            "top_match_is_preserved": original_order[0] == compressed_order[0],
            "full_ranking_is_preserved": original_order == compressed_order,
        },
    }


def compressed_image_search_certificate(query, images, rank, report, iterations=80, epsilon=EPSILON):
    """Recompute a small compression--retrieval report instead of trusting it.

    The certificate establishes only that this deterministic teaching pipeline
    was reported faithfully for the supplied matrices and parameters.  It does
    not establish semantic relevance or that low-rank compression is suitable
    for a real image-search workload.
    """
    empty = {
        "fields_match_recomputed_report": False,
        "rankings_are_permutations": False,
        "top_match_is_preserved": False,
        "full_ranking_is_preserved": False,
        "valid": False,
    }
    if not isinstance(report, dict):
        return empty
    try:
        expected = compressed_image_search(query, images, rank, iterations, epsilon)
        fields_match = all(report.get(field) == value for field, value in expected.items())
        reported_certificate = report.get("certificate")
        certificate_fields = expected["certificate"]
        rankings_are_permutations = (
            isinstance(reported_certificate, dict)
            and reported_certificate.get("original_ranking_is_a_permutation") is True
            and reported_certificate.get("compressed_ranking_is_a_permutation") is True
            and certificate_fields["original_ranking_is_a_permutation"]
            and certificate_fields["compressed_ranking_is_a_permutation"]
        )
        top_match_is_preserved = (
            isinstance(reported_certificate, dict)
            and reported_certificate.get("top_match_is_preserved") is True
            and certificate_fields["top_match_is_preserved"]
        )
        full_ranking_is_preserved = (
            isinstance(reported_certificate, dict)
            and reported_certificate.get("full_ranking_is_preserved") is True
            and certificate_fields["full_ranking_is_preserved"]
        )
        return {
            "fields_match_recomputed_report": fields_match,
            "rankings_are_permutations": rankings_are_permutations,
            "top_match_is_preserved": top_match_is_preserved,
            "full_ranking_is_preserved": full_ranking_is_preserved,
            "valid": fields_match and rankings_are_permutations,
        }
    except (TypeError, ValueError, ZeroDivisionError):
        return empty


def frobenius_error(matrix, approximation):
    """Return ||matrix - approximation||_F after checking compatible shapes."""
    if (len(matrix) != len(approximation) or not matrix
            or any(len(row) != len(approximation[index]) for index, row in enumerate(matrix))):
        raise ValueError("matrices must have the same non-empty shape")
    return sqrt(sum((value - approximation[row][column]) ** 2
                    for row, values in enumerate(matrix)
                    for column, value in enumerate(values)))
