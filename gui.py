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
from styles import Styles
from views.settings_window import SettingsWindow
from views.control_panel import ControlPanel
from views.grid_view import GridView

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
        ctrl_frame (tk.Frame): Frame for control buttons.
        grid_canvas (tk.Canvas): Canvas for drawing the grid.
        stats_frame (tk.Frame): Frame for statistics.
        pop_stat_lbl (tk.Label): Population label.
        gen_stat_lbl (tk.Label): Generation label.
        density_stat_lbl (tk.Label): Density label.
        growth_rate_lbl (tk.Label): Growth rate label.
    """

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
        self.root = root
        self.speed = 1

        self.root.geometry('850x700')
        self.root.title("Conway's Game of Life")

        # Game state        
        self.job_id   = None
        self.running  = False

        ##### Styles #####
        self.styles = Styles(size="medium", show_label_border=True, label_background="light")

        self.root.config(bg=self.styles.CLR_BG)

        ########################
        ##### Control Area #####
        ########################

        self.ctrl_frame = tk.Frame(self.root, bg=self.styles.CLR_BG)
        self.ctrl_frame.pack()

        self.control_panel = ControlPanel(
            self.ctrl_frame, available_patterns=self.rle_manager.available_patterns,
            on_random=self.random,
            on_rewind=self.rewind,
            on_clear=self.clear_gui,
            on_start=self.start,
            on_step=self.step_gui,
            on_open_settings=self.open_settings_window,
            on_preset_select=self.select_preset,
            on_speed_change=self.speed_control
        )

        #################
        ##### Cells #####
        #################

        self.grid_canvas = tk.Canvas(
            self.root, bg=self.styles.CLR_BG,
            highlightbackground=self.styles.CLR_BG
        )
        self.grid_canvas.pack(fill="both", expand=True)

        self.grid_view = GridView(
            self.grid_canvas,
            cell_size=cell_size,
            rows=self.engine.rows,
            cols=self.engine.cols,
            get_sliced_grid=self.engine.get_sliced_grid,
            toggle_cell=self.engine.toggle,
            refresh_gui=self.refresh_gui
        )

        ######################
        ##### Statistics #####
        ######################

        self.stats_frame = tk.Frame(self.root, bg=self.styles.CLR_BG)
        self.stats_frame.pack()

        ##### Row 0
        self.pop_stat_lbl     = tk.Label(self.stats_frame, text="Population: 0",    **self.styles.STYLE_LABEL)
        self.gen_stat_lbl     = tk.Label(self.stats_frame, text="Generation: 0",    **self.styles.STYLE_LABEL)
        self.density_stat_lbl = tk.Label(self.stats_frame, text="Density: 0.0",     **self.styles.STYLE_LABEL)
        self.growth_rate_lbl  = tk.Label(self.stats_frame, text="Growth Rate: 0.0", **self.styles.STYLE_LABEL)

        ##############################
        ##### Placing components #####
        ##############################
        logging.info("Placing the main window's components")

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
            self.root, self.engine.rows, self.engine.cols, self.grid_view.cell_size,
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

        if cell_size != self.grid_view.cell_size:
            self.grid_view.cell_size = cell_size
            self.grid_view.refresh()

        try:
            if (rows != self.engine.rows or
                cols != self.engine.cols):
                self.engine.change_dimensions(rows, cols)
                self.grid_view.rows = rows
                self.grid_view.cols = cols
                self.grid_view.refresh()
        except ValueError as e:
            logging.error(f"Failed to change grid dimensions: {e}")

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

    def speed_control(self, slider_val: int) -> None:
        """Controls the simulation speed based on slider value.

        Adjusts the speed variable and reschedules the loop if running.
        """

        if   (slider_val  < 0): self.speed = abs(slider_val)
        elif (slider_val >= 1): self.speed = 1 / slider_val

        if self.job_id is not None and self.running:
            self.root.after_cancel(self.job_id)
            self.job_id = self.root.after(round(1000 * self.speed), self.loop)

    ##### GUI Refresh #####

    def refresh_stats(self) -> None:
        """Refreshes the statistics labels.

        Updates the population, generation, density, and growth rate labels.
        """
        self.pop_stat_lbl.config    (text=f"Population: {self.engine.population}")
        self.gen_stat_lbl.config    (text=f"Generation: {self.engine.gen}")
        self.density_stat_lbl.config(text=f"Density: {round(self.engine.density, 2)}")
        self.growth_rate_lbl.config (text=f"Growth Rate: {round(self.engine.growth_rate, 2)}")

    def refresh_gui(self, clear_optmenu: bool = False) -> None:
        """Refreshes the entire GUI.

        Calls all refresh methods.

        Args:
            clear_optmenu (optional): Whether to clear the preset selection. Defaults to False.
        """
        logging.info("Refreshing the GUI")

        self.control_panel.refresh(
            clear_optmenu=clear_optmenu,
            is_running=self.running,
            has_population=self.engine.population >= 1,
            is_grid_saved=self.engine.is_grid_saved()
        )
        self.grid_view.refresh()
        self.refresh_stats()