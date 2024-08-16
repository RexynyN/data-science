from typing import List

# Alias for a List of floats (now a vector)
Vector = List[float]


import math 
def add(v: Vector, w: Vector) -> Vector:
    """ Returns the sum of two vectors """
    assert len(v) == len(w), "Both vectors must be the same length"

    # Sum of each component (v0 + w0), (v1 + w1) .... (vi + wi) 
    return [vi + wi for vi, wi in zip(v, w)]


def subtract(v: Vector, w: Vector) -> Vector:
    """ Returns the subtraction of two vectors """
    assert len(v) == len(w), "Both vectors must be the same length"

    # Sum of each component (v0 - w0), (v1 - w1) .... (vi - wi) 
    return [vi - wi for vi, wi in zip(v, w)]


def vector_sum(vectors: list[Vector]) -> Vector:
    """ Returns the sum of multiple vectors """
    assert vectors, "No empty vectors"

    num_elements = len(vectors[0])
    assert all(len(v) == num_elements for v in vectors), "Not all vectors are the same size!"

    # Sum all of the components into one single vector
    return [sum(vector[i] for vector in vectors) for i in range(num_elements)]

def scalar_multiply(vec: Vector, sca: float) -> Vector:
    """ Returns the multiplication of a vector with a scalar value """
    return [sca * vi for vi in vec]


def vector_mean(vectors: list[Vector]) -> Vector:
    """ Computes the mean of a list of vectors """
    n = len(vectors)
    return scalar_multiply(vector_sum(), 1/n)

def dot(v: Vector, w: Vector) -> float:
    """ Returns the dot product of both vectors """
    assert len(v) == len(w), "Both vectors must be the same length"

    return sum([vi * wi for vi, wi in zip(v, w)])

def sum_of_squares(v: Vector) -> float:
    """ Return the sums of squares of a vector v1 * v1 + v2 * v2 .... """
    return dot(v, v)

def magnitude(v: Vector) -> float:
    """ Computes the magnitude (or length) of a vector"""
    return math.sqrt(sum_of_squares(v))

def squared_distance(v: Vector, w: Vector) -> float:
    """ Calculate the (v1 - w1)^2 + ... + (vi - wi)^2 """
    return sum_of_squares(subtract(v, w))

def distance(v: Vector, w: Vector) -> float:
    """ Returns the distance between two vectors """
    return math.sqrt(squared_distance(v, w))
    # Can be done this way too 
    # return magnitude(subtract(v, w))


# Some testing to do, of course, why not
assert add([1, 2, 3], [4, 5, 6]) == [5, 7, 9]

assert subtract([5, 7, 9], [4, 5, 6]) == [1, 2, 3]

assert vector_sum([[1, 2], [3, 4], [5, 6], [7, 8]]) == [16, 20]

assert scalar_multiply(2, [1, 2, 3]) == [2, 4, 6]

assert vector_mean([[1, 2], [3, 4], [5, 6]]) == [3, 4]

assert dot([1, 2, 3], [4, 5, 6]) == 32  # 1 * 4 + 2 * 5 + 3 * 6

assert sum_of_squares([1, 2, 3]) == 14  # 1 * 1 + 2 * 2 + 3 * 3

assert magnitude([3, 4]) == 5


Matrix = list[list[float]]

A = [[1, 2, 3],  # A has 2 rows and 3 columns
     [4, 5, 6]]

B = [[1, 2],     # B has 3 rows and 2 columns
     [3, 4],
     [5, 6]]

def shape(A: Matrix) -> tuple[int, int]:
    """ Returns the shape of the matrix -> (rows, cols) """
    num_rows = len(A)
    num_cols = len(A[0]) if A else -
    return num_rows, num_cols

def get_row(A: Matrix, i: int) -> Vector:
    """ Returns the i-th row of A (as a Vector) """
    return A[i]

def get_column(A: Matrix, j: int) -> Vector:
    """Returns the j-th column of A (as a Vector)"""
    return [A_i[j]          # jth element of row A_i
            for A_i in A]   # for each row A_i

assert shape([[1, 2, 3], [4, 5, 6]]) == (2, 3)  # 2 rows, 3 columns



