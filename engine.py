import numpy as np
import logging

class GameOfLife:

    neighbor_coords = {
        "Moore": [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ],
        "Von Neumann": [
                 (-1, 0),
        (0, -1),          (0, 1),
                 (1, 0)
        ]
    }

    DEFAULT_ROWS = 50
    DEFAULT_COLS = 50

    def __init__(self, rows: int = 50, cols: int = 50):
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
        self.population = 0
        self.population_prev = 0
        self.gen         = 0
        self.density     = 0.0
        self.growth_rate = 0.0

        # Game rules
        self.neighborhood = "Moore"
        self.birth = {3}
        self.survive = {2, 3}

        try:
            self.create_grid()
            logging.log("Grid created successfully")
        except ValueError as e:
            logging.error(f"Failed to create grid, using default dimensions 50x50: {e}")
            self.rows = self.DEFAULT_ROWS
            self.cols = self.DEFAULT_COLS
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
        self._grid = np.zeros((self.rows, self.cols), dtype=bool)

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
            self._grid[r + center[0], c + center[1]] = True
        self.update_population()

    def step(self) -> None:
        """
        Advances the simulation by one generation.

        Uses iteration over each cell in the grid to determine its next state
        based on the current state and the defined rules, then updates the grid
        and statistics accordingly.
        """
        grid_next_gen = np.zeros_like(self._grid)
        for r in range(self.rows):
            for c in range(self.cols):
                grid_next_gen[r, c] = self.next_state(r, c)
        self._grid = grid_next_gen.copy()
        self.population_prev = self.population
        self.update_population()
        self.gen += 1

    def next_state(self, r: int, c: int) -> bool:
        """
        Determines the next state of the cell at the given position.

        Uses iteration over the defined neighborhood to count live neighbors and
        applies the birth/survival rules.

        Args:
            r: Row index of the cell.
            c: Column index of the cell.

        Returns:
            The next state of the cell (True for alive, False for dead).
        """
        current_cell = self._grid[r, c]

        neighbors_count = 0
        for dr, dc in self.neighbor_coords[self.neighborhood]:
            nr, nc = r + dr, c + dc
        
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self._grid[nr, nc]:
                    neighbors_count += 1

        if current_cell: # Survive
            return neighbors_count in self.survive
        return neighbors_count in self.birth # Birth
    
    def random(self) -> None:
        """
        Randomizes the grid with live cells.
        """
        self.clear()
        self._grid = np.random.randint(0, 2, size=self._grid.shape, dtype=bool)
        self.update_population()
    
    def has_live_cells(self) -> bool:
        """
        Checks if the grid has any live cells.

        Returns:
            True if there are live cells, False otherwise.
        """
        return np.any(self._grid)
    
    def update_density(self)-> None:
        """
        Updates the density statistic based on the current population.
        """
        self.density = self.population / float(self.rows * self.cols)

    def update_growth_rate(self) -> None:
        """
        Updates the growth rate statistic based on population change.
        """
        if self.population_prev == 0: return
        self.growth_rate = round(((self.population - self.population_prev) / self.population_prev) * 100, 2)
    
    def update_population(self) -> None:
        """
        Updates the population count and related statistics.
        """
        self.population = np.count_nonzero(self._grid)
        self.update_density()
        self.update_growth_rate()
    
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
            logging.warning(f"Invalid neighborhood type: {neighborhood}, keeping the current one: {self.neighborhood}")
        
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
        self._grid[r, c] = not self._grid[r, c]
        self.update_population()

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
