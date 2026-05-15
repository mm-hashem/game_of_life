# Conway's Game of Life

A Python implementation of Conway's Game of Life with flexible rule customization, support for MCell-style `B/S` rules, and `.rle` pattern loading from the Golly format, capable of simulating Life-Like Cellular Automata.

## Overview

This project follows OOP principles and separates the game engine from the user interface so the simulation logic stays clean and reusable while the GUI handles display and controls.

Key capabilities:
- Standard Conway Life rules by default: `B3/S23`
- Support for custom birth and survival rules using MCell notation
- Two neighborhood modes: `Moore` (8 neighbors) and `Von Neumann` (4 neighbors)
- Adjustable grid dimensions at runtime
- Load and apply Golly `.rle` pattern files from the `patterns/` folder
- Randomize the board, step generation-by-generation, or run continuously
- Export the current simulation as a GIF when Pillow is installed

## Project Structure

- `main.py` - application entry point
- `engine.py` - game logic engine and rules processing
- `gui.py` - Tkinter-based graphical interface and interaction logic
- `rle_manager.py` - parser and loader for `.rle` pattern files
- `settings_window.py` - settings dialog for rules, neighborhood mode, dimensions, and cell size
- `patterns/` - example `.rle` files for preset patterns
- `requirements.txt` - package dependencies

## Features

### Engine
- Dynamic rules via `birth` and `survive` sets
- Full simulation step logic with alive/dead transitions
- Grid resizing with validation
- Live population, density, generation count, and growth rate tracking

### GUI
- Start/stop simulation loop
- Step manually one generation at a time
- Clear board
- Randomize initial state
- Select preset patterns from `.rle` files
- Open settings window to configure rules and grid size
- Pan and zoom the board view
- Export gameplay as a GIF (requires `Pillow`)

### Pattern Loading
- Reads `.rle` files from the `patterns/` directory
- Extracts rule definitions from the header using MCell-style `B` and `S`
- Centers loaded patterns on the current board
- Supported pattern names come from pattern filenames without the `.rle` extension

## Installation

1. Create and activate a Python environment.
2. Install required packages:

```bash
python -m pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Usage

### Buttons
- `Random`: generate a random starting board.
- `Start`: start automatic evolution.
- `Step`: advance one generation.
- `Clear`: reset the board.
- `Select pattern`: Choose a pattern from the dropdown list to load a pattern from `patterns/`.
- Speed slider: adjust simulation speed.
- `Settings`: open settings window.
- `Export GIF`: export the gameplay to a GIF.

### Settings
- Neighborhood mode (`Moore` or `Von Neumann`)
- Birth rule (`B` digits)
- Survival rule (`S` digits)
- Grid dimensions (`rows` and `columns`)
- Cell display size

### Exporting GIFs
- If `Pillow` is installed, the `Export GIF` button will be available.
- The export feature captures the current board state and saves it to disk as GIF.

## Design Notes

- The engine and GUI are separated to follow object-oriented design and the single responsibility principle.
- Rule changes and dimension changes are handled through the settings dialog.
- `.rle` support allows loading standard Life patterns using the Golly file format.

## Requirements

- Python 3.10+ recommended
- `numpy` for simulation grid handling
- `pillow` for GIF export support

## Defaults

- Grid size: `50 x 50`
- Neighborhood: `Moore`
- Rule set: `B3/S23` (Conway's Game of Life)

## Future development

- Optimize memory allocation through the implementation of sparse matrices.
- Improve processing speed by utilizing convolutions and kernels.
- Add rewind button to step back through generations.
- Implement pattern saving and loading in a RLE format.

## License

This project is provided as-is for learning and experimentation with Conway's Game of Life and custom Life rules.