import math
import numpy as np
from dynamics.linkage import CrankShaft as Cs
from dynamics.spikm_trig import Toolkit


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
        _linkages, _motors, _feasible = self._init_nodes(_platform) if starting else self._update_nodes()
        return _platform, _linkages, _motors, _feasible

    def _motor_distance_vector(self):
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

            if not _link['feasible']:
                _feasible.append(False)
            else:
                _feasible.append(True)
                for key, v in _linkages.items():
                    v.append(_link[key])
                _motor.append(_link['angle'])
        return _linkages, _motor, _feasible

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
        def __init__(self, node, shaft, crank_length, crank_start_angle, link_length, crank_plane):
            self.me = Cs(node=node,
                         shaft=shaft,
                         crank_length=crank_length,
                         crank_start_angle=crank_start_angle,
                         link_length=link_length,
                         crank_plane=crank_plane
                         )

        def update_position(self, posn):
            self.me.move(x_new=posn[0], y_new=posn[1], z_new=posn[2])

        def get_linkage(self):
            return self.me.get_linkage()


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

