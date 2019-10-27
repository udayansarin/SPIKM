import numpy as np
import math


class Toolkit:
    """
    Define commonly used trigonometric functions for the inverse kinematics of a Stewart Platform
    """
    @staticmethod
    def get_theta(x, z):
        """
        obtain the angle of the triangle on the basis of the perpendicular and base
        :param x: float, base of the right angled triangle
        :param z: float, perpendicular of the right angled triangle
        :return: float, angle of the triangle
        """
        return math.atan(z/x)

    @staticmethod
    def get_xz(length, theta):
        """
        get the base and perpendicular of a right angled triangle on the basis of the known angle and hypotenuse
        :param length: float, hypotenuse
        :param theta: float, known angle of the right angled triangle
        :return: dict, {'x', 'y'} containing the base and perpendicular of a triangle
        """
        return {'x': length*math.cos(theta), 'z': length*math.sin(theta)}

    @staticmethod
    def apply_rotation(alpha, beta, gamma, vector):
        """
        apply a 3D rotation to a vector
        :param alpha: float, angle to rotate about the x axis in degrees
        :param beta: float, angle to rotate about the y axis in degrees
        :param gamma: float, angle to rotate about the z axis in degrees
        :param vector: list/np.array, vector to be rotated
        :return: np.array, rotated vector
        """
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
