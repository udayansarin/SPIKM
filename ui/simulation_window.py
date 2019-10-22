from tkinter import *
from ui.plotting_tools import GUIPlotter


class Controller:
    def __init__(self, frame, master):
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

    def _move(self):
        x = self._x_move.value
        y = self._y_move.value
        z = self._z_move.value
        a = self._a_move.value
        b = self._b_move.value
        g = self._g_move.value
        return [x, y, z, a, b, g]

    def update_coordinates(self):
        self._master.set_coordinates(self._move())

    class _Controller:
        def __init__(self, label_text, parent, col, driver, master):
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