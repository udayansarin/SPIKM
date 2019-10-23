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
            '1': None,
            '2': None,
            '3': None,
            '4': None,
            '5': None,
            '6': None
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
        return _Platform.get_nodes(self._shape) if starting else _Platform.get_nodes(self._current_platform)

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

