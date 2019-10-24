import math
import numpy as np
from dynamics.linkage import CrankShaft as Cs
from dynamics.spikm_trig import Toolkit

import matplotlib.pyplot as plt

class _Platform:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.a = 0
        self.b = 0
        self.g = 0
        self._design = None
        self.nodes = {
            '1': {'motor': None, 'node': None, 'rotation': 0},
            '2': {'motor': None, 'node': None, 'rotation': 0},
            '3': {'motor': None, 'node': None, 'rotation': -120},
            '4': {'motor': None, 'node': None, 'rotation': -120},
            '5': {'motor': None, 'node': None, 'rotation': 120},
            '6': {'motor': None, 'node': None, 'rotation': 120}
        }
        self._shape = None
        self._current_platform = None

    def _set_orientation(self, orientation):
        self.x = orientation['x']
        self.y = orientation['y']
        self.z = orientation['z']
        self.a = orientation['a']
        self.b = orientation['b']
        self.g = orientation['g']
        return

    def set_dimensions(self, design):
        self._design = design
        self._shape = _Platform.generate_shape(self._design)
        return

    def update_platform(self, move):
        self._set_orientation(orientation=move)
        _angular_pos = [Toolkit.apply_rotation(alpha=self.a, beta=self.b, gamma=self.g, vector=point)
                        for point in self._shape]
        self._current_platform = [list(np.array(v) + np.array([self.x, self.y, self.z])) for v in _angular_pos]

    def get_platform(self, starting=False):
        _platform = _Platform.get_nodes(self._shape) if starting else _Platform.get_nodes(self._current_platform)
        if starting:
            self._get_motors(_platform)
        return _platform

    def _motor_distance_vector(self):
        c_shaft = Toolkit.get_xz(length=self._design['crank_len'],
                                 theta=math.radians(self._design['crank_ang']))
        _x_abs = np.sqrt(self._design['lnkge_len']**2 -
                         self._design['assly_ofs']**2 -
                         (self._design['plane_ofs'] - 2*c_shaft['z'])**2) + c_shaft['x']
        _y_abs = self._design['assly_ofs']
        _z_abs = self._design['plane_ofs']
        return _x_abs, _y_abs, _z_abs

    def _get_motors(self, platform):
        motor_offsets = self._motor_distance_vector()
        print(motor_offsets)
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
            # plt.scatter([g_motor[0]], [g_motor[1]], marker='o')
            # plt.scatter([g_node[0]], [g_node[1]], marker='x')
            val['node'] = Cs(node=_node,
                             shaft=val['motor'],
                             crank_length=self._design['crank_len'],
                             crank_start_angle=self._design['crank_ang'],
                             link_length=self._design['lnkge_len'],
                             crank_plane=self._design['assly_ang'])
        # plt.show()

    @staticmethod
    def get_nodes(coordinates):
        x = [p[0] for p in coordinates]
        y = [p[1] for p in coordinates]
        z = [p[2] for p in coordinates]
        return x, y, z

    @staticmethod
    def generate_shape(design):
        p1 = [-0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        p2 = [0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        points = [p1, p2, list(Toolkit.apply_rotation(0, 0, -120, p1)), list(Toolkit.apply_rotation(0, 0, -120, p2)),
                  list(Toolkit.apply_rotation(0, 0, 120, p1)), list(Toolkit.apply_rotation(0, 0, 120, p2)), p1]
        return points

    @staticmethod
    def init_crank_shaft(design):
        crank_con = Toolkit.get_xz(length=design['crank_len'], theta=math.radians(design['crank_ang']))
        con_node = Toolkit.get_xz(length=design['lnkge_len'], theta=math.radians(90-design['lnkge_ang']))
        x = [0, crank_con['x'], crank_con['x'] + con_node['x']]
        z = [0, crank_con['z'], crank_con['z'] + con_node['z']]
        return x, z

    class _Node:
        def __init__(self, init_coordinates, crank_len, crank_ang, lnkge_len, lnkge_ang, assly_ang):
            self.x = init_coordinates['x']
            self.y = init_coordinates['y']
            self.z = init_coordinates['z']
            #todo: self.obj = Cs(all_arguments)
            #todo: I have functions to get the coordinates of the linkage if I provide the node's new coordinates
            # todo: what I need to do is calculate the new coordinates of the node for the input move
            # TODO: USE OTHER_ARGS ASSLY_ANG TO CALCULATE MOTOR POSITIONS, GENERATE_NODES ALREADY GIVES YOU NODES
            # TODO: YOU SHOULD NOW HAVE ENOUGH INFORMATION TO INSTANTIATE LINKAGE.PY ASSLY_ANG = CRANK_PLANE


class Platform:
    def __init__(self, design):
        self.ptfrm = _Platform()
        self.ptfrm.set_dimensions(design=design)

    @property
    def run(self):
        return self.ptfrm

    @staticmethod
    def generate(design):
        return _Platform.generate_shape(design)

    @staticmethod
    def compute_init_crankshaft(design):
        x, z = _Platform.init_crank_shaft(design)
        return {'x': x, 'z': z}

