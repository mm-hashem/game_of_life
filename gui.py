"""
GameOfLifeGUI class, which implements the graphical user interface for Conway's Game of Life using Tkinter.

The GameOfLifeGUI class provides a graphical interface to interact with the Game of Life,
simulation, including controls for starting/stopping, stepping, clearing, randomizing, selecting presets, adjusting speed, and settings.
The class manages the layout of the GUI components, handles user interactions, and updates the display based on the state of the game engine.
"""

import tkinter as tk
import logging
from engine import GameOfLife
from rle_manager import RLEManager
from settings_window import SettingsWindow

class GameOfLifeGUI:

    """A GUI for Conway's Game of Life using Tkinter.

    This class provides a graphical interface to interact with the Game of Life
    simulation, including controls for starting/stopping, stepping, clearing,
    randomizing, selecting presets, adjusting speed, and settings.

    Attributes:
        engine (GameOfLife): The game engine instance.
        rle_manager (RLEManager): Manager for RLE patterns.
        cell_size (int): Size of each cell in pixels.
        root (tk.Tk): The root Tkinter window.
        speed (int): Speed of the simulation.
        job_id: ID for the scheduled loop.
        running (bool): Whether the simulation is running.
        dragging (bool): Whether the user is dragging the canvas.
        slider_val_prev (int): Previous slider value.
        slider_var (tk.IntVar): Tkinter variable for the speed slider.
        ctrl_frame (tk.Frame): Frame for control buttons.
        start_btn (tk.Button): Start/Stop button.
        step_btn (tk.Button): Step button.
        clear_btn (tk.Button): Clear button.
        random_btn (tk.Button): Random button.
        speed_slider (tk.Scale): Speed slider.
        presets_opts (tk.StringVar): Variable for preset selection.
        preset_opts_list (tk.OptionMenu): Option menu for presets.
        open_settings_btn (tk.Button): Settings button.
        cell_buttons (list): 2D list of canvas rectangles for cells.
        cells_canvas (tk.Canvas): Canvas for drawing cells.
        stats_frame (tk.Frame): Frame for statistics.
        pop_stat_lbl (tk.Label): Population label.
        gen_stat_lbl (tk.Label): Generation label.
        density_stat_lbl (tk.Label): Density label.
        growth_rate_lbl (tk.Label): Growth rate label.
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
        "padx": 8,
        "font": ("Segoe UI", 11)
    }

    STYLE_CLK_BTN = {
        **STYLE_GREYED_BTN,
        "bg": CLR_CLK_BTN
    }

    STYLE_SLIDER = {
        "bg": CLR_BG,
        "fg": CLR_TEXT,
        "bg":CLR_BG,
        "highlightbackground": CLR_BG,
        "relief": "flat",
        "sliderrelief": "flat",
        "troughcolor": CLR_CLK_BTN
    }

    STYLE_LABEL = {
        "bg": CLR_CLK_BTN,
        "fg": CLR_TEXT,
        "highlightthickness": 2,
        "highlightbackground": CLR_BTN_BD
    }

    def __init__(
            self, root: tk.Tk, engine: GameOfLife, rle_manager: RLEManager
        ):
        """Initializes the GameOfLifeGUI.

        Args:
            root: The root Tkinter window.
            engine: The game engine instance.
            rle_manager: Manager for RLE patterns.
        """

        self.engine = engine
        self.rle_manager = rle_manager
        self.cell_size = 20
        self.root = root
        self.speed = 1

        self.root.geometry('850x700')
        self.root.title("Conway's Game of Life")

        # Game state        
        self.job_id   = None
        self.running  = False
        self.dragging = False

        self.slider_val_prev = 1
        self.slider_var = tk.IntVar(value=1)

        self.root.config(bg=self.CLR_BG)

        ########################
        ##### Control Area #####
        ########################

        self.ctrl_frame = tk.Frame(self.root, bg=self.CLR_BG)
        self.ctrl_frame.pack()

        self.start_btn = tk.Button(
            self.ctrl_frame, text="Start",
            **(self.STYLE_GREYED_BTN | {"padx": 15, "font": ("Segoe UI", 14)}),
            state=tk.DISABLED, command=self.start
        )

        self.step_btn = tk.Button(
            self.ctrl_frame, text="Step", **self.STYLE_GREYED_BTN,
            state=tk.DISABLED, command=self.step_gui
        )
        
        self.clear_btn = tk.Button(
            self.ctrl_frame, text="Clear", **self.STYLE_GREYED_BTN,
            state=tk.DISABLED, command=self.clear_gui
        )

        self.random_btn = tk.Button(
            self.ctrl_frame, text="Random", **self.STYLE_CLK_BTN,
            command=self.random
        )

        self.speed_slider = tk.Scale(
            self.ctrl_frame, **self.STYLE_SLIDER, orient="horizontal",
            from_=-10, to=10, label="1 gen/sec", variable=self.slider_var,
            resolution=1, showvalue=0, command=lambda _:self.speed_control()
        )
        self.speed_slider.set(1)

        self.presets_opts = tk.StringVar(value="Select pattern")
        self.preset_opts_list = tk.OptionMenu(
            self.ctrl_frame, self.presets_opts,
            *self.rle_manager.available_patterns,
            command=self.select_preset
        )
        self.preset_opts_list.config(**self.STYLE_CLK_BTN)
        self.preset_opts_list["menu"].config(
            bg=self.CLR_BG, fg=self.CLR_TEXT, bd=0, relief="flat"
        )

        self.open_settings_btn = tk.Button(
            self.ctrl_frame, text="Settings", **self.STYLE_CLK_BTN,
            command=self.open_settings_window
        )

        #################
        ##### Cells #####
        #################

        self.cell_buttons = None

        self.cells_canvas = tk.Canvas(
            self.root, bg=self.CLR_BG,
            highlightbackground=self.CLR_BG
        )
        self.cells_canvas.pack(fill="both", expand=True)

        self.cells_canvas.bind("<Button-1>", self.start_pan)
        self.cells_canvas.bind("<B1-Motion>", self.do_pan)
        self.cells_canvas.bind("<MouseWheel>", self.zoom)
 
        self.create_cells()

        ######################
        ##### Statistics #####
        ######################

        self.stats_frame = tk.Frame(self.root, bg=self.CLR_BG)
        self.stats_frame.pack()

        ##### Row 0
        self.pop_stat_lbl     = tk.Label(self.stats_frame, text="Population: 0",    **self.STYLE_LABEL)
        self.gen_stat_lbl     = tk.Label(self.stats_frame, text="Generation: 0",    **self.STYLE_LABEL)
        self.density_stat_lbl = tk.Label(self.stats_frame, text="Density: 0.0",     **self.STYLE_LABEL)
        self.growth_rate_lbl  = tk.Label(self.stats_frame, text="Growth Rate: 0.0", **self.STYLE_LABEL)

        ##############################
        ##### Placing components #####
        ##############################
        logging.info("Placing the main window's components")

        self.preset_opts_list.grid(row=0, column=0, padx=10, pady=5)
        self.random_btn.grid      (row=0, column=1, padx=10, pady=5)
        self.clear_btn.grid       (row=0, column=2, padx=10, pady=5)
        self.start_btn.grid       (row=0, column=3, padx=10, pady=5)
        self.step_btn.grid        (row=0, column=4, padx=10, pady=5)
        self.speed_slider.grid    (row=0, column=5, padx=10, pady=5)
        self.open_settings_btn.grid(row=0, column=7, padx=10, pady=5)

        self.pop_stat_lbl.grid    (row=0, column=0, padx=10, pady=10)
        self.gen_stat_lbl.grid    (row=0, column=1, padx=10, pady=10)
        self.density_stat_lbl.grid(row=0, column=2, padx=10, pady=10)
        self.growth_rate_lbl.grid (row=0, column=3, padx=10, pady=10)

    def open_settings_window(self) -> None:
        """Opens the settings window.

        This method creates and displays a new settings window for configuring
        the game parameters.
        """
        SettingsWindow(
            self.root, self.engine.rows, self.engine.cols, self.cell_size,
            list(self.engine.neighbor_coords), self.engine.neighborhood,
            self.engine.birth, self.engine.survive, self.engine.rand_density,
            self.engine.seed, self.apply_settings
        )

    def apply_settings(
            self, neighborhood: str, birth: set[int], survive: set[int],
            rows: int, cols: int, cell_size: int, density: float, seed: str | int | None
        ) -> None:
        """Applies the settings from the settings window.

        Args:
            neighborhood: The neighborhood type.
            birth: Set of birth rules.
            survive: Set of survival rules.
            rows: Number of rows in the grid.
            cols: Number of columns in the grid.
            cell_size: Size of each cell in pixels.
            density: Density for randomization.
            seed: Seed for randomization.
        """
        
        self.engine.change_rules(birth, survive, neighborhood)
        try:
            self.engine.set_rand_density(density)
        except ValueError as e:
            logging.error(f"Failed to set randomization density: {e}")
        self.engine.set_seed(seed, seed_set=True)
        self.cell_size = cell_size
        try:
            if (rows      != self.engine.rows or
                cols      != self.engine.cols or
                cell_size != self.cell_size):
                self.engine.change_dimensions(rows, cols)
                self.create_cells()
        except ValueError as e:
            logging.error(f"Failed to change grid dimensions: {e}")

    def center_canvas(self) -> None:
        """Centers the canvas in the window.

        This method adjusts the canvas view to center the grid within the
        available space.
        """
        self.cells_canvas.update_idletasks()
        bbox = self.cells_canvas.bbox("all")
        if not bbox:
            return

        cwidth = self.cells_canvas.winfo_width()
        cheight = self.cells_canvas.winfo_height()
        left, top, right, bottom = bbox

        grid_width = right - left
        grid_height = bottom - top

        if grid_width < cwidth:
            offset_x = (cwidth - grid_width) / 2 - left
        else:
            offset_x = 0

        if grid_height < cheight:
            offset_y = (cheight - grid_height) / 2 - top
        else:
            offset_y = 0

        if offset_x or offset_y:
            self.cells_canvas.move("all", offset_x, offset_y)

        self.cells_canvas.configure(scrollregion=self.cells_canvas.bbox("all"))

        if grid_width > cwidth:
            self.cells_canvas.xview_moveto((left + grid_width/2 - cwidth/2) / grid_width)
        if grid_height > cheight:
            self.cells_canvas.yview_moveto((top + grid_height/2 - cheight/2) / grid_height)

    def select_preset(self, selected_preset: str) -> None:
        """Selects and loads a preset pattern.

        Args:
            selected_preset (str): The name of the preset to load.
        """
        coords, birth, survive = self.rle_manager.get_configs(selected_preset)
        self.engine.load_preset(coords)
        self.engine.change_rules(birth, survive)
        self.refresh_gui()

    def create_cells(self) -> None:
        """Creates the cell grid on the canvas.

        This method draws rectangles for each cell in the grid and binds click
        events to them. Uses iteration to create the grid based on the current
        dimensions and cell size.
        """
        self.cells_canvas.delete("all")
        self.cell_buttons = [[None]*self.engine.cols for _ in range(self.engine.rows)]
                
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                x1 = c  * self.cell_size
                y1 = r  * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.cells_canvas.create_rectangle(x1, y1, x2, y2, fill=self.CLR_DEAD_CELL, outline="black")
                self.cell_buttons[r][c] = rect # TODO REMOVE AND PASS R AND C
                self.cells_canvas.tag_bind(
                    rect, "<ButtonRelease-1>", lambda event, r=r, c=c:
                    self.on_cell_click(r, c) if not self.is_dragging else None
                )

        self.cells_canvas.configure(scrollregion=self.cells_canvas.bbox("all"))
        self.root.after(100, self.center_canvas)
    
    def start(self) -> None:
        """Starts or stops the simulation.

        Toggles the running state and begins the game loop if starting.
        """
        logging.info("Starting the game")
        self.running = not self.running
        if self.running:
            self.loop()
        else: # TODO Delete?
            self.refresh_gui()
            self.stop_loop()

    def stop_loop(self) -> None:
        """Stops the game loop.

        Cancels any scheduled loop iterations and sets running to False.
        """
        if self.job_id:
            logging.info("Stopping the game")
            self.root.after_cancel(self.job_id)
            self.job_id = None
            self.running = False

    def loop(self) -> None:
        """Runs one iteration of the game loop.

        Advances the simulation by one step, checks for live cells, and schedules
        the next iteration.
        """
        logging.info("Game loop")

        if self.running:
            self.job_id = self.root.after(round(1000 * self.speed), self.loop)

        self.step_gui()
        
        if self.engine.population == 0:
            logging.info("No live cell")
            self.clear_gui()
        else:
            logging.info("There are live cells")
            self.refresh_gui()

    def on_cell_click(self, r: int, c: int) -> None:
        """Handles cell click events.

        Toggles the state of the clicked cell.

        Args:
            r (int): Row index of the cell.
            c (int): Column index of the cell.
        """
        logging.info(f"A cell was clicked, r: {r}, c: {c}")
        try:
            self.engine.toggle(r, c)
        except ValueError as e:
            logging.error(f"Failed to toggle cell state: {e}")
            return
        self.refresh_gui()

    def clear_gui(self) -> None:
        """Clears the grid and stops the simulation.

        Resets the engine state and refreshes the GUI.
        """
        logging.info("Clear buttons was clicked.")
        self.engine.clear()
        self.stop_loop()
        self.refresh_gui(True)

    def step_gui(self) -> None:
        """Advances the simulation by one step.

        Calls the engine's step method and refreshes the GUI.
        """
        logging.info("Step button was clicked.")
        self.engine.step()
        self.refresh_gui()

    def random(self) -> None:
        """Randomizes the grid state.

        Fills the grid with random live cells and refreshes the GUI.
        """
        self.engine.random()
        self.refresh_gui()

    ##### Generation Speed #####

    def speed_control(self) -> None:
        """Controls the simulation speed based on slider value.

        Adjusts the speed variable and reschedules the loop if running.
        """
        slider_val = self.slider_var.get()

        if self.slider_val_prev == 1 and slider_val in (-1, 0):
            self.speed_slider.set(-2)
        elif self.slider_val_prev == -2 and slider_val in (-1, 0):
            self.speed_slider.set(1)
        
        slider_val = self.slider_var.get()

        if   (slider_val  < 0): self.speed = abs(slider_val)
        elif (slider_val >= 1): self.speed = 1 / slider_val

        if self.job_id is not None and self.running:
            self.root.after_cancel(self.job_id)
            self.job_id = self.root.after(round(1000 * self.speed), self.loop)

        self.slider_val_prev = slider_val
        self.refresh_slider()

    ##### Cells Pan and Zoom #####

    def start_pan(self, event: tk.Event) -> None:
        """Starts panning the canvas.

        Args:
            event (tk.Event): The mouse event.
        """
        logging.info("Mouse left button was clicked")
        self.is_dragging = False
        self.cells_canvas.scan_mark(round(event.x), round(event.y))

    def do_pan(self, event: tk.Event) -> None:
        """Performs panning of the canvas.

        Args:
            event (tk.Event): The mouse event.
        """
        logging.info("Mouse left button pressed and moving")
        self.is_dragging = True
        self.cells_canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event: tk.Event) -> None:
        """Zooms the canvas in or out.

        Args:
            event (tk.Event): The mouse wheel event.
        """
        factor = 1.1 if event.delta > 0 else 0.9
        
        x = self.cells_canvas.canvasx(event.x)
        y = self.cells_canvas.canvasy(event.y)
        
        # Scale all items on the canvas
        self.cells_canvas.scale("all", x, y, factor, factor)
        
        # Update the scroll region
        self.cells_canvas.configure(scrollregion=self.cells_canvas.bbox("all"))

    ##### GUI Refresh #####

    def refresh_stats(self) -> None:
        """Refreshes the statistics labels.

        Updates the population, generation, density, and growth rate labels.
        """
        self.pop_stat_lbl.config    (text=f"Population: {self.engine.population}")
        self.gen_stat_lbl.config    (text=f"Generation: {self.engine.gen}")
        self.density_stat_lbl.config(text=f"Density: {round(self.engine.density, 2)}")
        self.growth_rate_lbl.config (text=f"Growth Rate: {round(self.engine.growth_rate, 2)}")

    def refresh_cells(self) -> None: # TODO optimize
        """Refreshes the cell colors on the canvas.

        Updates the fill color of each cell rectangle based on its state.
        Uses iteration to check the state of each cell and apply the appropriate color.
        """
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                color = self.CLR_ALIVE_CELL if self.engine.get_cell_state(r, c) else self.CLR_DEAD_CELL
                self.cells_canvas.itemconfig(self.cell_buttons[r][c], fill=color)

    def refresh_slider(self) -> None:
        """Refreshes the speed slider label.

        Updates the label to show the current speed setting.
        """
        if self.slider_var.get() >= 1:
            self.speed_slider.config(label=f"{self.slider_var.get()} gen/sec")
        else:
            self.speed_slider.config(label=f"{abs(self.slider_var.get())} sec/gen")

    def refresh_buttons(self, clear: bool) -> None:
        """Refreshes the state of control buttons.

        Args:
            clear (bool): Whether to reset the preset selection.
        """
        next_text = "Stop" if self.running else "Start"
        self.start_btn.config(text=next_text)

        if self.engine.population > 0:
            self.start_btn.config(bg=self.CLR_CLK_BTN, state=tk.NORMAL)
            self.clear_btn.config(bg=self.CLR_CLK_BTN, state=tk.NORMAL)
            self.step_btn.config (bg=self.CLR_CLK_BTN, state=tk.NORMAL)
        else:
            if not self.running:
                self.start_btn.config(bg=self.CLR_GREYED_BTN, state=tk.DISABLED)
            self.clear_btn.config(bg=self.CLR_GREYED_BTN, state=tk.DISABLED)
            self.step_btn.config (bg=self.CLR_GREYED_BTN, state=tk.DISABLED)

        if clear: self.presets_opts.set("Select pattern")

    def refresh_gui(self, clear: bool = False) -> None:
        """Refreshes the entire GUI.

        Calls all refresh methods.

        Args:
            clear (bool, optional): Whether to clear the preset selection. Defaults to False.
        """
        logging.info("Refreshing the GUI")
        #logging.debug(f"Running: {self.running}")

        self.refresh_buttons(clear)
        self.refresh_slider()
        self.refresh_cells()
        self.refresh_stats()