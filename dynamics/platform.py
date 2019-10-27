import math
import numpy as np
from dynamics.linkage import CrankShaft as Cs
from dynamics.spikm_trig import Toolkit


class _Platform:
    """
    Instances of this class show behaviour of the Stewart Platform
    """
    def __init__(self):
        """
        define and initialize parameters for a Stewart Platform
        """
        self.x = 0
        self.y = 0
        self.z = 0
        self.a = 0
        self.b = 0
        self.g = 0
        self._design = None
        self.nodes = {
            '1': {'motor': None, 'node': self._Node, 'rotation': 0},
            '2': {'motor': None, 'node': self._Node, 'rotation': 0},
            '3': {'motor': None, 'node': self._Node, 'rotation': -120},
            '4': {'motor': None, 'node': self._Node, 'rotation': -120},
            '5': {'motor': None, 'node': self._Node, 'rotation': 120},
            '6': {'motor': None, 'node': self._Node, 'rotation': 120}
        }
        self._shape = None
        self._current_platform = None

    def _set_orientation(self, orientation):
        """
        update instance orientation properties to match the input target orientation
        :param orientation: dict, {'x', 'y', 'z', 'a', 'b', 'g'} containing 6-dof positional parameters
        :return:
        """
        self.x = orientation['x']
        self.y = orientation['y']
        self.z = orientation['z']
        self.a = orientation['a']
        self.b = orientation['b']
        self.g = orientation['g']
        return

    def set_dimensions(self, design):
        """
        define the shape and design of the stewart platform
        :param design: dict, containing the design properties of the Stewart Platform see ui.setup._update_design
        :return:
        """
        self._design = design
        self._shape = _Platform.generate_shape(self._design)
        return

    def update_platform(self, move):
        """
        update the current position of the platform in space on the basis of the inputted move
        :param move: dict, {'x', 'y', 'z', 'a', 'b', 'g'} containing 6-dof positional parameters
        :return:
        """
        self._set_orientation(orientation=move)
        _angular_pos = [Toolkit.apply_rotation(alpha=self.a, beta=self.b, gamma=self.g, vector=point)
                        for point in self._shape]
        self._current_platform = [list(np.array(v) + np.array([self.x, self.y, self.z])) for v in _angular_pos]
        return

    def get_platform(self, starting=False):
        """
        get all properties of the platform for the current orientation - linkages, platform, motors and feasibility
        :param starting: bool, indicating if the platform is at home or at a self._current_platform position
        :return: lists, defining the platform, linkages, motor angles and whether the position is feasible
        """
        _platform = _Platform.get_nodes(self._shape) if starting else _Platform.get_nodes(self._current_platform)
        _linkages, _motors, _feasible = self._init_nodes(_platform) if starting else self._update_nodes()
        return _platform, _linkages, _motors, _feasible

    def _motor_distance_vector(self):
        """
        for the Stewart Platform design, calculate the vector between the node and the motor shaft (normal view)
        :return: floats, absolute x coordinate of the vector, absolute y, absolute z
        """
        c_shaft = Toolkit.get_xz(length=self._design['crank_len'],
                                 theta=math.radians(self._design['crank_ang']))
        _x_abs = (self._design['lnkge_len']**2 -
                  self._design['assly_ofs']**2 -
                  (self._design['plane_ofs'] - 2*c_shaft['z'])**2)**0.5 + c_shaft['x']
        if np.iscomplex(_x_abs):
            _x_abs = None
        _y_abs = self._design['assly_ofs']
        _z_abs = self._design['plane_ofs']
        return _x_abs, _y_abs, _z_abs

    def _init_nodes(self, platform):
        """
        initialize the nodes (linkage - platform connection) of the platform as instances of class _Node
        :param platform: coordinates of the platform in separate lists for x, y, z at indices 1, 2, 3
        :return: list, 6x3 list for the coordinates of the linkage, 6x for motor angles, 6x for feasibility
        """
        motor_offsets = self._motor_distance_vector()
        if motor_offsets[0] is None:
            return None, None, [False]*6
        _linkages = {
            'x': [],
            'y': [],
            'z': []
        }
        _motor = []
        _feasible = []
        for node, val in self.nodes.items():
            node_num = int(node)
            _even = node_num % 2 == 0
            del_x = -motor_offsets[0]
            del_y = -motor_offsets[1] if _even else motor_offsets[1]
            del_z = -motor_offsets[2]
            _angle = (180-self._design['assly_ang'])+val['rotation'] \
                if _even else self._design['assly_ang']+val['rotation']
            g_node = np.array([platform[0][node_num - 1], platform[1][node_num - 1], platform[2][node_num - 1]])
            l_node = Toolkit.apply_rotation(alpha=0, beta=0, gamma=-_angle, vector=g_node)
            l_motor = l_node + np.array([del_x, del_y, del_z])
            g_motor = Toolkit.apply_rotation(alpha=0, beta=0, gamma=_angle, vector=l_motor)
            val['motor'] = {'x': g_motor[0], 'y': g_motor[1], 'z': g_motor[2]}
            _node = {'x': g_node[0], 'y': g_node[1], 'z': g_node[2]}
            val['node'] = self._Node(node=_node,
                                     shaft=val['motor'],
                                     crank_length=self._design['crank_len'],
                                     crank_start_angle=self._design['crank_ang'],
                                     link_length=self._design['lnkge_len'],
                                     crank_plane=_angle
                                     )
            _link = val['node'].get_linkage()
            if not _link['feasible']:
                _feasible.append(False)
            else:
                _feasible.append(True)
                for key, v in _linkages.items():
                    v.append(_link[key])
                _motor.append(_link['angle'])
        return _linkages, _motor, _feasible

    def _update_nodes(self):
        """
        update the position of the nodes on the basis of the current position of the platform, this function returns
        values comparable to _init_nodes, with the difference of initialization versus positional updates
        :return:
        """
        _linkages = {
            'x': [],
            'y': [],
            'z': []
        }
        _motor = []
        _feasible = []
        for node_num, curr_pos in enumerate(self._current_platform[:-1]):
            _node = self.nodes[str(node_num+1)]
            _node['node'].update_position(posn=curr_pos)
            _link = _node['node'].get_linkage()
            _feasible.append(_link['feasible'])
            for key, v in _linkages.items():
                v.append(_link[key])
            _motor.append(_link['angle'])
        return _linkages, _motor, _feasible

    @staticmethod
    def get_nodes(coordinates):
        """
        convert the nodal positions from [[x1, y1, z1], [x2, y2, z2], ...] -> [x1, x2..], [y1..], [z1...]
        :param coordinates: nodal positions of the Stewart Platform as a list
        :return: lists, x, y, z positions of each node in ordered form in separate lists
        """
        x = [p[0] for p in coordinates]
        y = [p[1] for p in coordinates]
        z = [p[2] for p in coordinates]
        return x, y, z

    @staticmethod
    def generate_shape(design):
        """
        generate the shape of the Stewart Platform on the basis of the design dictionary,
        see ui.setup._update_design
        :param design: dict, containing design parameters for the Stewart Platform
        :return: list, containing nodes of the stewart platform as [[x1, y1, z1], [x2, y2, z2], ...]
        """
        p1 = [-0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        p2 = [0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        points = [p1, p2, list(Toolkit.apply_rotation(0, 0, -120, p1)), list(Toolkit.apply_rotation(0, 0, -120, p2)),
                  list(Toolkit.apply_rotation(0, 0, 120, p1)), list(Toolkit.apply_rotation(0, 0, 120, p2)), p1]
        return points

    class _Node:
        """
        Instances of this class define nodes of the Platform and exhibit behaviour by instantiating
        dynamics.linkage.CrankShaft
        """
        def __init__(self, node, shaft, crank_length, crank_start_angle, link_length, crank_plane):
            """
            define a node of the stewart platform
            :param node: dict{'x', 'y', 'z'}, location of the platform connection in global x, y, z coordinate system
            :param shaft: dict{'x', 'y', 'z'}, location of the motor shaft in the global x, y, z coordinate system
            :param crank_length: float or int length of crankshaft
            :param crank_start_angle: float or int, starting angle of crankshaft, 90 is horizontal
            :param link_length: float or int length of linkage
            :param crank_plane: angle that the plane of rotation of the motor shaft subtends to the global x axis
            """
            self.me = Cs(node=node,
                         shaft=shaft,
                         crank_length=crank_length,
                         crank_start_angle=crank_start_angle,
                         link_length=link_length,
                         crank_plane=crank_plane
                         )

        def update_position(self, posn):
            """
            update the position of the given node
            :param posn: list, [x, y, z] coordinates of the new node position
            :return:
            """
            self.me.move(x_new=posn[0], y_new=posn[1], z_new=posn[2])
            return

        def get_linkage(self):
            """
            get a list defining the position of the associated linkage in space
            :return: dict, {'feasible': bool, move feasible, 'x', 'y', 'z': list of link coordinates,
            'angle': float, motor}
            """
            return self.me.get_linkage()


class Platform:
    """
    Used as a non-protected member for other packages to interface with class _Platform
    """
    def __init__(self, design):
        self.ptfrm = _Platform()
        self.ptfrm.set_dimensions(design=design)

    @property
    def run(self):
        """
        run a function from class _Platform
        :return: return from the referenced function
        """
        return self.ptfrm
