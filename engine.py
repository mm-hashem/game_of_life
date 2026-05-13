import numpy as np

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

    def __init__(self, rows: int = 50, cols: int = 50):

        # Cells grid
        self.grid = None
        
        # Dimensions
        self.rows = rows
        self.cols = cols
        self.center = None

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

        neighbors_count = 0
        for dr, dc in self.neighbor_coords[self.neighborhood]:
            nr, nc = r + dr, c + dc
        
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr, nc]:
                    neighbors_count += 1

        if current_cell: # Survive
            return neighbors_count in self.survive
        return neighbors_count in self.birth # Birth
    
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
    
    def update_rules(self, neighborhood: str, birth: set, survive: set) -> None:
        self.neighborhood = neighborhood
        self.birth = birth
        self.survive = survive
    
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