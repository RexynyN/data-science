import math 
from typing import List, Tuple, Callable

Vector = List[float]
Matrix = List[List[float]]


# For v and w are vectors
# R = [v[0] + w[0],  v[1] + w[1], .... v[i] + w[i]]
def add(v: Vector, w: Vector) -> Vector: 
    """ Add two vectors together """
    assert len(v) == len(w), "Vectors must have the same length"

    return [v_i + w_i for v_i, w_i in zip(v, w)]

assert add([1, 2, 3], [4, 5, 6]) == [5, 7, 9]

# For v and w are vectors
# R = [v[0] - w[0],  v[1] - w[1], .... v[i] - w[i]]
def subtract(v: Vector, w: Vector) -> Vector:
    """Subtracts corresponding elements"""
    assert len(v) == len(w), "Vectors must have the same length"

    return [v_i - w_i for v_i, w_i in zip(v, w)]

assert subtract([5, 7, 9], [4, 5, 6]) == [1, 2, 3]

def vector_sum(vectors: List[Vector]) -> Vector: 
    """ Sums all of the given vectors together into a single vector"""
    assert vectors, "The vector list is empty"

    num_elements = len(vectors[0])
    assert all(len(v) == num_elements for v in vectors), "There are vectors of different sizes"

    # R[i] = v[i] + w[i] + y[i] ... + z[i]
    return [sum(vector[i] for vector in vectors) for i in range(num_elements)]

assert vector_sum([[1, 2], [3, 4], [5, 6], [7, 8]]) == [16, 20]

def scalar_multiply(c: float, v: Vector) -> Vector:
    """ Multiply the given vector to a scalar value """
    
    # R = [c * v[0], c * v[1], ... c * v[i]]
    return [c * v_i for v_i in v]

assert scalar_multiply(2, [1, 2, 3]) == [2, 4, 6]


def vector_mean(vectors: List[Vector]) -> Vector: 
    """Computes the element-wise average"""
    n = len(vectors)

    # R = [1/len * v[0], 1/len * v[1], ... 1/len * v[i]]
    # R being the mean vector of the bunch
    return scalar_multiply(1/n, vector_sum(vectors))

assert vector_mean([[1, 2], [3, 4], [5, 6]]) == [3, 4]

def dot(v: Vector, w: Vector) -> Vector: 
    """ Add two vectors together """
    assert len(v) == len(w), "Vectors must have the same length"

    # (v[0] * w[0]) + (v[1] * w[1]) + .... + (v[i] * w[i])
    return sum(v_i * w_i for v_i, w_i in zip(v, w))


def sum_of_squares(v: Vector) -> float:
    """Returns v_1 * v_1 + ... + v_n * v_n"""
    return dot(v, v)

assert sum_of_squares([1, 2, 3]) == 14 # 1 * 1 + 2 * 2 + 3 * 3


def magnitude(v: Vector) -> float: 
    """ Return the length (or magnitude) of an vector"""
    return math.sqrt(sum_of_squares(v))

assert magnitude([3, 4]) == 5


# √(v1 − w1) ^ 2 + ... + (vn − wn) ^ 2

def squared_distance(v: Vector, w: Vector) -> float:
    """Computes (v_1 - w_1) ** 2 + ... + (v_n - w_n) ** 2"""
    return sum_of_squares(subtract(v, w))

def distance(v: Vector, w: Vector) -> float:
    """Computes the distance between v and w"""
    return math.sqrt(squared_distance(v, w))



def shape(A: Matrix) -> Tuple[int, int]:
    """Returns (# of rows of A, # of columns of A)"""
    num_rows = len(A)
    num_cols = len(A[0]) if A else 0 # number of elements in first row
    return num_rows, num_cols

assert shape([[1, 2, 3], [4, 5, 6]]) == (2, 3) # 2 rows, 3 columns


def get_row(A: Matrix, i: int) -> Vector:
    """Returns the i-th row of A (as a Vector)"""
    return A[i] # A[i] is already the ith row

def get_column(A: Matrix, j: int) -> Vector:
    """Returns the j-th column of A (as a Vector)"""
    return [A_i[j] # jth element of row A_i
    for A_i in A] # for each row A_i



def make_matrix(num_rows: int, num_cols: int,
    entry_fn: Callable[[int, int], float]
) -> Matrix:
    """
    Returns a num_rows x num_cols matrix
    whose (i,j)-th entry is entry_fn(i, j)
    """
    return [[entry_fn(i, j) # given i, create a list
        for j in range(num_cols)] # [entry_fn(i, 0), ... ]
        for i in range(num_rows)] # create one list for each i


def identity_matrix(n: int) -> Matrix:
    """Returns the n x n identity matrix"""
    return make_matrix(n, n, lambda i, j: 1 if i == j else 0)


assert identity_matrix(5) == [
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1]
]

