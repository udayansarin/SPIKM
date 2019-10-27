import numpy as np
import sys
from tkinter import *

from dynamics.platform import Platform
from ui.plotting import GUIPlotter


class Design:
    """
    Tools and tkinter controls for design of the Stewart Platform
    """
    def __init__(self, frame, driver, master):
        """
        initialize properties and features for the design of the Stewart Platform
        :param frame: tk.Frame, where the controller is to be placed
        :param driver: interface._Window, running the design and display setup
        :param master: interface._Execute, running the program
        """
        self._parent = frame
        self._driver = driver
        print(f'Program master in class {type(self).__name__}:')
        print(master)
        self._master = master
        self._me = LabelFrame(self._parent)
        self._me.grid(row=1, column=0)
        self._inp_ptfrm_sze = None
        self._inp_ptfrm_len = None
        self._inp_crank_ang = None
        self._inp_assly_ofs = None
        self._inp_assly_ang = None
        self._inp_crank_len = None
        self._inp_lnkge_len = None
        self._inp_plane_dst = None
        self._simulate_strt = None
        self._design_update = None
        self._design_ok = None
        self._design = {}
        self._show_widgets()

    def _show_widgets(self):
        """
        show input widgets to define platform design parameters
        :return:
        """
        self._inp_ptfrm_sze = self._Input(label_text='Platform Centre Length', parent=self._me, row=1, col=0)
        self._inp_ptfrm_len = self._Input(label_text='Platform Edge Length', parent=self._me, row=1, col=1)
        self._inp_lnkge_len = self._Input(label_text='Linkage Length', parent=self._me, row=1, col=2)
        self._inp_crank_len = self._Input(label_text='Crank Length', parent=self._me, row=1, col=3)
        self._inp_crank_ang = self._Input(label_text='Initial Crank Angle', parent=self._me, row=1, col=4,
                                          limit_low=-90, limit_high=90)
        self._inp_assly_ofs = self._Input(label_text='Assembly Offset', parent=self._me, row=1, col=5,
                                          limit_low=-90, limit_high=90)
        self._inp_assly_ang = self._Input(label_text='Assembly Angle', parent=self._me, row=1, col=6,
                                          limit_low=-90, limit_high=90)
        self._inp_plane_ofs = self._Input(label_text='Motor - Platform Offset', parent=self._me, row=2, col=0)
        self._design_update = Button(self._me, text='Update', command=lambda: self._update_design(), width=11,
                                     height=2, font=('Helvetica', '15'))
        self._design_update.grid(row=2, column=5)
        self._simulate_strt = Button(self._me, text='Simulate', command=lambda: self._start_sim(), width=11,
                                     height=2, font=('Helvetica', '15'))
        self._simulate_strt.grid(row=2, column=6)
        return

    def _update_design(self):
        """
        update the platform design on the basis of tk.Entry widget values
        :return:
        """
        self._design = {
            'ptfrm_sze': self._inp_ptfrm_sze.value,
            'ptfrm_len': self._inp_ptfrm_len.value,
            'lnkge_len': self._inp_lnkge_len.value,
            'crank_ang': self._inp_crank_ang.value,
            'crank_len': self._inp_crank_len.value,
            'assly_ang': self._inp_assly_ang.value,
            'assly_ofs': self._inp_assly_ofs.value,
            'plane_ofs': self._inp_plane_ofs.value
        }
        self._design_ok = not(-1 in [val for _, val in self._design.items()])
        ptfrm = Platform(design=self._design)
        platform, linkages, motors, feasible = ptfrm.run.get_platform(starting=True)
        if self._design_ok and not(False in feasible):
            self._driver.output_child.plot_ptfrm(x=platform[0], y=platform[1], z=platform[2], linkage_x=linkages['x'],
                                                 linkage_y=linkages['y'], linkage_z=linkages['z'])
            print('Saving design to Program Master at:')
            print(self._master)
            self._master.save_design(self._design)
        else:
            print('Error: Unable to save incomplete/erroneous design!')
        return

    @property
    def design(self):
        return self._design

    def _start_sim(self):
        """
        start the simulation on the basis of the stored design, if it is validated
        :return:
        """
        if self._design_ok:
            print('confirming design validated at')
            print(self._master)
            self._driver.me.select(self._driver.tabs['simulation'].me)
            self._master.validate()
        else:
            print("Error: Design not complete/saved!")
        return

    class _Input:
        """
        Define amalgamation of tkinter widgets as a single design parameter entry
        """
        def __init__(self, label_text, parent, row, col, limit_low=0, limit_high=sys.maxsize):
            """
            initialize a design parameter input field
            :param label_text: str, containing the field header
            :param parent: tk.Frame, where the input is to be populated
            :param row: int, the row in the tk.Frame grid where the input field is populated
            :param col: int, the column in the tk.Frame grid where the input field is populated
            :param limit_low: int, the lower limit which the input field will accept as a valid value
            :param limit_high: int, the higher limit which the input field will accepts as a valid value
            """
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
            """
            check if the inputted value is valud
            :return: float/int, input value or -1 if the value is not valid
            """
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
            """
            provide a user prompt for the input value by changing the accept button to green (if valid) red (if invalid)
            :return:
            """
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
    """
    Tools to show the current design state of the Stewart Platform
    """
    def __init__(self, frame):
        """
        initialize behaviour and tk instances to display the design of the Stewart Platform
        :param frame: tk.Frame, where the display is to be populated
        """
        self._parent = frame
        self._me = LabelFrame(self._parent)
        self._me.grid(row=0, column=0)
        self._display_iso = Frame(self._me)
        self._display_iso.grid(row=0, column=0)
        self._display_top = Frame(self._me)
        self._display_top.grid(row=0, column=1)
        self.plot_ptfrm()

    def plot_ptfrm(self, x=None, y=None, z=None, linkage_x=None, linkage_y=None, linkage_z=None):
        """
        plot the platform into the display windows
        :param x: list, 7 elements for the x geometry of the Stewart Platform
        :param y: list, y geometry of the Stewart Platform
        :param z: list, z geometry of the Stewart Platform
        :param linkage_x: list, 6x3 containing the x coordinates of the six linkages
        :param linkage_y: list, y coordinates for the linkages
        :param linkage_z: list, z coordinates for the linkages
        :return:
        """
        if not(x or y or z):
            x = []
            y = []
            z = []
            _lim = 1
            linkage_x = []
            linkage_y = []
            linkage_z = []
        else:
            _lim = max(np.max(linkage_x), np.max(linkage_z), abs(np.min(linkage_z)))
        iso = GUIPlotter.plot_3d(x, y, z, self._display_iso, linkage_x, linkage_y, linkage_z, title='Isometric View',
                                 _lim=_lim, fig_size=(4, 4))
        iso.get_tk_widget().grid(row=0, column=0)
        iso.draw()

        Display._spacer(self._display_iso, row=0, col=1)

        top = GUIPlotter.plot_3d(x, y, z, self._display_top, linkage_x, linkage_y, linkage_z, title='Top View',
                                 _lim=_lim, fig_size=(4, 4))
        top.get_tk_widget().grid(row=0, column=2)
        top.draw()
        return

    @staticmethod
    def _spacer(parent, row, col):
        """
        add tk.Label to space both simulation output plots
        :param parent: tk.Frame, containing the spacer
        :param row: int, row in the tk.Frame grid to populate
        :param col: int, col in the tk.Frame grid to populate
        :return:
        """
        Label(parent, text='\t').grid(row=row, column=col)
        return
