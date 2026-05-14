import tkinter as tk
import logging

class SettingsWindow:

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
            birth: set, survive: set, on_save_callback: function
        ):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.neighborhoods = neighborhoods
        self.current_neighborhood = current_neighborhood
        self.birth = birth
        self.survive = survive
        self.cell_size = cell_size
        self.callback = on_save_callback

        ##### Creating the window
        self.settings_window = tk.Toplevel(self.root, bg=self.CLR_BG)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x200")
        self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.destroy)

        ##### Creating the buttons frame
        self.settings_btns_frame = tk.Frame(self.settings_window, bg=self.CLR_BG)
        self.settings_btns_frame.pack()

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
            self.settings_btns_frame, **self.STYLE_ENTRY
        )
        self.cols_entry.insert(0, str(self.cols))

        self.rows_lbl = tk.Label(
            self.settings_btns_frame, text="Rows",
            **self.STYLE_LABEL
        )
        self.rows_entry = tk.Entry(self.settings_btns_frame, **self.STYLE_ENTRY)
        self.rows_entry.insert(0, str(self.rows))

        self.cell_size_lbl = tk.Label(
            self.settings_btns_frame, text="Cell Size",
            **self.STYLE_LABEL
        )
        self.cell_size_entry = tk.Entry(self.settings_btns_frame, **self.STYLE_ENTRY)
        self.cell_size_entry.insert(0, str(self.cell_size))

        self.save_settings_btn = tk.Button(
            self.settings_btns_frame, text="Save", **self.STYLE_CLK_BTN,
            command=self.send_settings_back
        )
        self.settings_window.bind('<Return>', lambda event: self.save_settings_btn.invoke())

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

        self.save_settings_btn.grid(row=5, column=0, padx=10, pady=5, columnspan=4)
    
    def send_settings_back(self):
        birth_str = self.birth_entry.get()
        survive_str = self.survive_entry.get()
        try:
            neighborhood = self.neighborhoods_opts.get()
            birth = {int(char) for char in birth_str} 
            survive = {int(char) for char in survive_str} 
            cols = max(1, min(int(self.cols_entry.get()), 100))
            rows = max(1, min(int(self.rows_entry.get()), 100))
            cell_size = max(1, min(int(self.cell_size_entry.get()), 100))
        except ValueError:
            logging.error("The entered values are incorrect.")
            return
        
        self.settings_window.destroy()
        self.callback(neighborhood, birth, survive, cols, rows, cell_size)

    def validate_rulestring(self, rulestring: str) -> bool:
        rule = {int(char) for char in rulestring}
        neighbors = 8 if self.current_neighborhood == "Moore" else 4
        if len(rule) <= neighbors + 1 and all(x <= neighbors for x in rule):
            return True
        return False