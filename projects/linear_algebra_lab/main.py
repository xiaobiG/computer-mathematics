"""Teaching implementations for matrix multiplication, elimination and projection."""

from math import sqrt


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


def solve(matrix, target, epsilon=EPSILON):
    """Solve a square dense system using Gaussian elimination with pivoting."""
    size = len(matrix)
    if size == 0 or len(target) != size or any(len(row) != size for row in matrix):
        raise ValueError("matrix must be square and match target")
    augmented = [list(map(float, row)) + [float(target[i])] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= epsilon:
            raise ValueError("system does not have a unique solution")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        for row in range(column + 1, size):
            factor = augmented[row][column] / pivot_value
            for item in range(column, size + 1):
                augmented[row][item] -= factor * augmented[column][item]
    result = [0.0] * size
    for row in range(size - 1, -1, -1):
        result[row] = (augmented[row][size] - sum(
            augmented[row][column] * result[column] for column in range(row + 1, size)
        )) / augmented[row][row]
    return result


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


def least_squares_qr(matrix, target, epsilon=EPSILON):
    """Solve min ||Ax-b||_2 with modified Gram--Schmidt and back substitution.

    This small dense teaching implementation requires full column rank.  It
    avoids forming A^T A, whose condition number is roughly squared.
    """
    if (not matrix or not matrix[0] or len(target) != len(matrix)
            or any(len(row) != len(matrix[0]) for row in matrix)):
        raise ValueError("matrix must be non-empty rectangular and match target")
    rows, columns = len(matrix), len(matrix[0])
    if rows < columns:
        raise ValueError("least squares QR requires at least as many rows as columns")
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
    residual = [float(target[row]) - sum(matrix[row][column] * solution[column] for column in range(columns))
                for row in range(rows)]
    return solution, residual


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


def frobenius_error(matrix, approximation):
    """Return ||matrix - approximation||_F after checking compatible shapes."""
    if (len(matrix) != len(approximation) or not matrix
            or any(len(row) != len(approximation[index]) for index, row in enumerate(matrix))):
        raise ValueError("matrices must have the same non-empty shape")
    return sqrt(sum((value - approximation[row][column]) ** 2
                    for row, values in enumerate(matrix)
                    for column, value in enumerate(values)))
