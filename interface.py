import os
from tkinter import *
from tkinter import ttk

import matplotlib
import matplotlib.patches as patches

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use('TkAgg')


class _Logger:

    log_file = os.path.join(os.getcwd(), 'log.txt')

    @staticmethod
    def clear_log():
        open(_Logger.log_file, 'w').close()

    @staticmethod
    def log(text):
        with open(_Logger.log_file, 'a') as f:
            f.write(f'{text}\n')
        print(text)


class _Interface:
    def __init__(self, _child):
        self._child = _child
        self._title = 'SPIKM - Inverse Kinematics'
        self._icon_f = os.path.join(os.getcwd(), 'arm.gif')
        self._size = "700x700"
        self._notebook = None

    def _init_notebook(self):
        self._notebook = self._Notebook(parent=self._child)
        self._notebook.show_notebook()
        self._notebook.setup_tabs()

    def _init_tab(self, tab):
        self._notebook.add_tab(target=tab)

    def _delete_tabs(self):
        self._notebook.clear_tabs()

    def initialize_window(self):
        _icon = PhotoImage(file=self._icon_f)
        self._child.title(self._title)
        self._child.tk.call('wm', 'iconphoto', self._child._w, _icon)
        self._child.geometry(self._size)
        self._child.resizable(height=False, width=False)

    def run_setup(self):
        self._init_notebook()
        self._init_tab(tab='setup')
        self._init_tab(tab='simulation')

    class _Notebook:
        def __init__(self, parent):
            self._tabs = {}
            self._parent = parent
            self.me = ttk.Notebook(self._parent)

        def show_notebook(self):
            self.me.pack(expand=1, fill='both')

        def setup_tabs(self):
            _tabs = ['setup', 'simulation']
            for tb in _tabs:
                _Logger.log(text=f'{tb} tab created')
                self._tabs[tb] = self._Tab(name=tb, parent=self.me)

        def add_tab(self, target):
            if target in self._tabs:
                self._tabs[target].add_tab()

        def clear_tabs(self):
            for tb, _tab in self._tabs.items():
                self.me.forget(_tab.me)
                _tab.kill()
                del _tab
                _Logger.log(f'{tb} tab destroyed')
            self._tabs = {}

        class _Tab:
            def __init__(self, name, parent):
                self._parent = parent
                self._name = name
                self._frames = {}
                self.me = ttk.Frame(self._parent)

            def add_tab(self):
                self._parent.add(self.me, text=self._name.upper())

            def kill(self):
                self.me.destroy()


class RunInterface:
    def __init__(self):
        _Logger.clear_log()
        self._root = Tk()
        self._root_control = _Interface(self._root)
        self._root_control.initialize_window()
        self._root_control.run_setup()
        self._root.mainloop()


if __name__ == '__main__':
    r = RunInterface()