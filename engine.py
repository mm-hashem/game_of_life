"""
GameOfLife class, which implements the logic for Conway's Game of Life and Life-like cellular automata.

The GameOfLife class manages the grid, applies the rules of the game, and tracks statistics such as population and growth rate.
The class provides methods for loading preset patterns, randomizing the grid, toggling cell states, and changing game rules and dimensions.
"""
from scipy.signal import convolve2d
import numpy as np
import random
import logging
import hashlib

class GameOfLife:

    neighbor_coords = {
        "Moore": [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
        ],
        "Von Neumann": [
                 (-1, 0),
        (0, -1),          (0, 1),
                 ( 1, 0)
        ]
    }

    KERNEL_MOORE = np.array([
        [True, True,  True],
        [True, False, True],
        [True, True,  True]
    ], dtype=np.bool)

    KERNEL_VON_NEUMANN = np.array([
        [False, True,  False],
        [True,  False, True],
        [False, True,  False]
    ], dtype=np.bool)

    def __init__(self, rows: int, cols: int) -> None:
        """
        Initializes the GameOfLife instance with specified grid dimensions.

        Args:
            rows: Number of rows in the grid. Defaults to 50.
            cols: Number of columns in the grid. Defaults to 50.

        Raises:
            ValueError: If the provided dimensions are invalid.
        """

        # Cells grid
        self._grid = None
        
        # Dimensions
        self.rows = rows
        self.cols = cols

        # Stats
        self.population      = 0
        self.population_prev = 0
        self.gen         = 0
        self.density     = 0.0
        self.growth_rate = 0.0

        # Game rules
        self.neighborhood = "Moore"
        self.birth   = {3}
        self.survive = {2, 3}

        # Randomness settings
        self.rand_density = 0.5
        self.seed = random.randint(0, 2**32 - 1)
        self.rng  = np.random.default_rng(self.seed)
        self.seed_set = False # Flag that seed was set, to prevent reseeding on every randomization

        try:
            self.create_grid()
            logging.info("Grid created successfully")
        except ValueError as e:
            logging.critical(f"Failed to create grid, invalid dimensions: {e}")
            self.create_grid()
        except Exception as e:
            logging.fatal(f"An unexpected error occurred: {e}")

    def create_grid(self) -> None:
        """
        Initializes the grid based on the current dimensions.

        Raises:
            ValueError: If dimensions are invalid.
        """
        if self.rows < 1 or self.cols < 1:
            raise ValueError(f"Grid dimensions must be >= 1, Received rows: {self.rows}, columns: {self.cols}")
        self._grid = np.zeros((self.rows, self.cols), dtype=np.bool)

    def load_preset(self, coords: list[tuple[int, int]]) -> None:
        """
        Loads a preset pattern onto the grid based on the provided coordinates.
        
        Uses iteration over the list of coordinates to set the corresponding
        cells to alive, centering the pattern on the grid.

        Args:
            coords: A list of (row, column) tuples representing the positions of live cells.
        """
        self.clear()

        center = (round(self.rows / 2), round(self.cols / 2))
        for r, c in coords:
            self._grid[r + center[0], c + center[1]] = 1
        self.update_stats()

    def neighbor_count(self) -> np.ndarray:
        """
        Counts the number of live neighbors for each cell in the grid.

        Uses convolution with the appropriate kernel based on the neighborhood type
        to efficiently count live neighbors for all cells.

        Returns:
            A 2D array of the same shape as the grid, where each element represents
            the count of live neighbors for the corresponding cell.
        """
        if self.neighborhood == "Moore":
            return convolve2d(self._grid.astype(np.uint8), self.KERNEL_MOORE.astype(np.uint8), mode='same', boundary='fill', fillvalue=0)
        elif self.neighborhood == "Von Neumann":
            return convolve2d(self._grid.astype(np.uint8), self.KERNEL_VON_NEUMANN.astype(np.uint8), mode='same', boundary='fill', fillvalue=0)
        else:
            raise ValueError(f"Invalid neighborhood type: {self.neighborhood}")
        
    def step(self) -> None:
        """
        Advances the simulation by one generation.

        Applies the rules of the game to determine which cells will be alive or dead in the next generation.
        """
        neighbors = self.neighbor_count()
        alive = self._grid
        self._grid = (
            ((alive == True)  & np.isin(neighbors, list(self.survive))) |
            ((alive == False) & np.isin(neighbors, list(self.birth)))
        ).astype(np.bool)
        self.update_stats()

    def set_rand_density(self, density: float) -> None:
        """
        Sets the density for randomization.

        Args:
            density: A float value between 0.0 and 1.0 representing the desired density of live cells.

        Raises:
            ValueError: If the provided density is out of bounds.
        """
        if density < 0.0 or density > 1.0:
            raise ValueError(f"Density must be between 0.0 and 1.0, Received density: {density}")
        self.rand_density = density


    def set_seed(self, seed: int | str | None = None, seed_set: bool = False) -> None:
        """
        Sets the seed for randomization.

        Args:
            seed: A value for the random number generator. If None, a new random seed will be used.
            seed_set: A boolean flag indicating whether the seed was explicitly set, to prevent reseeding on every randomization.
        """
        
        if seed_set or self.seed_set:
            self.seed = seed
            self.seed_set = True
            if isinstance(seed, str):
                numeric_seed = int(hashlib.md5(seed.encode()).hexdigest(), 16) % 2**32
            else:
                numeric_seed = seed
            self.rng = np.random.default_rng(numeric_seed)
        else:
            self.seed = random.randint(0, 2**32 - 1)
            self.rng  = np.random.default_rng(self.seed)
    
    def random(self) -> None:
        """
        Randomizes the grid with live cells.
        """

        self.clear()

        if self.seed_set:
            self.set_seed(self.seed, seed_set=True)
        else:
            self.set_seed()

        self._grid = self.rng.choice(
            [True, False], size=self._grid.shape,
            p=[self.rand_density, 1 - self.rand_density]
        ).astype(dtype=np.bool)

        self.update_stats()
        
    def update_stats(self) -> None:
        """
        Updates all statistics related to the current state of the grid.
        """
        self.population_prev = self.population
        self.population = np.count_nonzero(self._grid)
        self.density = self.population / float(self.rows * self.cols)
        if self.population_prev != 0:
            self.growth_rate = round(((self.population - self.population_prev) / self.population_prev) * 100, 2)
        self.gen += 1
    
    def change_rules(self, birth: set[int], survive: set[int], neighborhood: str | None = None) -> None:
        """
        Changes the game rules for birth, survival, and neighborhood.

        Args:
            birth: Set of neighbor counts that cause a dead cell to become alive.
            survive: Set of neighbor counts that allow a live cell to survive.
            neighborhood: Optional neighborhood type ('Moore' or 'Von Neumann').
        """
        if neighborhood is not None and neighborhood in self.neighbor_coords:
            self.neighborhood = neighborhood
        else:
            logging.info(f"Neighborhood type was not provided, keeping the current one: {self.neighborhood}")
        
        self.birth   = birth
        self.survive = survive
    
    def toggle(self, r: int, c: int) -> None:
        """
        Toggles the state of the cell at the given position.

        Args:
            r: Row index of the cell.
            c: Column index of the cell.

        Raises:
            ValueError: If coordinates are invalid.
        """
        if self.rows < 1 or self.cols < 1:
            raise ValueError(f"Cell coordinates must be >= 1, Received coordinates: (row={self.rows}, column={self.cols})")
        elif r >= self.rows or c >= self.cols:
            raise ValueError(f"Cell coordinates must be within grid bounds, Received coordinates: (row={r}, column={c}), Grid dimensions: (rows={self.rows}, columns={self.cols})")
        self._grid[r, c] = not self._grid[r, c]
        self.update_stats()

    def change_dimensions(self, rows: int, cols: int) -> None:
        """
        Changes the grid dimensions and recreates the grid.

        Args:
            rows: New number of rows.
            cols: New number of columns.

        Raises:
            ValueError: If dimensions are invalid.
        """
        if self.rows < 1 or self.cols < 1:
            raise ValueError(f"Grid dimensions must be >= 1, Received rows: {self.rows}, columns: {self.cols}")

        self.rows = rows
        self.cols = cols
        self.create_grid()

    def get_cell_state(self, r: int, c: int) -> bool:
        """
        Gets the state of the cell at the given position.

        Args:
            r: Row index of the cell.
            c: Column index of the cell.

        Returns:
            The state of the cell (True for alive, False for dead).
        """
        return self._grid[r, c]

    def clear(self) -> None:
        """
        Clears the grid and resets all statistics.
        """
        self._grid.fill(False)
        self.population = 0
        self.population_prev = 0
        self.gen         = 0
        self.growth_rate = 0.0
        self.density     = 0.0
