import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use('TkAgg')


class GUIPlotter:
    """
     Tools to create a matplotlib tkinter plot using canvas tools for features of the Stewart Platform
    """
    @staticmethod
    def plot_3d(_x, _y, _z, _window, linkage_x, linkage_y, linkage_z, title="Stewart Platform Simulation", _lim=1,
                fig_size=None):
        """

        :param _x: list, x coordinates of the platform
        :param _y: list, y coordinates of the platform
        :param _z: list, z coordinates of the platform
        :param _window: tk.Frame, where the plot is to be displayed
        :param linkage_x: list, x coordinates of the linkage
        :param linkage_y: list, y coordinates of the linkage
        :param linkage_z: list, z coordinates of the linkage
        :param title: str, title of the plot
        :param _lim: float, limits to be displayed for each axis of the plot
        :param fig_size: list, containing x_size and y_size for the plot
        :return: FigureCanvasTkAgg, canvas containing the plot
        """
        if fig_size:
            fig = Figure(figsize=fig_size)
        else:
            fig = Figure()
        _lim *= 1.1
        simulation = Axes3D(fig)
        simulation.text2D(0.05, 0.95, title, transform=simulation.transAxes)
        simulation.set_xlabel('X')
        simulation.set_ylabel('Y')
        simulation.set_zlabel('Z')
        simulation.set_zlim(-_lim, _lim)
        simulation.set_xlim(-_lim, _lim)
        simulation.set_ylim(-_lim, _lim)
        simulation.plot(_x, _y, _z)
        for i, _ in enumerate(linkage_x):
            simulation.plot(linkage_x[i], linkage_y[i], linkage_z[i])
        if 'TOP' in title.upper():
            simulation.view_init(90, -90)
        canvas = FigureCanvasTkAgg(fig, master=_window)
        simulation.figure.canvas = canvas
        simulation.mouse_init()
        return canvas

    @staticmethod
    def plot_motors(_window, motor_angles=[0.0]*6, _incompatible=[True]*6):
        """
        generate a control panel display for the platform motor angles
        :param _window: tk.Frame, where the plot is to be displayed
        :param motor_angles: list, containing the angles of each motor
        :param _incompatible: list, containing bools corresponding to whether the motor can achieve the move
        :return: FigureCanvasTkAgg, canvas containing the plot
        """
        fig = Figure(figsize=(2, 5))
        base = 610
        for i, angle in enumerate(motor_angles):
            motor_num = i + 1
            subplot_num = base + motor_num
            marker = f'${"%+.3f" % angle}$'
            color = 'green' if _incompatible[i] else 'red'
            m = fig.add_subplot(subplot_num)
            m.title.set_text(f'Motor{motor_num}')
            m.scatter([angle], [0], marker=marker, s=600, c=color)
            m.set_xlim([-90, 90])
            m.set_ylim([-1, 1])
            m.set_yticks([])
        canvas = FigureCanvasTkAgg(fig, master=_window)
        fig.tight_layout()
        return canvas
