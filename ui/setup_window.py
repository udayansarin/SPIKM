import math
import sys
from tkinter import *

from dynamics.spikm_trig import Toolkit
from ui.plotting_tools import GUIPlotter


class _Orientation:
    def __init__(self):
        self.pltfrm_angle = None
        self.pltfrm_len = None
        self.linkage_angle = None
        self.crank_angle = None
        self.assembly_angle = None
        self.crank_length = None
        self.linkage_length = None


class Design:
    def __init__(self, frame):
        self._parent = frame
        self._me = LabelFrame(self._parent)
        self._me.grid(row=1, column=0)
        self._orientation = _Orientation()
        self._inp_ptfrm_sze = None
        self._inp_ptfrm_len = None
        self._inp_lnkge_ang = None
        self._inp_crank_ang = None
        self._inp_assly_ang = None
        self._inp_crank_len = None
        self._inp_lnkge_len = None
        self._simulate_strt = None
        self._design_update = None
        self._design_ok = None
        self._design = {}
        self._output = Display(frame=self._parent)
        self._show_widgets()

    def _show_widgets(self):
        self._inp_ptfrm_sze = self._Input(label_text='Platform Centre Length', parent=self._me, row=1, col=0)
        self._inp_ptfrm_len = self._Input(label_text='Platform Edge Length', parent=self._me, row=1, col=1)
        self._inp_lnkge_len = self._Input(label_text='Linkage Length', parent=self._me, row=1, col=2)
        self._inp_lnkge_ang = self._Input(label_text='Initial Linkage Angle', parent=self._me, row=1, col=3,
                                          limit_low=-90, limit_high=90)
        self._inp_crank_len = self._Input(label_text='Crank Length', parent=self._me, row=1, col=4)
        self._inp_crank_ang = self._Input(label_text='Initial Crank Angle', parent=self._me, row=1, col=5,
                                          limit_low=-90, limit_high=90)
        self._inp_assly_ang = self._Input(label_text='Assembly Angle', parent=self._me, row=1, col=6,
                                          limit_low=-90, limit_high=90)
        self._design_update = Button(self._me, text='Update', command=lambda: self._update_design(), width=11,
                                     height=2, font=('Helvetica', '15'))
        self._design_update.grid(row=2, column=5)
        self._simulate_strt = Button(self._me, text='Simulate', command=lambda: self._start_sim(), width=11,
                                     height=2, font=('Helvetica', '15'))
        self._simulate_strt.grid(row=2, column=6)

    def _update_design(self):
        self._design = {
            'ptfrm_sze': self._inp_ptfrm_sze.value,
            'ptfrm_len': self._inp_ptfrm_len.value,
            'lnkge_ang': self._inp_lnkge_ang.value,
            'lnkge_len': self._inp_lnkge_len.value,
            'crank_ang': self._inp_crank_ang.value,
            'crank_len': self._inp_crank_len.value,
            'assly_ang': self._inp_assly_ang.value
        }
        self._design_ok = not(-1 in [val for _, val in self._design.items()])
        if self._design_ok:
            cs_x, cs_y = self.crankshaft
            self._output.plot_crank(x=cs_x, y=cs_y)
            pt_x, pt_y = self.platform
            self._output.plot_ptfrm(x=pt_x, y=pt_y)

    @property
    def crankshaft(self):
        design = self.design
        x = [0,
             design['crank_len']*math.cos(math.radians(design['crank_ang'])),
             design['crank_len']*math.cos(math.radians(design['crank_ang'])) +
             design['lnkge_len']*math.sin(math.radians(design['lnkge_ang']))]
        y = [0,
             design['crank_len']*math.sin(math.radians(design['crank_ang'])),
             design['crank_len']*math.sin(math.radians(design['crank_ang'])) +
             design['lnkge_len']*math.cos(math.radians(design['lnkge_ang']))]
        return x, y

    @property
    def platform(self):
        design = self.design
        p1 = [-0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        p2 = [0.5*design['ptfrm_len'], design['ptfrm_sze'], 0]
        points = [p1, p2, list(Toolkit.apply_rotation(0, 0, -120, p1)), list(Toolkit.apply_rotation(0, 0, -120, p2)),
                  list(Toolkit.apply_rotation(0, 0, 120, p1)), list(Toolkit.apply_rotation(0, 0, 120, p2)), p1]
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        return x, y

    @property
    def validated(self):
        return self._design_ok

    @property
    def design(self):
        return self._design

    def _start_sim(self):
        return

    class _Input:
        def __init__(self, label_text, parent, row, col, limit_low=0, limit_high=sys.maxsize):
            self._parent = parent
            self._me = LabelFrame(self._parent)
            self._me.grid(row=row, column=col)
            self.label = Label(self._me, text=label_text)
            self.entry = Entry(self._me)
            self.submit = Button(self._me, text='Submit', command=lambda: self._set_value(), relief=RIDGE)
            self.label.pack()
            self.entry.pack()
            self.submit.pack()
            self._valid = None
            self._value = -1
            self._limit_low = limit_low
            self._limit_high = limit_high

        def _check_value(self):
            self._valid = False
            try:
                _inp = float(self.entry.get())
                assert(self._limit_low < _inp < self._limit_high)
                self._valid = True
                return _inp
            except (ValueError, AssertionError) as e:
                print(e)
                return -1

        def _set_value(self):
            val = self._check_value()
            if self._valid:
                self.submit.configure(background='green', relief=SUNKEN)
            else:
                self.submit.configure(background='red', relief=RAISED)
            self._value = val

        @property
        def value(self):
            return self._value


class Display:
    def __init__(self, frame):
        self._parent = frame
        self._me = LabelFrame(self._parent)
        self._me.grid(row=0, column=0)
        self._crank_window = Frame(self._me)
        self._crank_window.grid(row=0, column=0)
        self._platform_window = Frame(self._me)
        self._platform_window.grid(row=0, column=1)
        self.plot_crank()
        self.plot_ptfrm()

    def plot_crank(self, x=None, y=None):
        if not(x or y):
            x = []
            y = []
            _lim = None
        else:
            _lim = max(max(x), max(y))
        cvs = GUIPlotter.make_plot(x, y, self._crank_window, plot_title='Crank Shaft', x_axis='X →', y_axis='Z →',
                                   x_size=4, y_size=4, _lim=_lim)
        cvs.get_tk_widget().grid(row=0, column=0)
        cvs.draw()

    def plot_ptfrm(self, x=None, y=None):
        if not(x or y):
            x = []
            y = []
            _lim = None
        else:
            _lim = max(max(x), max(y))
        cvs = GUIPlotter.make_plot(x, y, self._platform_window, plot_title='Platform', x_axis='X →', y_axis='Y →',
                                   x_size=4, y_size=4, _lim=_lim)
        Display._spacer(self._crank_window, row=0, col=1)

        cvs.get_tk_widget().grid(row=0, column=1)
        cvs.draw()

    @staticmethod
    def _spacer(parent, row, col):
        Label(parent, text='\t').grid(row=row, column=col)
