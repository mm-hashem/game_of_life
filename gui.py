import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab
import logging
from engine import GameOfLife
from rle_manager import RLEManager

class GameOfLifeGUI:

    # Color codes
    #DEAD_CELL_CLR  = "#7e7e7e"
    #ALIVE_CELL_CLR = "#ffff00"
    BORDER_CLR     = "#999999"
    #CLR_CLK_BTN    = "#2F2FE4"

    # Color palette
    CLR_BG = "#112736"
    CLR_DEAD_CELL = "#A3A3A1"
    CLR_ALIVE_CELL = "#ffff00"
    CLR_CELL_BORDER = ""
    CLR_CLK_BTN = "#456882"
    CLR_GREYED_BTN = "#D2C1B6"
    #font_bold      = font.Font(family="Arial", size=14, weight="bold")

    def __init__(
            self, root: tk.Tk, engine: GameOfLife, rle_manager: RLEManager,
            cell_size: int = 23, speed: int = 1
        ):
        self.engine = engine
        self.rle_manager = rle_manager
        self.cell_size = cell_size
        self.root = root
        self.speed = speed
        self.frames = []

        self.root.geometry('650x700')
        self.root.title("Conway's Game of Life")

        # Game state        
        self.job_id   = None
        self.running  = False
        self.dragging = False

        self.slider_var = tk.IntVar(value=1)

        self.root.config(bg=self.CLR_BG)

        ########################
        ##### Control Area #####
        ########################

        self.ctrl_frame = tk.Frame(self.root, bg=self.CLR_BG)
        self.ctrl_frame.pack()

        self.start_btn = tk.Button(
            self.ctrl_frame, text="Start", bg=self.CLR_GREYED_BTN, fg="#ffffff",
            borderwidth=0, highlightthickness=0, relief="flat", state=tk.DISABLED,
            command=self.start,
            font=("Segoe UI", 13), padx=3, pady=3
        )

        self.step_btn = tk.Button(
            self.ctrl_frame, text="Step", bg=self.CLR_GREYED_BTN, fg="#ffffff",
            borderwidth=0, highlightthickness=0, relief="flat", state=tk.DISABLED,
            command=self.step_gui,
            padx=10, pady=5
        )
        
        self.clear_btn = tk.Button(
            self.ctrl_frame, text="Clear", bg=self.CLR_GREYED_BTN, fg="#ffffff",
            borderwidth=0, highlightthickness=0, relief="flat", state=tk.DISABLED,
            command=self.clear_gui,
            padx=10, pady=5
        )

        self.random_btn = tk.Button(
            self.ctrl_frame, text="Random", bg=self.CLR_CLK_BTN, fg="#ffffff",
            borderwidth=0, highlightthickness=0, relief="flat",
            command=self.random,
            padx=10, pady=5
        )

        self.speed_slider = tk.Scale(
            self.ctrl_frame, from_=-10, to=10, orient="horizontal", label="1 gen/sec",
            variable=self.slider_var, showvalue=0, command=self.speed_control,
            background=self.CLR_BG, highlightbackground=self.CLR_BG, fg="#ffffff",
            relief="flat", sliderrelief="flat", troughcolor=self.CLR_CLK_BTN
        )
        self.speed_slider.set(1)

        self.presets_opts = tk.StringVar(value="Select preset")
        self.preset_opts_list = tk.OptionMenu(self.ctrl_frame, self.presets_opts, *self.rle_manager.available_patterns, command=self.select_preset)

        self.export_gif_btn = tk.Button(
            self.ctrl_frame, text="Export GIF", bg=self.CLR_CLK_BTN, fg="#ffffff",
            borderwidth=0, highlightthickness=0, relief="flat",
            command=self.save_recording,
            padx=10, pady=5
        )        

        #################
        ##### Cells #####
        #################

        self.cell_buttons = [[None]*self.engine.cols for _ in range(self.engine.rows)]

        self.cells_canvas = tk.Canvas(
            self.root,
            background=self.CLR_BG,
            highlightbackground=self.CLR_BG,
        )
        self.cells_canvas.pack(fill="both", expand=True)

        self.cells_canvas.bind("<Button-1>", self.start_pan)
        self.cells_canvas.bind("<B1-Motion>", self.do_pan)
        self.cells_canvas.bind("<MouseWheel>", self.zoom)
 
        self.create_cells()
        self.root.after(100, self.center_canvas)

        ######################
        ##### Statistics #####
        ######################

        self.stats_frame = tk.Frame(self.root, bg="#080616")
        self.stats_frame.pack()

        ##### Row 0
        self.pop_stat_lbl = tk.Label(self.stats_frame, text="Population: 0")
        self.gen_stat_lbl = tk.Label(self.stats_frame, text="Generation: 0")
        self.density_stat_lbl = tk.Label(self.stats_frame, text="Density: 0.0")
        self.growth_rate_lbl = tk.Label(self.stats_frame, text="Growth Rate: 0.0")

        self.config_btns()

    def center_canvas(self) -> None:
        bbox = self.cells_canvas.bbox('all')
        if not bbox: return # Exit if canvas is empty

        # Get canvas viewport size
        cwidth = self.cells_canvas.winfo_width()
        cheight = self.cells_canvas.winfo_height()

        # Get the total scrollable dimensions from the bbox
        scroll_left, scroll_top, scroll_right, scroll_bottom = bbox
        scroll_width = scroll_right - scroll_left
        scroll_height = scroll_bottom - scroll_top

        # Calculate the center point of your content
        center_x = (scroll_left + scroll_right) / 2
        center_y = (scroll_top + scroll_bottom) / 2

        # Calculate the top-left position
        target_left = center_x - (cwidth / 2)
        target_top = center_y - (cheight / 2)

        # Convert to fractions (0.0 to 1.0) based on the scrollregion
        fraction_x = max(0, min(1, (target_left - scroll_left) / scroll_width))
        fraction_y = max(0, min(1, (target_top - scroll_top) / scroll_height))

        # Move the view
        self.cells_canvas.xview_moveto(fraction_x)
        self.cells_canvas.yview_moveto(fraction_y)

    def select_preset(self, selected_preset: str) -> None:
        coords = self.rle_manager.get_pattern_coords(selected_preset)
        self.engine.load_preset(coords)
        self.refresh_gui()

    def config_btns(self) -> None:
        logging.info("Configuring control buttons")

        self.start_btn.grid       (row=0, column=0, padx=10, pady=5)
        self.step_btn.grid        (row=0, column=1, padx=10, pady=5)
        self.clear_btn.grid       (row=0, column=2, padx=10, pady=5)
        self.random_btn.grid      (row=0, column=3, padx=10, pady=5)
        self.speed_slider.grid    (row=0, column=4, padx=10, pady=5)
        self.preset_opts_list.grid(row=0, column=5, padx=10, pady=5)
        self.export_gif_btn.grid  (row=0, column=6, padx=10, pady=5)

        self.pop_stat_lbl.grid    (row=0, column=0, padx=10, pady=10)
        self.gen_stat_lbl.grid    (row=0, column=1, padx=10, pady=10)
        self.density_stat_lbl.grid(row=0, column=2, padx=10, pady=10)
        self.growth_rate_lbl.grid (row=0, column=3, padx=10, pady=10)

    def create_cells(self) -> None:
        #self.cells_canvas.delete("all")
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                x1, y1 = c *  self.cell_size, r *  self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                rect = self.cells_canvas.create_rectangle(x1, y1, x2, y2, fill=self.CLR_DEAD_CELL, outline="black")
                self.cell_buttons[r][c] = rect # TODO REMOVE AND PASS R AND C
                self.cells_canvas.tag_bind(
                    rect, "<ButtonRelease-1>", lambda event, r=r, c=c:
                    self.on_cell_click(r, c) if not self.is_dragging else None
                )
        self.cells_canvas.configure(scrollregion=self.cells_canvas.bbox("all"))
    
    def start(self) -> None:
        logging.info("Starting the game")
        self.running = not self.running
        if self.running:
            self.loop()
        else: # TODO Delete?
            self.refresh_gui()
            self.stop_loop()

    def stop_loop(self) -> None:
        if self.job_id:
            logging.info("Stopping the game")
            self.root.after_cancel(self.job_id)
            self.job_id = None
            self.running = False

    def loop(self) -> None:
        logging.info("Game loop")
        self.step_gui()
        self.job_id = self.root.after(round(1000 * self.speed), self.loop)
        if not self.engine.has_live_cells():
            logging.info("No live cell")
            self.clear_gui()
        else:
            logging.info("There are live cells")

    def on_cell_click(self, r: int, c: int) -> None:
        logging.info(f"A cell was clicked, r: {r}, c: {c}")
        self.engine.toggle(r, c)
        self.refresh_gui()

    def clear_gui(self) -> None:
        logging.info("Clear buttons was clicked.")
        self.engine.clear()
        self.stop_loop()
        self.refresh_gui(True)

    def step_gui(self) -> None:
        logging.info("Step button was clicked.")
        self.engine.step()
        self.refresh_gui()

    def random(self) -> None:
        self.engine.random()
        self.refresh_gui()

    ##### Generation Speed #####

    def speed_control(self, slider_val) -> None:
        slider_val_int = int(slider_val)
        if   (slider_val_int  < 0): self.speed = abs(slider_val_int)
        elif (slider_val_int >= 1): self.speed = 1 / slider_val_int

        self.refresh_gui()

    ##### Cells Pan and Zoom #####

    def start_pan(self, event: tk.Event) -> None:
        logging.info("Mouse left button was clicked")
        self.is_dragging = False
        self.cells_canvas.scan_mark(round(event.x), round(event.y))

    def do_pan(self, event: tk.Event) -> None:
        logging.info("Mouse left button pressed and moving")
        self.is_dragging = True
        self.cells_canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 0.9
        
        x = self.cells_canvas.canvasx(event.x)
        y = self.cells_canvas.canvasy(event.y)
        
        # Scale all items on the canvas
        self.cells_canvas.scale("all", x, y, factor, factor)
        
        # Update the scroll region
        self.cells_canvas.configure(scrollregion=self.cells_canvas.bbox("all"))

    ##### GUI Refresh #####

    def refresh_stats(self) -> None:
        self.pop_stat_lbl.config    (text=f"Population: {self.engine.population}")
        self.gen_stat_lbl.config    (text=f"Generation: {self.engine.gen}")
        self.density_stat_lbl.config(text=f"Density: {self.engine.density}")
        self.growth_rate_lbl.config (text=f"Growth Rate: {self.engine.growth_rate}")

    def refresh_cells(self) -> None: # TODO optimize
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                color = self.CLR_ALIVE_CELL if self.engine.grid[r, c] else self.CLR_DEAD_CELL
                self.cells_canvas.itemconfig(self.cell_buttons[r][c], fill=color)

        #self.root.update()
        #self.get_coordinates() #TODO export canvas only with stats

    def refresh_buttons(self, clear: bool) -> None:
        next_text = "Stop" if self.running else "Start"
        self.start_btn.config(text=next_text)

        if self.slider_var.get() >= 1:
            self.speed_slider.config(label=f"{self.slider_var.get()} gen/sec")
        else:
            self.speed_slider.config(label=f"{abs(self.slider_var.get())} sec/gen")

        if self.engine.has_live_cells():
            self.start_btn.config(bg=self.CLR_CLK_BTN, state=tk.NORMAL)
            self.clear_btn.config(bg=self.CLR_CLK_BTN, state=tk.NORMAL)
            self.step_btn.config (bg=self.CLR_CLK_BTN, state=tk.NORMAL)
        else:
            if not self.running:
                self.start_btn.config(bg=self.CLR_GREYED_BTN, state=tk.DISABLED)
            self.clear_btn.config(bg=self.CLR_GREYED_BTN, state=tk.DISABLED)
            self.step_btn.config (bg=self.CLR_GREYED_BTN, state=tk.DISABLED)

        if clear: self.presets_opts.set("Select preset")

    def refresh_gui(self, clear: bool = False) -> None:
        logging.info("Refreshing the GUI")
        logging.debug(f"Running: {self.running}")

        self.refresh_buttons(clear)
        self.refresh_cells()
        self.refresh_stats()

    ##### Saving to GIF #####

    def get_coordinates(self) -> None:
        logging.info("Recording the GUI")

        if not self.root.winfo_exists():
            return

        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = self.root.winfo_width()
        h = self.root.winfo_height()


        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        self.frames.append(img)

    def save_recording(self) -> None:
        logging.info("Saving the game record")

        if not self.frames:
            logging.error("No frames to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
            initialfile="gameoflife.gif",
            title="Choose where to save your game recording"
        )

        if not file_path:
            logging.info("No path was selected.")
            return

        self.frames[0].save(
            file_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=500,
            loop=0
        )

        logging.info(f"The recording was saved successfully to: {file_path}")