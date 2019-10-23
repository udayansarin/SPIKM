import math
import sys
from tkinter import *

from dynamics.spikm_trig import Toolkit
from dynamics.platform import Platform
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
    def __init__(self, frame, driver, master):
        self._parent = frame
        self._driver = driver
        print(f'Program master in class {type(self).__name__}:')
        print(master)
        self._master = master
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
        return

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
            cs_x, cs_z = self.crankshaft
            self._driver.output_child.plot_crank(x=cs_x, y=cs_z)
            pt_x, pt_y = self.platform
            self._driver.output_child.plot_ptfrm(x=pt_x, y=pt_y)
            print('Saving design to Program Master at:')
            print(self._master)
            self._master.save_design(self._design)
        else:
            print('Error: Unable to save incomplete design!')
        return

    @property
    def design(self):
        return self._design

    @property
    def crankshaft(self):
        design = self._design
        crank_con = Toolkit.get_xz(length=design['crank_len'], theta=math.radians(design['crank_ang']))
        con_node = Toolkit.get_xz(length=design['lnkge_len'], theta=math.radians(90-design['lnkge_ang']))
        x = [0, crank_con['x'], crank_con['x'] + con_node['x']]
        z = [0, crank_con['z'], crank_con['z'] + con_node['z']]
        return x, z

    @property
    def platform(self):
        points = Platform.generate(design=self._design)
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        return x, y

    def _start_sim(self):
        if self._design_ok:
            print('confirming design validated at')
            print(self._master)
            self._master.validate()
        else:
            print("Error: Design not complete/saved!")
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
            return

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
        return

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
        return

    @staticmethod
    def _spacer(parent, row, col):
        Label(parent, text='\t').grid(row=row, column=col)
        return
