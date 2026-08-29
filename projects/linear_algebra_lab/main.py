"""Teaching implementations for matrix multiplication, elimination and projection."""

from math import isfinite, sqrt


EPSILON = 1e-12


def matmul(left, right):
    """Return left @ right for non-empty rectangular nested lists."""
    if not left or not right or not left[0] or not right[0]:
        raise ValueError("matrices must be non-empty")
    left_width = len(left[0])
    right_width = len(right[0])
    if any(len(row) != left_width for row in left + right):
        raise ValueError("matrices must be rectangular")
    if left_width != len(right):
        raise ValueError("incompatible matrix shapes")
    return [
        [sum(left[i][k] * right[k][j] for k in range(left_width))
         for j in range(right_width)]
        for i in range(len(left))
    ]


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
    query_components, compressed_query, query_error = compress_grayscale(query, rank, iterations, epsilon)
    compressed_images = []
    image_errors = []
    component_counts = []
    for image in images:
        components, compressed, error = compress_grayscale(image, rank, iterations, epsilon)
        compressed_images.append(compressed)
        image_errors.append(error)
        component_counts.append(len(components))
    return {
        "query_component_count": len(query_components),
        "query_error": query_error,
        "image_component_counts": component_counts,
        "image_errors": image_errors,
        "ranking": rank_images(compressed_query, compressed_images),
    }


def frobenius_error(matrix, approximation):
    """Return ||matrix - approximation||_F after checking compatible shapes."""
    if (len(matrix) != len(approximation) or not matrix
            or any(len(row) != len(approximation[index]) for index, row in enumerate(matrix))):
        raise ValueError("matrices must have the same non-empty shape")
    return sqrt(sum((value - approximation[row][column]) ** 2
                    for row, values in enumerate(matrix)
                    for column, value in enumerate(values)))
