from tkinter import *
from ui.plotting_tools import GUIPlotter


class Controller:
    def __init__(self, frame):
        self._parent = frame
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
        self._x_move = self._Controller(label_text='translation, x:', parent=self._me, col=0)
        self._y_move = self._Controller(label_text='translation, y:', parent=self._me, col=1)
        self._z_move = self._Controller(label_text='translation, z:', parent=self._me, col=2)
        self._alpha = self._Controller(label_text='rotation, alpha:', parent=self._me, col=3)
        self._beta = self._Controller(label_text='rotation, beta', parent=self._me, col=4)
        self._gamma = self._Controller(label_text='rotation, gamma', parent=self._me, col=5)

    class _Controller:
        def __init__(self, label_text, parent, col):
            self._parent = parent
            self._me = LabelFrame(self._parent)
            self._me.grid(row=1, column=col)
            self.label = Label(self._me, text=label_text)
            self.label.grid(row=1, column=col)
            self.throttle = Scale(self._me, from_=-15, to=15, orient=HORIZONTAL, resolution=0.5,
                                  command=lambda x: self._get_move())
            self.throttle.set(0)
            self.throttle.grid(row=2, column=col)

        def _get_move(self):
            print(float(self.throttle.get()))


class Simulation:
    def __init__(self, frame):
        self._parent = frame
        self._me = LabelFrame(self._parent)
        self._me.grid(row=0, column=0)
        x = [1, 2, 3, 4]
        y = [1, 2, 4, 8]
        cvs1 = GUIPlotter.make_plot(x, y, self._me, 'test', 'test', 'test', 6, 4.5)

        cvs1.get_tk_widget().grid(row=0, column=0)
        cvs1.draw()

    @staticmethod
    def _spacer(parent, row, col):
        Label(parent, text='\t').grid(row=row, column=col)