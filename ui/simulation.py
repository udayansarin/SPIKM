import numpy as np
from tkinter import *
from ui.plotting import GUIPlotter
from dynamics.platform import Platform


class Controller:
    """
    Generate a controller for the Stewart Platform
    """
    def __init__(self, frame, master):
        """
        define widgets and parameters for the Stewart Platform Controller
        :param frame: tk.Frame, where the controller is to be placed
        :param master: interface._Execute, running the program
        """
        self._parent = frame
        print(f'Program master in class {type(self).__name__}:')
        print(master)
        self._master = master
        self._me = LabelFrame(self._parent)
        self._me.grid(row=1, column=0)
        self._x_move = None
        self._y_move = None
        self._z_move = None
        self._alpha = None
        self._beta = None
        self._gamma = None
        self._show_widgets()

    def _show_widgets(self):
        """
        define individual controllers for each DOF of the platform
        :return:
        """
        self._x_move = self._Controller(label_text='translation, x:', parent=self._me, col=0,
                                        driver=self, master=self._master)
        self._y_move = self._Controller(label_text='translation, y:', parent=self._me, col=1,
                                        driver=self, master=self._master)
        self._z_move = self._Controller(label_text='translation, z:', parent=self._me, col=2,
                                        driver=self, master=self._master)
        self._a_move = self._Controller(label_text='rotation, alpha:', parent=self._me, col=3,
                                        driver=self, master=self._master)
        self._b_move = self._Controller(label_text='rotation, beta', parent=self._me, col=4,
                                        driver=self, master=self._master)
        self._g_move = self._Controller(label_text='rotation, gamma', parent=self._me, col=5,
                                        driver=self, master=self._master)
        return

    def _move(self):
        """
        get the target orientation of the Stewart Platform from the controller widgets
        :return: dict, containing 6-dof orientation in space {'x', 'y', 'z', 'a', 'b', 'g'}
        """
        return {
            'x': self._x_move.value,
            'y': self._y_move.value,
            'z': self._z_move.value,
            'a': self._a_move.value,
            'b': self._b_move.value,
            'g': self._g_move.value
        }

    def update_coordinates(self):
        """
        update the position of the Stewart Platform in the program controlling instance of interface._Execute
        :return:
        """
        self._master.set_coordinates(self._move())
        return

    class _Controller:
        """
        Protected member, instances of this class show slider properties associated with a give platform dof
        """
        def __init__(self, label_text, parent, col, driver, master):
            """
            define parameters and properties for the given dof controller which shows tkinter slider/throttle behaviour
            :param label_text: str, to be positioned as the header for the dof slider
            :param parent: tk.Frame, where the slider controller is to be populated
            :param col: int, column in the tk grid to populate
            :param driver: ui.simulation.Controller, containing this axis controller
            :param master: interface._Execute, running the program
            """
            self._master = master
            self._parent = parent
            self._driver = driver
            self._value = 0
            self._me = LabelFrame(self._parent)
            self._me.grid(row=1, column=col)
            self.label = Label(self._me, text=label_text)
            self.label.grid(row=1, column=col)
            self.throttle = Scale(self._me, from_=-15, to=15, orient=HORIZONTAL, resolution=0.5,
                                  command=lambda x: self._get_move())
            self.throttle.set(0)
            self.throttle.grid(row=2, column=col)

        def _get_move(self):
            """
            get the position which the current dof needs to be driven to when the slider is re-positioned
            :return:
            """
            if not self._master.validated:
                self.throttle.set(0)
                print("Error: Complete Design First")
                return
            self._value = float(self.throttle.get())
            self._driver.update_coordinates()
            return

        @property
        def value(self):
            return self._value


class Simulation:
    """
    Instances of this class are used to display the Stewart Platform Simulation
    """
    def __init__(self, frame):
        """
        Initialize properties and parameters to show the Stewart Platform simulation
        :param frame: tk.Frame, where the simulation is to be displayed
        """
        self._parent = frame
        self._sim = LabelFrame(self._parent)
        self._sim.grid(row=0, column=0)
        self._motor = LabelFrame(self._parent)
        self._motor.grid(row=0, column=1)
        self.ptfrm = None
        self.plot_limit = None
        self._init_empty_plots()

    def _init_empty_plots(self):
        """
        initialize empty plot windows where the simulation is to be displayed
        :return:
        """
        x = []
        y = []
        z = []
        sim = GUIPlotter.plot_3d(x, y, z, self._sim, x, y, z)
        sim.get_tk_widget().grid(row=0, column=0)
        sim.draw()

        motors = GUIPlotter.plot_motors(_window=self._motor)
        motors.get_tk_widget().grid(row=0, column=0)
        motors.draw()
        return

    def _update_plot(self, platform, linkages):
        """
        update the plot for the stewart platform
        :param platform: list, 7x3 containing the coordinates for the platform in each dimension per row
        :param linkages: dict, containing three 6x3 lists for each coordinate to plot platform linkages
        :return:
        """
        if not self.plot_limit:
            self.plot_limit = max(np.max(linkages['x']), np.max(linkages['y']), abs(np.min(linkages['z'])))

        sim = GUIPlotter.plot_3d(_x=platform[0], _y=platform[1], _z=platform[2], _window=self._sim,
                                 linkage_x=linkages['x'], linkage_y=linkages['y'], linkage_z=linkages['z'],
                                 _lim=self.plot_limit)
        sim.get_tk_widget().grid(row=0, column=0)
        sim.draw()
        return

    def _update_motors(self, motors, motor_warnings):
        """
        update the motor plots
        :param motors: list, containing the angle of each motor in degrees
        :param motor_warnings: list, containing bools indicating if the given move is feasible
        :return:
        """
        motors = GUIPlotter.plot_motors(_window=self._motor, motor_angles=motors, _incompatible=motor_warnings)
        motors.get_tk_widget().grid(row=0, column=0)
        motors.draw()
        return

    def start_simulation(self, design):
        """
        start the Stewart Platform simulation
        :param design: dict, containing the design of the Stewart Platform, see ui.setup.Design._update_design
        :return:
        """
        self.ptfrm = Platform(design=design)
        platform, linkages, motors, feasible = self.ptfrm.run.get_platform(starting=True)
        if False in feasible:
            print("Design is Erroneous!")
        else:
            self._update_plot(platform=platform, linkages=linkages)
            self._update_motors(motors=motors, motor_warnings=feasible)
        return

    def update_simulation(self, coordinates):
        """
        update the stewart platform simulation on the basis of updated coordinates of the platform
        :param coordinates: list, 7x3 containing the position of the platform nodes
        :return:
        """
        self.ptfrm.run.update_platform(coordinates)
        platform, linkages, motors, feasible = self.ptfrm.run.get_platform(starting=False)
        if False in feasible:
            print("Design cannot make this move!")
        else:
            self._update_plot(platform=platform, linkages=linkages)
        self._update_motors(motors=motors, motor_warnings=feasible)
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
