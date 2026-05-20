"""
Settings window for the Game of Life application.

This module provides a Tkinter-based settings window that allows users to configure
game rules, grid dimensions, and cell size for the Conway's Game of Life simulation.
"""

import tkinter as tk
import logging

class SettingsWindow:
    """
    A Tkinter window for configuring Game of Life settings.

    This class creates a modal dialog window with input fields for neighborhood type,
    birth and survival rules, grid dimensions (rows and columns), and cell size.
    Changes are applied via a callback function when the user saves.

    Attributes:
    """

    # Color palette
    CLR_BG = "#112736"
    CLR_DEAD_CELL = "#A3A3A1"
    CLR_ALIVE_CELL = "#ffff00"
    CLR_CELL_BORDER = ""
    CLR_CLK_BTN = "#456882" # Clickable button color
    CLR_GREYED_BTN = "#D2C1B6" # Greyed-out button color
    CLR_BTN_BD = "#234C6A" # Button border
    CLR_TEXT = "#ffffff" # Text color
    
    STYLE_GREYED_BTN = {
        "bg": CLR_GREYED_BTN,
        "fg": CLR_TEXT,
        "bd": 0,
        "highlightthickness": 2,
        "relief": "flat",
        "highlightbackground": CLR_BTN_BD,
        "activebackground": CLR_BTN_BD,
        "activeforeground": CLR_TEXT,
        "padx": 5,
        "font": ("Segoe UI", 9)
    }

    STYLE_CLK_BTN = {
        **STYLE_GREYED_BTN,
        "bg": CLR_CLK_BTN
    }

    STYLE_LABEL = {
        "bg": CLR_BG,
        "fg": CLR_TEXT
    }

    STYLE_LABEL_ERROR = {
        "bg": CLR_BG,
        "fg": "red"
    }

    STYLE_ENTRY = {
        "bg": CLR_CLK_BTN,
        "fg": "#ffffff",
        "relief": "flat",
        "highlightthickness": 2,
        "highlightbackground": CLR_CLK_BTN, 
        "highlightcolor": CLR_BTN_BD,
        "bd": 0,
        "width": 10 
    }

    def __init__(
            self, root: tk.Tk, rows: int, cols: int, cell_size: int,
            neighborhoods: list[str], current_neighborhood: str,
            birth: set, survive: set, rand_density: float, seed: int | str,
            on_save_callback: function
        ):
        """
        Initializes the settings window with the provided parameters.
        
        Args:
            root: The main Tkinter application window.
            rows: Current number of rows in the grid.
            cols: Current number of columns in the grid.
            cell_size: Current size of each cell in pixels.
            neighborhoods: List of available neighborhood types (e.g., "Moore", "Von Neumann").
            current_neighborhood: The currently selected neighborhood type.
            birth: Set of the current cell birth rule.
            survive: Set of the current cell survival rule.
            on_save_callback: Function to call with new settings when the user saves.
        """

        self.root = root
        self.rows = rows
        self.cols = cols
        self.neighborhoods = neighborhoods
        self.current_neighborhood = current_neighborhood
        self.birth = birth
        self.survive = survive
        self.cell_size = cell_size
        self.rand_density = rand_density
        self.seed = seed
        self.callback = on_save_callback

        ##### Creating the window
        self.settings_window = tk.Toplevel(self.root, bg=self.CLR_BG)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x350")
        self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.destroy)

        ##### Creating the buttons frame
        self.settings_btns_frame = tk.Frame(self.settings_window, bg=self.CLR_BG)
        self.settings_btns_frame.pack()

        self.entry_error_lbl = tk.Label(
            self.settings_btns_frame, text="",
            **self.STYLE_LABEL_ERROR
        )

        self.save_settings_btn = tk.Button(
            self.settings_btns_frame, text="Save", **self.STYLE_CLK_BTN,
            command=self.send_settings_back
        )
        self.settings_window.bind('<Return>', lambda event: self.save_settings_btn.invoke())

        ##### Notice label - Row 0
        self.info_lbl = tk.Label(
            self.settings_btns_frame, text="All inputs must be integers",
            **self.STYLE_LABEL
        )
        
        ######################
        ##### Game Rules #####
        ##### Column 0-1 #####
        ######################

        ##### Row 1 #####
        self.rules_lbl = tk.Label(
            self.settings_btns_frame, text="Game Rules (MCell)",
            **self.STYLE_LABEL
        )

        ##### Neighbothood Selection - Row 2

        # Column 0
        self.neighborhood_lbl = tk.Label(
            self.settings_btns_frame, text="Neighborhood",
            **self.STYLE_LABEL
        )

        # Column 1
        self.neighborhoods_opts = tk.StringVar(value=self.current_neighborhood)
        self.neighborhoods_opts_list = tk.OptionMenu(
            self.settings_btns_frame, self.neighborhoods_opts,
            *self.neighborhoods
        )
        self.neighborhoods_opts_list.config(**self.STYLE_CLK_BTN)
        self.neighborhoods_opts_list["menu"].config(
            bg=self.CLR_BG, fg=self.CLR_TEXT, bd=0, relief="flat"
        )

        ##### Birth Setting - Row 3

        self.birth_lbl = tk.Label(
            self.settings_btns_frame, text="Birth",
            **self.STYLE_LABEL
        )
        self.birth_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY,
            validate="key",
            validatecommand=(self.root.register(self.validate_rulestring), '%P')
        )
        self.birth_entry.insert(0, "".join(map(str, sorted(self.birth))))

        ##### Survive Setting - Row 4

        self.survive_lbl = tk.Label(
            self.settings_btns_frame, text="Survive",
            **self.STYLE_LABEL
        )
        self.survive_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY,
            validate="key",
            validatecommand=(self.root.register(self.validate_rulestring), '%P')
        )
        self.survive_entry.insert(0, "".join(map(str, sorted(self.survive))))

        ##### Column 2 #####

        self.gui_settings_lbl = tk.Label(
            self.settings_btns_frame, text="Grid Settings",
            **self.STYLE_LABEL
        )
        self.cols_lbl = tk.Label(
            self.settings_btns_frame, text="Columns",
            **self.STYLE_LABEL
        )
        self.cols_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY,
            validate="key",
            validatecommand=(self.root.register(self.validate_dimensions), '%P')
        )
        self.cols_entry.insert(0, str(self.cols))

        self.rows_lbl = tk.Label(
            self.settings_btns_frame, text="Rows",
            **self.STYLE_LABEL
        )
        self.rows_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY,
            validate="key",
            validatecommand=(self.root.register(self.validate_dimensions), '%P')
        )
        self.rows_entry.insert(0, str(self.rows))

        self.cell_size_lbl = tk.Label(
            self.settings_btns_frame, text="Cell Size",
            **self.STYLE_LABEL
        )
        self.cell_size_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY,
            validate="key",
            validatecommand=(self.root.register(self.validate_dimensions), '%P')
        )
        self.cell_size_entry.insert(0, str(self.cell_size))

        ##### Randomness Settings #####

        self.rand_settings_lbl = tk.Label(
            self.settings_btns_frame, text="Randomness Settings",
            **self.STYLE_LABEL
        )

        self.rand_density_lbl = tk.Label(
            self.settings_btns_frame, text="Density as %",
            **self.STYLE_LABEL
        )
        self.rand_density_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY
        )
        self.rand_density_entry.insert(0, str(self.rand_density * 100.0))

        self.seed_lbl = tk.Label(
            self.settings_btns_frame, text="Seed",
            **self.STYLE_LABEL
        )
        self.seed_entry = tk.Entry(
            self.settings_btns_frame, **self.STYLE_ENTRY
        )
        self.seed_entry.insert(0, "" if self.seed is None else str(self.seed))

        ##############################
        ##### Placing components #####
        ##############################
        logging.info("Placing the settings' window components")

        self.info_lbl.grid(row=0, padx=10, pady=5, columnspan=4)

        ######################

        self.rules_lbl.grid       (row=1, column=0, padx=5, pady=5, columnspan=2)
        self.gui_settings_lbl.grid(row=1, column=2, padx=5, pady=5, columnspan=2)

        #######################
        
        self.neighborhood_lbl.grid       (row=2, column=0, padx=0, pady=5, sticky="e")
        self.neighborhoods_opts_list.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.cols_lbl.grid  (row=2, column=2, padx=5, pady=5, sticky="e")
        self.cols_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        #############################

        self.birth_lbl.grid  (row=3, column=0, padx=5, pady=5, sticky="e")
        self.birth_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.rows_lbl.grid  (row=3, column=2, padx=5, pady=5, sticky="e")
        self.rows_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        ######################

        self.survive_lbl.grid  (row=4, column=0, padx=5, pady=5, sticky="e")
        self.survive_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.cell_size_lbl.grid  (row=4, column=2, padx=5, pady=5, sticky="e")
        self.cell_size_entry.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        ##################

        self.rand_settings_lbl.grid(row=5, column=0, padx=5, pady=5, columnspan=2)

        self.rand_density_lbl.grid  (row=6, column=0, padx=5, pady=5, sticky="e")
        self.rand_density_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.seed_lbl.grid  (row=7, column=0, padx=5, pady=5, sticky="e")
        self.seed_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        ##############

        self.entry_error_lbl.grid(row=8, column=0, padx=10, pady=0, columnspan=4)

        self.save_settings_btn.grid(row=9, column=0, padx=10, pady=5, columnspan=4)
    
    def send_settings_back(self):
        """
        Collects and validates the settings, and sends them back via the callback.
        
        If the input values are valid, the settings window is closed and the
        callback is invoked with the new settings. Uses iteration and set
        comprehension to convert the birth and survive rulestrings into sets
        of integers.
        """
        birth_str = self.birth_entry.get()
        survive_str = self.survive_entry.get()
        try:
            neighborhood = self.neighborhoods_opts.get()
            birth = {int(char) for char in birth_str} 
            survive = {int(char) for char in survive_str} 
            cols = max(1, int(self.cols_entry.get()))
            rows = max(1, int(self.rows_entry.get()))
            cell_size = max(1, int(self.cell_size_entry.get()))
            density = float(self.rand_density_entry.get()) / 100.0
            # TODO move validation to the engine
            seed_input = self.seed_entry.get()
            if seed_input.isnumeric():
                seed = int(seed_input)
            else:
                seed = None if seed_input == '' else seed_input
        except ValueError:
            logging.error("Invalid input values, cannot save settings")
            return
        
        self.settings_window.destroy()
        self.callback(neighborhood, birth, survive, cols, rows, cell_size, density, seed)

    def validate_rulestring(self, rulestring: str) -> bool:
        """
        Validates the birth/survival rulestring input.
        
        The rulestring should consist of digits representing the number of
        neighbors required for birth/survival. The valid digits depend on the
        selected neighborhood type (0-8 or None for Moore, 0-4 or None for Von Neumann).
        If the rulestring is valid, the save button is enabled; otherwise,
        an error message is displayed. Uses iteration and set comprehension
        to check the validity of the rulestring.
        """
        rule = {int(char) for char in rulestring}
        neighbors = 8 if self.neighborhoods_opts.get() == "Moore" else 4
        if len(rule) <= neighbors + 1 and all(x <= neighbors for x in rule):
            return True
        self.entry_error_lbl.config(text="Invalid rulestring")
        self.root.after(2000, lambda: self.entry_error_lbl.config(text=""))
        return False
    
    def validate_dimensions(self, dimension: str) -> bool:
        """
        Validates the grid dimension and cell size inputs.
        
        The input should be a positive integer. If the input is valid, the save
        button is enabled; otherwise, the save button is disabled. An empty input
        is considered valid to allow clearing the entry, but it will disable the
        save button until a valid value is entered.
        """
        if dimension.isdigit():
            if int(dimension) > 0:
                self.save_settings_btn.config(state=tk.NORMAL, **self.STYLE_CLK_BTN)
                return True
        # Return true to allow clearing the entry but disable saving
        elif dimension == '':
            self.save_settings_btn.config(state=tk.DISABLED, **self.STYLE_GREYED_BTN)
            return True
        self.save_settings_btn.config(state=tk.DISABLED, **self.STYLE_GREYED_BTN)
        return False