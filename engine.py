import numpy as np

class GameOfLife:

    def __init__(self, rows: int = 50, cols: int = 50):
        self.rows = rows
        self.cols = cols
        self.center = None
        self.grid = None
        self.population = 0
        self.population_prev = 0
        self.gen         = 0
        self.density     = 0.0
        self.growth_rate = 0.0

        self.create_grid()

    def create_grid(self) -> None:
        self.center = (round(self.rows / 2), round(self.cols / 2))
        self.grid = np.zeros((self.rows, self.cols), dtype=bool)

    def load_preset(self, coords: list) -> None:
        self.clear()
        for r, c in coords:
            self.grid[r + self.center[0], c + self.center[1]] = True
        self.update_population()

    def step(self) -> None:
        grid_next_gen = np.zeros_like(self.grid)
        for r in range(self.rows):
            for c in range(self.cols):
                grid_next_gen[r, c] = self.next_state(r, c)
        self.grid = grid_next_gen.copy()
        self.population_prev = self.population
        self.update_population()
        self.gen += 1

    def next_state(self, r: int, c: int) -> bool:
        current_cell = self.grid[r, c]
        neighbors = self.grid[max(0, r-1):r+2, max(0, c-1):c+2]
        neighbors_count = np.sum(neighbors) - current_cell
        if current_cell:
            return 2 <= neighbors_count <= 3
        return neighbors_count == 3
    
    def random(self) -> None:
        self.clear()
        self.grid = np.random.randint(0, 2, size=self.grid.shape, dtype=bool)
        self.update_population()
    
    def has_live_cells(self) -> bool:
        return np.any(self.grid)
    
    def update_density(self)-> None:
        self.density = self.population / float(self.rows * self.cols)

    def update_growth_rate(self) -> None:
        if self.population_prev == 0: return
        self.growth_rate = round(((self.population - self.population_prev) / self.population_prev) * 100, 2)
    
    def update_population(self) -> None:
        self.population = np.count_nonzero(self.grid)
        self.update_density()
        self.update_growth_rate()
    
    def toggle(self, r: int, c: int) -> None:
        self.grid[r, c] = not self.grid[r, c]
        self.update_population()

    def change_dimensions(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.create_grid()

    def clear(self) -> None:
        self.grid.fill(False)
        self.population = 0
        self.population_prev = 0
        self.gen        = 0
        self.growth_rate = 0.0
        self.density = 0.0
