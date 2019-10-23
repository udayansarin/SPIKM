import os
from tkinter import *
from tkinter import ttk
from ui.setup_window import Design, Display
from ui.simulation_window import Controller, Simulation


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


class _Controller:
    def __init__(self, _child):
        self._child = _child
        self._title = 'SPIKM - Inverse Kinematics'
        self._icon_f = os.path.join(os.getcwd(), 'arm.gif')
        self._size = "905x600"
        self._window = None
        self._validated = False
        self._design = None
        self._coordinates = None
        self.program_controller = self

    def _init_notebook(self):
        self._window = self._Window(parent=self._child, master=self.program_controller)
        self._window.show_notebook()
        self._window.setup_tabs()

    def _init_tab(self, tab):
        self._window.add_tab(target=tab)

    def _delete_tabs(self):
        self._window.clear_tabs()

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

    def shutdown(self):
        self._delete_tabs()

    @property
    def validated(self):
        return self._validated

    def validate(self):
        self._window.simulation_child.start_simulation(self._window.design_child.design)
        self._validated = True
        return

    def save_design(self, checked_design):
        self._design = checked_design
        return

    @property
    def design(self):
        return self._design

    def set_coordinates(self, coordinates):
        self._coordinates = coordinates
        print(self._coordinates)
        self._window.simulation_child.update_simulation(self._coordinates)

    @property
    def coordinates(self):
        return self._coordinates

    class _Window:
        def __init__(self, parent, master):
            self._tabs = {}
            self._parent = parent
            self.me = ttk.Notebook(self._parent)
            self._master = master
            self.output_child = None
            self.design_child = None
            self.simulation_child = None
            self.controller_child = None

        def show_notebook(self):
            self.me.pack(expand=1, fill='both')

        def setup_tabs(self):
            _tabs = ['setup', 'simulation']
            for tb in _tabs:
                _Logger.log(text=f'{tb} tab created')
                self._tabs[tb] = self._Tab(name=tb, parent=self.me, driver=self, master=self._master)

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
            def __init__(self, name, parent, driver, master):
                self._parent = parent
                self._driver = driver
                self._name = name
                self._frames = {}
                self.me = ttk.Frame(self._parent)
                self._master = master

            def add_tab(self):
                self._parent.add(self.me, text=self._name.upper())
                if self._name == 'setup':
                    self._driver.output_child = Display(frame=self.me)
                    self._driver.design_child = Design(frame=self.me, driver=self._driver, master=self._master)
                elif self._name == 'simulation':
                    self._driver.simulation_child = Simulation(frame=self.me)
                    self._driver.controller_child = Controller(frame=self.me, master=self._master)
                return

            def kill(self):
                self.me.destroy()


class RunInterface:
    def __init__(self):
        _Logger.clear_log()
        self._root = Tk()
        self._root_control = _Controller(self._root)
        self._root_control.initialize_window()
        self._root_control.run_setup()
        #self._root_control.shutdown()
        self._root.mainloop()


if __name__ == '__main__':
    r = RunInterface()
