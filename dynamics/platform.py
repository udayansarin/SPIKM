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
        self.ptfrm_sze = 0
        self.ptfrm_len = 0
        self.assly_ang = 0
        self.crank_len = 0
        self.crank_ang = 0
        self.lnkge_ang = 0
        self.lnkge_len = 0

    def set_coordinates(self, orientation):
        self.x = orientation['x']
        self.y = orientation['y']
        self.z = orientation['z']
        self.a = orientation['a']
        self.b = orientation['b']
        self.g = orientation['g']
        return

    def set_dimensions(self, design):
        self.ptfrm_sze = design['ptfrm_sze']
        self.ptfrm_len = design['ptfrm_len']
        self.assly_ang = design['assly_ang']
        self.crank_len = design['crank_len']
        self.crank_ang = design['crank_ang']
        self.lnkge_ang = design['ptfrm_len']
        self.lnkge_len = design['lnkge_len']
        return

    @staticmethod
    def generate_nodes(design):
        p1 = [-0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        p2 = [0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        points = [p1, p2, list(Toolkit.apply_rotation(0, 0, -120, p1)), list(Toolkit.apply_rotation(0, 0, -120, p2)),
                  list(Toolkit.apply_rotation(0, 0, 120, p1)), list(Toolkit.apply_rotation(0, 0, 120, p2)), p1]
        return points

    class _Node:
        def __init__(self, init_coordinates, other_args):
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

    @staticmethod
    def generate(design):
        return _Platform.generate_nodes(design)

