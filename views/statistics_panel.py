"""Widgets that display live simulation statistics in the GUI."""

import logging
import tkinter as tk
from styles import Styles
import logging

class StatisticsPanel:
    """Display a row of labels showing current simulation metrics.

    The panel is intended to live inside a parent frame and updates the
    displayed values whenever the simulation advances.

    Attributes:
        _stats_frame (tk.Frame): Parent frame used to host the labels.
        styles (Styles): Style configuration applied to all labels.
        pop_stat_lbl (tk.Label): Label showing the current population.
        gen_stat_lbl (tk.Label): Label showing the current generation.
        density_stat_lbl (tk.Label): Label showing the current density.
        growth_rate_lbl (tk.Label): Label showing the current growth rate.
    """

    def __init__(self, stats_frame: tk.Frame):
        """Create the statistics panel and place all labels.

        Args:
            stats_frame: The parent frame that will contain the statistics.
        """

        self._stats_frame = stats_frame
        
        self.styles = Styles(size="medium", show_label_border=True, label_background="light")

        self.pop_stat_lbl     = tk.Label(self._stats_frame, text="Population: 0",    **self.styles.STYLE_LABEL)
        self.gen_stat_lbl     = tk.Label(self._stats_frame, text="Generation: 0",    **self.styles.STYLE_LABEL)
        self.density_stat_lbl = tk.Label(self._stats_frame, text="Density: 0.0",     **self.styles.STYLE_LABEL)
        self.growth_rate_lbl  = tk.Label(self._stats_frame, text="Growth Rate: 0.0", **self.styles.STYLE_LABEL)

        self._placement()

    def _placement(self) -> None:
        """Arrange the statistics labels in a single row.

        The labels are positioned using a fixed grid layout so each metric
        remains aligned and visible alongside the others.
        """
        logging.info("Placing the statistics panel components")

        self.pop_stat_lbl.grid(row=0, column=0, padx=10, pady=10)
        self.gen_stat_lbl.grid(row=0, column=1, padx=10, pady=10)
        self.density_stat_lbl.grid(row=0, column=2, padx=10, pady=10)
        self.growth_rate_lbl.grid (row=0, column=3, padx=10, pady=10)

    def refresh(
        self,
        population: int,
        generation: int,
        density: float,
        growth_rate: float,
    ) -> None:
        """Update all displayed statistics with the latest values.

        Args:
            population: The current number of live cells.
            generation: The current simulation generation number.
            density: The current live-cell density as a percentage or ratio.
            growth_rate: The most recent growth rate calculation.
        """
        self.pop_stat_lbl.config(text=f"Population: {population}")
        self.gen_stat_lbl.config(text=f"Generation: {generation}")
        self.density_stat_lbl.config(text=f"Density: {round(density, 2)}")
        self.growth_rate_lbl.config (text=f"Growth Rate: {round(growth_rate, 2)}")