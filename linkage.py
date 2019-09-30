import math
import numpy as np
from numpy.polynomial import Polynomial as poly

from spikm_trig import Toolkit as STrig


class CrankShaft:

    def __init__(self, node, shaft, crank_length, crank_start_angle, link_length, crank_plane):
        """
        initialize the crankshaft assembly between the motor and the corresponding connection on the platform
        :param node: dict{'x', 'y', 'z'}, location of the platform connection in the global x, y, z coordinate system
        :param shaft: dict{'x', 'y', 'z'}, location of the motor shaft in the global x, y, z coordinate system
        :param crank_length: float or int length of crankshaft
        :param crank_start_angle: float or int, starting angle of crankshaft, 90 is horizontal
        :param link_length: float or int length of linkage
        :param crank_plane: angle that the plane of rotation of the motor shaft subtends to the global x axis
        """
        self.init = False
        self.incompatible = False
        try:
            for connection, coordinates in {'platform': node, 'motor': shaft}.items():
                for coordinate, val in coordinates.items():
                    assert ((type(val) is int) or (type(val) is float))
        except AssertionError:
            print(f"Error in coordinate for {connection}[{coordinate}]\nvalue:{val}")
            return
        try:
            assert(
                ((type(crank_plane) is int) or (type(crank_plane) is float))
                and 0 <= crank_plane < 360
            )
        except AssertionError:
            print(f"Error in initializing crank orientation: angle: {crank_length}")
            return
        self._crank = self._Crank(length=crank_length, start_angle=crank_start_angle)
        self._link = self._Linkage(length=link_length)

        if not(self._crank.init and self._link.init):
            print("Terminating linkage initialization due to setup error!")
            return
        self.init = True
        self._crank_plane = crank_plane
        self._node = node
        self._shaft = shaft
        self._connector = self._con_loc_global()

    def _con_loc_global(self):
        """
        calculate the coordinate of the crank-linkage connection in global coordinates
        :return: crank-linkage connection in global coordinates
        """
        _alpha = 0
        _beta = 0
        _gamma = self._crank_plane
        # global coordinate of the motor shaft + the local crank vector rotated to the global coordinate system
        _delta_coordinates = STrig.apply_rotation(_alpha, _beta, _gamma, self._crank.connector)
        return {'x': self._shaft['x'] + _delta_coordinates[0],
                'y': self._shaft['y'] + _delta_coordinates[1],
                'z': self._shaft['z'] + _delta_coordinates[2]}

    def _node_loc_local(self):
        """
        calculate the local coordinate of the linkage-platform connection for computational simplicity
        :return: coordinates of the linkage-platform connection
        """
        _alpha = 0
        _beta = 0
        _gamma = -self._crank_plane
        _vector = np.array(self._node['x'], self._node['y'], self._node['z']) - \
            np.array(self._shaft['x'], self._shaft['y'], self._shaft['z'])
        _loc_vector = STrig.apply_rotation(_alpha, _beta, _gamma, _vector)
        return {'x': _loc_vector[0], 'y': _loc_vector[1], 'z': _loc_vector[2]}

    def move(self, x_new, y_new, z_new):
        self._node['x'] = x_new
        self._node['y'] = y_new
        self._node['z'] = z_new
        node_local = self._node_loc_local()  # local x, y and z for the platform
        x = node_local['x']
        y = node_local['y']
        z = node_local['z']
        k_sq = self._crank.length**2 - self._link.length**2 + x**2 + y**2 + z**2
        a = 1 + (x/z)**2  # x^2 term
        b = -(k_sq*x)/(z**2)  # x term
        c = (k_sq/(2*z))**2 - self._crank.length**2  # constant term
        c_local_x = poly([c, b, a]).roots()[0]  # ax^2 + bx + c = 0
        if np.iscomplex(c_local_x):
            print("You cannot complete this move!")
            self.incompatible = True
        c_local_z = k_sq/(2*z) - (c_local_x*x/z)
        self._crank.move({'x': c_local_x, 'z': c_local_z})
        self._connector = self._con_loc_global()

    def get_linkage(self):
        """
        develop plot for the linkage in global 3d space in the form of lists of x, y and z coordinates of each point
        :return: bool - whether the plot is real/complex, x coordinate list, y list, z list
        """
        x = []
        y = []
        z = []
        if not self.incompatible:
            x = [self._shaft['x'], self._connector['x'], self._node['x']]
            y = [self._shaft['y'], self._connector['y'], self._node['y']]
            z = [self._shaft['z'], self._connector['z'], self._node['z']]

        return (not self.incompatible), x, y, z

    class _Crank:
        def __init__(self, length, start_angle):
            """
            define a crank connected to a motor with the motor shaft at (0, 0, 0) in local coordinates
            :param length: length of the crank shaft
            :param start_angle: starting angle of the crank shaft, between (0, 180) with 90 being horizontal
            """
            self.init = False
            try:
                assert (
                    ((type(length) is int) or (type(length) is float))
                    and length > 0
                    and ((type(start_angle) is float) or type(start_angle) is int)
                    and 0 <= start_angle <= 180
                )
            except AssertionError:
                print("Error in initializing crank!")
                return
            self.init = True
            self.length = length
            self.angle = math.radians(start_angle)
            self.connector = STrig.get_xy(length=self.length, theta=self.angle)

        def move(self, new_connector):
            """
            update the crank angle based on the movement of the linkage
            :param new_connector: new position of the crank as dict {'x': _, 'z': _}
            :return:
            """
            self.connector = new_connector
            self.angle = STrig.get_theta(x=self.connector['x'], z=self.connector['z'])

    class _Linkage:
        def __init__(self, length):
            """
            define the linkage connecting a crank to the corresponding stewart platform connection
            """
            self.init = False
            try:
                assert (
                    ((type(length) is int) or type(length) is float)
                    and length > 0
                )
            except AssertionError:
                print("Error in initializing linkage")
                return
            self.init = True
            self.length = length
