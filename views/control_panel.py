"""Control panel UI for the Game of Life simulator.

This module defines the ControlPanel class, which creates and manages the
button controls, preset menu, and speed slider used by the main simulation
window.
"""

import logging
import tkinter as tk
from styles import Styles

class ControlPanel:
    """Builds and manages the simulation control panel widgets."""

    def __init__(
            self, ctrl_frame: tk.Frame, available_patterns: list,
            on_random, on_rewind, on_clear, on_start, on_step, on_open_settings,
            on_preset_select, on_speed_change
        ):
        """Initialize the control panel and wire all UI callbacks.

        Args:
            ctrl_frame: Parent frame used to place the controls.
            available_patterns: List of preset patterns for the dropdown menu.
            on_random: Callback triggered by the Random button.
            on_rewind: Callback triggered by the Rewind button.
            on_clear: Callback triggered by the Clear button.
            on_start: Callback triggered by the Start/Stop button.
            on_step: Callback triggered by the Step button.
            on_open_settings: Callback triggered by the Settings button.
            on_preset_select: Callback for preset menu selection changes.
            on_speed_change: Callback for speed slider updates.
        """

        self.ctrl_frame = ctrl_frame
        self.on_speed_change = on_speed_change # To be called when the slider value changes
        self.slider_val_prev = 1

        self.styles = Styles(size="medium", show_label_border=True, label_background="light")

        ##### Select preset dropdown menu

        self._selected_pattern = tk.StringVar(value="Select pattern")
        self.preset_opts_list = tk.OptionMenu(
            self.ctrl_frame, self._selected_pattern,
            *available_patterns,
            command=on_preset_select
        )
        self.preset_opts_list.config(**self.styles.STYLE_CLK_BTN)
        self.preset_opts_list["menu"].config(
            bg=self.styles.CLR_BG, fg=self.styles.CLR_TEXT, bd=0, relief="flat"
        )

        ##### Random Button
        self.random_btn = tk.Button(
            self.ctrl_frame, text="Random", **self.styles.STYLE_CLK_BTN,
            command=on_random
        )

        ##### Rewind Button
        self.rewind_btn = tk.Button(
            self.ctrl_frame, text="Rewind", **self.styles.STYLE_GREYED_BTN,
            state=tk.DISABLED, command=on_rewind
        )

        ##### Clear Button
        self.clear_btn = tk.Button(
            self.ctrl_frame, text="Clear", **self.styles.STYLE_GREYED_BTN,
            state=tk.DISABLED, command=on_clear
        )

        ##### Start Button
        self.start_btn = tk.Button(
            self.ctrl_frame, text="Start",
            **(self.styles.STYLE_GREYED_BTN | {"padx": 15, "font": ("Segoe UI", 14)}),
            state=tk.DISABLED, command=on_start
        )
        
        ##### Step Button
        self.step_btn = tk.Button(
            self.ctrl_frame, text="Step", **self.styles.STYLE_GREYED_BTN,
            state=tk.DISABLED, command=on_step
        )
        
        ##### Speed Slider
        self.speed_slider = tk.Scale(
            self.ctrl_frame, **self.styles.STYLE_SLIDER, orient="horizontal",
            from_=-10, to=10, label="1 gen/sec", resolution=1, showvalue=0,
            command=lambda val: self.slider_control(int(val))
        )

        ##### Settings Button
        self.open_settings_btn = tk.Button(
            self.ctrl_frame, text="Settings", **self.styles.STYLE_CLK_BTN,
            command=on_open_settings
        )

        self.initialize_view()

    def initialize_view(self):
        """Initializes the control panel's view and places its components."""
        logging.info("Initializing control panel view.")

        # Set default slider value to 1 gen/sec
        self.speed_slider.set(1)

        # Place components in the control panel
        self.preset_opts_list.grid (row=0, column=0, padx=10, pady=5)
        self.random_btn.grid       (row=0, column=1, padx=10, pady=5)
        self.rewind_btn.grid       (row=0, column=2, padx=10, pady=5)
        self.clear_btn.grid        (row=0, column=3, padx=10, pady=5)
        self.start_btn.grid        (row=0, column=4, padx=10, pady=5)
        self.step_btn.grid         (row=0, column=5, padx=10, pady=5)
        self.speed_slider.grid     (row=0, column=6, padx=10, pady=5)
        self.open_settings_btn.grid(row=0, column=7, padx=10, pady=5)

    def refresh(
            self, clear_optmenu: bool, is_running: bool,
            has_population: bool, is_grid_saved: bool
        ) -> None:
        """Refresh the panel state after simulation or UI changes.

        Args:
            clear_optmenu: Whether to reset the preset selection label.
            is_running: Whether the simulation is currently running.
            has_population: Whether the current grid has live cells.
            is_grid_saved: Whether the grid is saved.
        """

        self.refresh_buttons(
            clear_optmenu=clear_optmenu, is_running=is_running,
            has_population=has_population, is_grid_saved=is_grid_saved
        )

        # Slider will be refreshed when the user interacts with it, so no need to refresh it here

    def refresh_buttons(
            self,
            clear_optmenu: bool,
            is_running: bool,
            has_population: bool,
            is_grid_saved: bool
        ) -> None:
        """Update the enabled state and labels for the action buttons.

        Args:
            clear_optmenu: Whether to reset the preset selection label.
            is_running: Whether the simulation is currently running.
            has_population: Whether live cells exist in the current grid.
            is_grid_saved: Whether the grid is saved.
        """
        next_text = "Stop" if is_running else "Start"
        self.start_btn.config(text=next_text)

        if has_population:
            self.start_btn.config(bg=self.styles.CLR_CLK_BTN, state=tk.NORMAL)
            self.clear_btn.config(bg=self.styles.CLR_CLK_BTN, state=tk.NORMAL)
            self.step_btn.config (bg=self.styles.CLR_CLK_BTN, state=tk.NORMAL)
        else:
            self.start_btn.config(bg=self.styles.CLR_GREYED_BTN, state=tk.DISABLED)
            self.clear_btn.config(bg=self.styles.CLR_GREYED_BTN, state=tk.DISABLED)
            self.step_btn.config (bg=self.styles.CLR_GREYED_BTN, state=tk.DISABLED)

        if is_grid_saved:
            self.rewind_btn.config(bg=self.styles.CLR_CLK_BTN, state=tk.NORMAL)
        else:
            self.rewind_btn.config(bg=self.styles.CLR_GREYED_BTN, state=tk.DISABLED)

        if clear_optmenu: self._selected_pattern.set("Select pattern")

    def slider_control(self, slider_val: int) -> None:
        """Handle speed slider changes and keep the display consistent.

        Args:
            slider_val: The raw numeric value selected by the slider.
        """

        if self.slider_val_prev == 1 and slider_val in (-1, 0):
            self.speed_slider.set(-2)
        elif self.slider_val_prev == -2 and slider_val in (-1, 0):
            self.speed_slider.set(1)

        adjusted_slider_val = int(self.speed_slider.get())
        self.slider_val_prev = adjusted_slider_val

        self.refresh_slider(adjusted_slider_val)
        self.on_speed_change(adjusted_slider_val)

    def refresh_slider(self, slider_val: int) -> None:
        """Update the slider label to show generations per second or seconds per generation."""
        if slider_val >= 1:
            self.speed_slider.config(label=f"{slider_val} gen/sec")
        else:
            self.speed_slider.config(label=f"{abs(slider_val)} sec/gen")