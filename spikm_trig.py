import numpy as np
import math


def get_theta(x, y):
    return math.atan(y/x)


def apply_rotation(alpha, beta, gamma, vector):
    a = math.radians(alpha)
    b = math.radians(beta)
    g = math.radians(gamma)
    rot_matrix = np.array([[math.cos(b) * math.cos(g),
                            -1 * math.cos(a) * math.sin(g) + math.sin(a) * math.sin(b) * math.cos(g),
                            math.sin(a) * math.sin(g) + math.cos(a) * math.cos(g) * math.sin(b)],
                           [math.cos(b) * math.sin(g),
                            math.cos(a) * math.cos(g) + math.sin(a) * math.sin(b) * math.sin(g),
                            -1 * math.sin(a) * math.cos(g) + math.cos(a) * math.sin(g) * math.sin(b)],
                           [-1 * math.sin(b), math.sin(a) * math.cos(b), math.cos(a) * math.cos(b)]])
    prod = rot_matrix.dot(vector)
    return prod
