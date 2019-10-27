import os
from tkinter import *
from tkinter import ttk
from ui.setup import Design, Display
from ui.simulation import Controller, Simulation


class _Logger:
    """
    Tools to create a log file for the simulation results and status
    """
    log_file = os.path.join(os.getcwd(), 'log.txt')

    @staticmethod
    def clear_log():
        """
        clear the existing log file
        :return:
        """
        open(_Logger.log_file, 'w').close()
        return

    @staticmethod
    def log(text):
        """
        add a new line to the log file
        :param text: str, line to be added
        :return:
        """
        with open(_Logger.log_file, 'a') as f:
            f.write(f'{text}\n')
        print(text)
        return


class _Execute:
    """
    Program control class
    """
    def __init__(self, _child):
        """
        define properties to control the execution of the design and simulation of the Stewart Platform in 6-dof
        :param _child: tk.Tk, running the display of the program
        """
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
        """
        initialize the tk notebook containing the setup and simulation tabs of the program
        :return:
        """
        self._window = self._Window(parent=self._child, master=self.program_controller)
        self._window.show_notebook()
        self._window.setup_tabs()
        return

    def _init_tab(self, tab):
        """
        initialize a given tab
        :param tab: str, indicating the tab name to be initialized
        :return:
        """
        self._window.add_tab(target=tab)
        return

    def _delete_tabs(self):
        """
        delete all tabs belonging to the tk notebook
        :return:
        """
        self._window.clear_tabs()

    def initialize_window(self):
        """
        non protected member to initialize the program controller window by updating the icon, title and geometry
        :return:
        """
        _icon = PhotoImage(file=self._icon_f)
        self._child.title(self._title)
        self._child.tk.call('wm', 'iconphoto', self._child._w, _icon)
        self._child.geometry(self._size)
        self._child.resizable(height=False, width=False)

    def run_setup(self):
        """
        non protected member to initialize the program window
        :return:
        """
        self._init_notebook()
        self._init_tab(tab='setup')
        self._init_tab(tab='simulation')

    def shutdown(self):
        self._delete_tabs()

    @property
    def validated(self):
        return self._validated

    def validate(self):
        """
        used to coerce the validation of the design belonging to the current program execution
        :return:
        """
        self._window.simulation_child.start_simulation(self._window.design_child.design)
        self._validated = True
        _Logger.log("Design Validated")
        return

    def save_design(self, checked_design):
        """
        save the design for the current program execution
        :param checked_design:
        :return:
        """
        self._design = checked_design
        _Logger.log(f"Design saved - \n{str(self._design)}")
        return

    @property
    def design(self):
        return self._design

    def set_coordinates(self, coordinates):
        """
        move the Platform in the current execution to the coordinates passed as arguments
        :param coordinates: dict, containing the 6-dof position to which the platform is to be moved
        :return:
        """
        self._coordinates = coordinates
        self._window.simulation_child.update_simulation(self._coordinates)
        return

    @property
    def coordinates(self):
        return self._coordinates

    class _Window:
        """
        Instances of this class develop a tk notebook with setup and simulation tabs in the calling tk parent
        """
        def __init__(self, parent, master):
            """
            initialize the tk notebook for simulation and setup widget population
            :param parent: tk.Frame, where the notebook is populated
            :param master: interface._Execute, running the program
            """
            self.tabs = {}
            self._parent = parent
            self.me = ttk.Notebook(self._parent)
            self._master = master
            self.output_child = None
            self.design_child = None
            self.simulation_child = None
            self.controller_child = None

        def show_notebook(self):
            self.me.pack(expand=1, fill='both')
            return

        def setup_tabs(self):
            """
            setup simulation and setup tabs
            :return:
            """
            _tabs = ['setup', 'simulation']
            for tb in _tabs:
                _Logger.log(text=f'{tb} tab created')
                self.tabs[tb] = self._Tab(name=tb, parent=self.me, driver=self, master=self._master)
            return

        def add_tab(self, target):
            """
            add a given tab to the notebook
            :param target: str, tab to be added to the notebook
            :return:
            """
            if target in self.tabs:
                self.tabs[target].add_tab()
            return

        def clear_tabs(self):
            """
            remove all tabs
            :return:
            """
            for tb, _tab in self.tabs.items():
                self.me.forget(_tab.me)
                _tab.kill()
                del _tab
                _Logger.log(f'{tb} tab destroyed')
            self.tabs = {}

        class _Tab:
            """
            Define properties for a tk.Tab populated in the program controller's ttk.Notebook
            """
            def __init__(self, name, parent, driver, master):
                """
                initialize tab properties and behaviour
                :param name: str, name of the tab
                :param parent: ttk.Notebook, where the tab is to be added
                :param driver: interface._Execute._Window, calling the tab setup
                :param master: interface._Execute, running the program
                """
                self._parent = parent
                self._driver = driver
                self._name = name
                self._frames = {}
                self.me = ttk.Frame(self._parent)
                self._master = master

            def add_tab(self):
                """
                add the given tab to the notebook
                :return:
                """
                self._parent.add(self.me, text=self._name.upper())
                if self._name == 'setup':
                    self._driver.output_child = Display(frame=self.me)
                    self._driver.design_child = Design(frame=self.me, driver=self._driver, master=self._master)
                elif self._name == 'simulation':
                    self._driver.simulation_child = Simulation(frame=self.me)
                    self._driver.controller_child = Controller(frame=self.me, master=self._master)
                return

            def kill(self):
                """
                destroy the tab
                :return:
                """
                self.me.destroy()


class RunInterface:
    """
    run program execution by initializing _Execute and calling non-protected members
    """
    def __init__(self):
        _Logger.clear_log()
        self._root = Tk()
        self._root_control = _Execute(self._root)
        self._root_control.initialize_window()
        self._root_control.run_setup()
        self._root.mainloop()


if __name__ == '__main__':
    r = RunInterface()
