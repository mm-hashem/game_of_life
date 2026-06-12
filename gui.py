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
from PIL import Image, ImageTk
import numpy as np

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
    CLR_BG          = "#112736"

    CLR_DEAD_CELL   = "#8d8d8d"       # Hex
    color_for_zeros = [141, 141, 141] # RGB

    CLR_ALIVE_CELL  = "#ffff00"     # Hex
    color_for_ones  = [255, 255, 0] # RGB

    CLR_CELL_BORDER = ""
    CLR_CLK_BTN     = "#456882" # Clickable button color
    CLR_GREYED_BTN  = "#D2C1B6" # Greyed-out button color
    CLR_BTN_BD      = "#234C6A" # Button border
    CLR_TEXT        = "#ffffff" # Text color

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
            self, root: tk.Tk, engine: GameOfLife, rle_manager: RLEManager,
            cell_size: int = 10
        ):
        """Initializes the GameOfLifeGUI.

        Args:
            root: The root Tkinter window.
            engine: The game engine instance.
            rle_manager: Manager for RLE patterns.
        """

        self.engine = engine
        self.rle_manager = rle_manager
        self.cell_size = cell_size
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

        # Image handling
        self.tk_img = None
        self.canvas_img_id = None
        self.palette = np.array([self.color_for_zeros, self.color_for_ones], dtype=np.uint8)
        self._initial_center_done = False

        ########################
        ##### Control Area #####
        ########################

        self.ctrl_frame = tk.Frame(self.root, bg=self.CLR_BG)
        self.ctrl_frame.pack()

        ##### Rewind Button

        self.rewind_btn = tk.Button(
            self.ctrl_frame, text="Rewind", **self.STYLE_GREYED_BTN,
            state=tk.DISABLED, command=self.rewind
        )

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

        self.cells_canvas.bind("<Button-1>",        self.start_pan)
        self.cells_canvas.bind("<ButtonRelease-1>", self.on_cell_click)
        self.cells_canvas.bind("<B1-Motion>",       self.do_pan)
        self.cells_canvas.bind("<MouseWheel>",      self.zoom)

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

        self.preset_opts_list.grid (row=0, column=0, padx=10, pady=5)
        self.random_btn.grid       (row=0, column=1, padx=10, pady=5)
        self.rewind_btn.grid       (row=0, column=2, padx=10, pady=5)
        self.clear_btn.grid        (row=0, column=3, padx=10, pady=5)
        self.start_btn.grid        (row=0, column=4, padx=10, pady=5)
        self.step_btn.grid         (row=0, column=5, padx=10, pady=5)
        self.speed_slider.grid     (row=0, column=6, padx=10, pady=5)
        self.open_settings_btn.grid(row=0, column=7, padx=10, pady=5)

        self.pop_stat_lbl.grid    (row=0, column=0, padx=10, pady=10)
        self.gen_stat_lbl.grid    (row=0, column=1, padx=10, pady=10)
        self.density_stat_lbl.grid(row=0, column=2, padx=10, pady=10)
        self.growth_rate_lbl.grid (row=0, column=3, padx=10, pady=10)

        self.root.after_idle(self._initial_render)
        self.cells_canvas.bind("<Configure>", self._on_canvas_configure)
        
    def _initial_render(self) -> None:
        """Performs the initial rendering of the GUI.

        This method is called after the main loop starts to ensure that the canvas
        has been properly initialized before drawing the cells.
        """

        _, _, view_w, view_h = self._get_viewport(0)

        # If canvas not yet laid out, try again shortly
        if view_w <= 1 or view_h <= 1:
            self.root.after(50, self._initial_render)
            return

        if not self._initial_center_done and not self.dragging:
            self.center_canvas()
            self.draw_cells()
            self._initial_center_done = True

    def _on_canvas_configure(self, event) -> None:
        # Don't interfere while the user is actively panning
        if self.dragging:
            return

        grid_w, grid_h = self._get_visual_grid_size()
        if grid_w <= event.width and grid_h <= event.height:
            self.center_canvas()
            self.draw_cells()

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
            self, neighborhood: str, birth_str: str, survive_str: str,
            rows: str, cols: str, cell_size: str, density: str, seed: str | int | None
        ) -> None:
        """Applies the settings from the settings window.

        Args:
            neighborhood: The neighborhood type.
            birth_str: String of birth rules.
            survive_str: String of survival rules.
            rows: Number of rows in the grid.
            cols: Number of columns in the grid.
            cell_size: Size of each cell in pixels.
            density: Density for randomization.
            seed: Seed for randomization.
        """
        # Process settings
        try:
            birth   = {int(char) for char in birth_str} 
            survive = {int(char) for char in survive_str}
            rows = int(rows)
            cols = int(cols)
            cell_size = int(cell_size)
            density = float(density) / 100.0
            if seed.isnumeric():
                seed = int(seed)
            else:
                seed = None if seed == '' else seed
        except ValueError as e:
            logging.error(f"Invalid settings input: {e}")
            # TODO - show error message to user instead of just logging
            return

        try:
            self.engine.set_rand_density(density)
        except ValueError as e:
            logging.error(f"Failed to set randomization density: {e}")
            
        self.engine.change_rules(birth, survive, neighborhood)
        self.engine.set_seed(seed, seed_set=True)
        self.cell_size = cell_size
        try:
            if (rows      != self.engine.rows or
                cols      != self.engine.cols or
                cell_size != self.cell_size):
                self.engine.change_dimensions(rows, cols)
                self.draw_cells()
        except ValueError as e:
            logging.error(f"Failed to change grid dimensions: {e}")

    def center_canvas(self) -> None:
        """Centers the canvas in the window.

        This method adjusts the canvas view to center the visual grid within the
        available space.
        """

        _, _, view_w, view_h = self._get_viewport(0)
        grid_w, grid_h       = self._get_visual_grid_size()
        total_w, total_h     = self._sync_scrollregion(view_w, view_h, grid_w, grid_h)

        if grid_w > view_w:
            left = (grid_w - view_w) / 2
            self.cells_canvas.xview_moveto(left / total_w)
        else:
            self.cells_canvas.xview_moveto(0)

        if grid_h > view_h:
            top = (grid_h - view_h) / 2
            self.cells_canvas.yview_moveto(top / total_h)
        else:
            self.cells_canvas.yview_moveto(0)

    def select_preset(self, selected_preset: str) -> None:
        """Selects and loads a preset pattern.

        Args:
            selected_preset (str): The name of the preset to load.
        """
        try:
            coords, birth, survive = self.rle_manager.get_configs(selected_preset)
        except ValueError as e:
            logging.error(f"Failed to load preset: {e}")
            return

        self.engine.load_preset(coords)
        self.engine.change_rules(birth, survive)
        self.refresh_gui()

    def draw_cells(self) -> None:
        """Draws the cells on the canvas.

        This method calculates the visible portion of the visual grid, colorizes it,
        and renders it on the canvas. It also handles centering for small visual grids
        and keeps the scroll region in sync with the grid size.
        """
        # Get the current visible pixel coordinates of the canvas viewport
        x_canvas, y_canvas, view_w, view_h = self._get_viewport(0)
        grid_w, grid_h = self._get_visual_grid_size()
        
        # Fallback
        if view_w <= 1: view_w = grid_w
        if view_h <= 1: view_h = grid_h

        # Sync scrollregion
        self._sync_scrollregion(view_w, view_h, grid_w, grid_h)

        # Map pixel coordinates to NumPy grid indices
        start_col = max(0, int(x_canvas // self.cell_size))
        end_col   = min(self.engine.cols, int((x_canvas + view_w) // self.cell_size) + 1)
        
        start_row = max(0, int(y_canvas // self.cell_size))
        end_row   = min(self.engine.rows, int((y_canvas + view_h) // self.cell_size) + 1)
        
        # Slice the array
        visible_grid = self.engine.grid[start_row:end_row, start_col:end_col]

        # Colorize the visible grid
        img_array = self.palette[visible_grid.astype(np.uint8)]
        img = Image.fromarray(img_array, mode='RGB')

        # Resize the visible portion
        target_w = (end_col - start_col) * self.cell_size
        target_h = (end_row - start_row) * self.cell_size
        
        img = img.resize((int(target_w), int(target_h)), resample=Image.NEAREST)
        self.tk_img = ImageTk.PhotoImage(img)

        # Compute centering offset for small grids
        offset_x, offset_y = self._get_visual_grid_offsets(view_w, view_h, grid_w, grid_h)

        # Calculate where this cropped image belongs
        img_x = offset_x + start_col * self.cell_size
        img_y = offset_y + start_row * self.cell_size

        # Update image and shift its coordinates to match the scroll position
        if self.canvas_img_id is None:
            self.canvas_img_id = self.cells_canvas.create_image(img_x, img_y, image=self.tk_img, anchor="nw")
        else:
            self.cells_canvas.itemconfig(self.canvas_img_id, image=self.tk_img)
            self.cells_canvas.coords(self.canvas_img_id, img_x, img_y)

    def rewind(self) -> None:
        """Rewinds the simulation to the previously saved state.

        This method restores the grid to the last saved state and refreshes the GUI.
        """
        self.clear_gui()
        self.engine.create_grid(fromsaved=True)
        self.refresh_gui()

    def start(self) -> None:
        """Starts or stops the simulation.

        Toggles the running state and begins the game loop if starting.
        """
        logging.info("Starting the game")
        
        if not self.running:
            self.engine.save_grid()

        self.running = not self.running
        if self.running:
            self.loop()
        else:
            self.stop_loop()
            self.refresh_gui()

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

        self.engine.step()
        
        if self.engine.population == 0:
            logging.info("No live cell")
            self.stop_loop()
            self.refresh_gui()
        else:
            logging.info("There are live cells")
            self.refresh_gui()

    def on_cell_click(self, event: tk.Event) -> None:
        """Handles cell click events.

        Toggles the state of the clicked cell.

        Args:
            event (tk.Event): The mouse event.
        """
        if self.dragging:
            logging.info("Mouse released after dragging, not toggling cell")
            #self.dragging = False
            return
        
        x_canvas, y_canvas, view_w, view_h = self._get_viewport(event)
        grid_w,   grid_h   = self._get_visual_grid_size()
        offset_x, offset_y = self._get_visual_grid_offsets(view_w, view_h, grid_w, grid_h)

        c = int((x_canvas - offset_x) // self.cell_size)
        r = int((y_canvas - offset_y) // self.cell_size)

        if r < 0 or r >= self.engine.rows or c < 0 or c >= self.engine.cols:
            logging.warning(f"Clicked outside of the visual grid bounds, r: {r}, c: {c}")
            return

        logging.info(f"A cell was clicked, r: {r}, c: {c}")

        self.engine.toggle(r, c)

        self.refresh_gui()

    def clear_gui(self) -> None:
        """Clears the grid and stops the simulation.

        Resets the engine state and refreshes the GUI.
        """
        logging.info("Clear buttons was clicked.")
        self.engine.clear()
        self.stop_loop()
        self.refresh_gui(clear_optmenu=True)

    def step_gui(self) -> None:
        """Advances the simulation by one step.

        This method is called when the user clicks the "Step" button to advance
        the simulation by a single generation.
        """
        logging.info("Step button was clicked.")
        self.engine.step()
        self.refresh_gui()

    def random(self) -> None:
        """Randomizes the grid state.

        Fills the grid with random live cells and refreshes the GUI.
        """
        self.clear_gui()
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
        self.dragging = False
        self.cells_canvas.scan_mark(round(event.x), round(event.y))

    def do_pan(self, event: tk.Event) -> None:
        """Performs panning of the canvas.

        Args:
            event (tk.Event): The mouse event.
        """
        logging.info("Mouse left button pressed and moving")
        self.dragging = True
        self.cells_canvas.scan_dragto(event.x, event.y, gain=1)
        self.draw_cells()

    def zoom(self, event: tk.Event) -> None:
        """Zooms the canvas in or out.

        Args:
            event (tk.Event): The mouse wheel event.
        """
        if hasattr(event, "delta"):
            direction = 1 if event.delta > 0 else -1
        else:
            direction = 1 if event.num == 4 else -1 if event.num == 5 else 0
        if direction == 0:
            return

        old_cell = max(1, int(self.cell_size))
        factor   = 1.1 if direction > 0 else 0.9

        # Get the current view metrics before zooming
        x_canvas,     y_canvas, view_w, view_h = self._get_viewport(event)
        old_grid_w,   old_grid_h   = self._get_visual_grid_size()
        offset_x_old, offset_y_old = self._get_visual_grid_offsets(view_w, view_h, old_grid_w, old_grid_h)

        # Relative position inside the visual grid
        rel_x = (x_canvas - offset_x_old) / old_cell
        rel_y = (y_canvas - offset_y_old) / old_cell

        # Compute new cell size (clamp >= 1)
        new_cell = max(1, int(round(old_cell * factor)))

        # If rounding doesn't change size, step by 1
        if new_cell == old_cell:
            new_cell = max(1, old_cell + (1 if direction > 0 else -1))

        self.cell_size = new_cell

        # Update canvas scrollregion to the new visual grid size
        new_grid_w,   new_grid_h   = self._get_visual_grid_size()
        total_w,      total_h      = self._sync_scrollregion(view_w, view_h, new_grid_w, new_grid_h)
        offset_x_new, offset_y_new = self._get_visual_grid_offsets (view_w, view_h, new_grid_w, new_grid_h)

        new_x_canvas = offset_x_new + rel_x * new_cell
        new_y_canvas = offset_y_new + rel_y * new_cell

        new_x_left = new_x_canvas - event.x
        new_y_top  = new_y_canvas - event.y

        frac_x = 0.0 if total_w == 0 else new_x_left / total_w
        frac_y = 0.0 if total_h == 0 else new_y_top  / total_h
        frac_x = max(0.0, min(1.0, frac_x))
        frac_y = max(0.0, min(1.0, frac_y))

        self.cells_canvas.xview_moveto(frac_x)
        self.cells_canvas.yview_moveto(frac_y)

        # Redraw the image at the new scale
        self.draw_cells()

    ##### GUI Refresh #####

    def refresh_stats(self) -> None:
        """Refreshes the statistics labels.

        Updates the population, generation, density, and growth rate labels.
        """
        self.pop_stat_lbl.config    (text=f"Population: {self.engine.population}")
        self.gen_stat_lbl.config    (text=f"Generation: {self.engine.gen}")
        self.density_stat_lbl.config(text=f"Density: {round(self.engine.density, 2)}")
        self.growth_rate_lbl.config (text=f"Growth Rate: {round(self.engine.growth_rate, 2)}")

    def refresh_slider(self) -> None:
        """Refreshes the speed slider label.

        Updates the label to show the current speed setting.
        """
        if self.slider_var.get() >= 1:
            self.speed_slider.config(label=f"{self.slider_var.get()} gen/sec")
        else:
            self.speed_slider.config(label=f"{abs(self.slider_var.get())} sec/gen")

    def refresh_buttons(self, clear_optmenu: bool) -> None:
        """Refreshes the state of control buttons.

        Args:
            clear_optmenu: Whether to reset the preset selection.
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

        if self.engine.is_grid_saved():
            self.rewind_btn.config(bg=self.CLR_CLK_BTN, state=tk.NORMAL)
        else:
            self.rewind_btn.config(bg=self.CLR_GREYED_BTN, state=tk.DISABLED)

        if clear_optmenu: self.presets_opts.set("Select pattern")

    def refresh_gui(self, clear_optmenu: bool = False) -> None:
        """Refreshes the entire GUI.

        Calls all refresh methods.

        Args:
            clear_optmenu (optional): Whether to clear the preset selection. Defaults to False.
        """
        logging.info("Refreshing the GUI")

        self.refresh_buttons(clear_optmenu=clear_optmenu)
        self.refresh_slider()
        self.draw_cells()
        self.refresh_stats()

    def _get_viewport(self, event: tk.Event | int = 0) -> tuple[float, float, float, float]:
        """Calculates viewport metrics for the canvas.

        Args:
            event: The mouse event to calculate the viewport for.
                   If 0, uses the top-left corner of the canvas.

        Returns:
            A tuple containing the left, top, width, and height of the visible
            area in canvas coordinates.
        """
        self.cells_canvas.update_idletasks()

        if event != 0:
            x_canvas = self.cells_canvas.canvasx(event.x)
            y_canvas = self.cells_canvas.canvasy(event.y)
        else:
            x_canvas = self.cells_canvas.canvasx(0)
            y_canvas = self.cells_canvas.canvasy(0)

        view_w = max(1, self.cells_canvas.winfo_width())
        view_h = max(1, self.cells_canvas.winfo_height())

        return x_canvas, y_canvas, view_w, view_h
    
    def _get_visual_grid_size(self) -> tuple[float, float]:
        """Calculates the pixel size of the entire visual grid.

        Returns:
            A tuple containing the width and height of the visual grid in pixels.
        """
        cell_size = max(1, self.cell_size)

        grid_w = self.engine.cols * cell_size
        grid_h = self.engine.rows * cell_size

        return grid_w, grid_h
    
    @staticmethod
    def _get_visual_grid_offsets(view_w, view_h, grid_w, grid_h) -> tuple[float, float]:
        """Calculates centering offsets for the visual grid.

        Args:
            view_w: The width of the visible area.
            view_h: The height of the visible area.
            grid_w: The width of the visual grid.
            grid_h: The height of the visual grid.
        
        Returns:
            A tuple containing the x and y offsets to center the visual grid within the visible area.
        """
        offset_x = max(0, (view_w - grid_w) // 2)
        offset_y = max(0, (view_h - grid_h) // 2)

        return offset_x, offset_y
    
    def _sync_scrollregion(self, view_w, view_h, grid_w, grid_h) -> tuple[float, float]:
        """Synchronizes the canvas scrollregion with the visual grid size.

        Args:
            view_w: The width of the visible area.
            view_h: The height of the visible area.
            grid_w: The width of the visual grid.
            grid_h: The height of the visual grid.

        Returns:
            A tuple containing the total width and height of the scrollregion.
        """
        total_w = max(grid_w, view_w)
        total_h = max(grid_h, view_h)

        self.cells_canvas.configure(scrollregion=(0, 0, total_w, total_h))

        return total_w, total_h

