import math

import spikm_trig as s_trig


class CrankShaft:

    def __init__(self, node, shaft, crank_length, crank_start_angle, link_length, crank_plane):
        """
        initialize the crankshaft assembly between the motor and the corresponding connection on the platform
        :param node: dict{'x', 'y', 'z'}, location of the platform connection in the global x, y, z coordinate system
        :param shaft: dict{'x', 'y', 'z'}, location of the motor shaft in the global x, y, z coordinate system
        :param crank_length:
        :param crank_start_angle:
        :param link_length:
        :param crank_plane:
        """
        self.init = False
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

        if self._crank.init and self._link.init:
            self.init = True
            self._crank_plane = crank_plane
            self._node = node
            self._shaft = shaft


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
            self.connector = {'x': 0, 'y': 0}

        def move(self, new_connector):
            """
            update the crank angle based on the movement of the linkage
            :param new_connector: new position of the crank as dict {'x': _, 'y': _}
            :return:
            """
            self.connector = new_connector
            self.angle = s_trig.get_theta(x=self.connector['x'], y=self.connector['y'])

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
