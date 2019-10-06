import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use('TkAgg')


class GUIPlotter:
    """
    Generic class to create a matplotlib tkinter plot using canvas tools
    """

    @staticmethod
    def make_plot(_x, _y, _window, x_axis=None, y_axis=None, plot_title=None, x_size=None, y_size=None):
        """
        Create a matplotlib plot instance in a wkinter frame/window
        :param _x: x list to plot
        :param _y: y list to plot
        :param _window: tkinter widget to develop the plot in
        :param x_axis: x axis label
        :param y_axis: y axis label
        :param plot_title: plot title
        :return:
        """
        fig = Figure(figsize=(x_size, y_size))
        a = fig.add_subplot(111)
        a.set_title(plot_title)
        a.set_xlabel(x_axis)
        a.set_ylabel(y_axis)
        a.grid()
        a.plot(_x, _y, color='red')

        canvas = FigureCanvasTkAgg(fig, master=_window)
        fig.tight_layout()
        return canvas
