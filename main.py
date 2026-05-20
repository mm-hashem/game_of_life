import sys
import logging
import tkinter as tk
from engine import GameOfLife
from rle_manager import RLEManager
from gui import GameOfLifeGUI

# Check if running in Pyodide
IS_PYD = (sys.platform == "emscripten")

def main() -> None:
    if IS_PYD:
        logging.disable(logging.CRITICAL)
    elif __debug__:
        logging.basicConfig(
            filename='gol.log', filemode='w', level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(filename)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
        )

    root = tk.Tk()
    logging.info("Instantiated Tkinter")

    ROWS = 50
    COLS = 50
    PATTERNS_FOLDER = "patterns"

    engine = GameOfLife(ROWS, COLS)
    logging.info("Instantiated GameOfLife")

    rle_manager = RLEManager(PATTERNS_FOLDER)

    gui = GameOfLifeGUI(root, engine, rle_manager)
    logging.info("Instantiated GameOfLifeGUI")

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    logging.info("Starting Tkinter mainloop")
    root.mainloop()

if __name__ == "__main__":
    main()