from tkinter import *
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
        self._inp_pltfrm_angle = None
        self._inp_pltfrm_len = None
        self._inp_linkage_angle = None
        self._inp_crank_angle = None
        self._inp_assembly_angle = None
        self._inp_crank_len = None
        self._inp_linkage_len = None
        self._show_widgets()

    def _show_widgets(self):
        self._inp_pltfrm_angle = self._Input(label_text='Platform Edge Angle:', parent=self._me, col=0)
        self._inp_pltfrm_len = self._Input(label_text='Platform Edge Length:', parent=self._me, col=1)
        self._inp_linkage_angle = self._Input(label_text='Initial Linkage Angle:', parent=self._me, col=2)
        self._inp_linkage_length = self._Input(label_text='Linkage Length:', parent=self._me, col=3)
        self._inp_crank_angle = self._Input(label_text='Initial Crank AngleL', parent=self._me, col=4)
        self._inp_crank_len = self._Input(label_text='Crank Length:', parent=self._me, col=5)
        self._inp_assembly_angle = self._Input(label_text='Assembly Angle:', parent=self._me, col=6)

    class _Input:
        def __init__(self, label_text, parent, col):
            self._parent = parent
            self._me = LabelFrame(self._parent)
            self._me.grid(row=1, column=col)
            self.label = Label(self._me, text=label_text)
            self.entry = Entry(self._me)
            self.label.pack()
            self.entry.pack()


class Display:
    def __init__(self, frame):
        self._parent = frame
        self._me = LabelFrame(self._parent)
        self._me.grid(row=0, column=0)
        self._crank_window = Frame(self._me)
        self._crank_window.grid(row=0, column=0)
        self._platform_window = Frame(self._me)
        self._platform_window.grid(row=0, column=1)
        x = [1, 2, 3, 4]
        y = [1, 2, 4, 8]
        cvs1 = GUIPlotter.make_plot(x, y, self._crank_window, 'test', 'test', 'test', 4, 4)
        cvs2 = GUIPlotter.make_plot(y, x, self._platform_window, 'test', 'test', 'test', 4, 4)

        cvs1.get_tk_widget().grid(row=0, column=0)
        cvs1.draw()
        Display._spacer(self._crank_window, row=0, col=1)

        cvs2.get_tk_widget().grid(row=0, column=1)
        cvs2.draw()

    @staticmethod
    def _spacer(parent, row, col):
        Label(parent, text='\t').grid(row=row, column=col)
