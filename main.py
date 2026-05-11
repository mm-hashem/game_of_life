import logging
import tkinter as tk
from engine import GameOfLife
from rle_manager import RLEManager
from gui import GameOfLifeGUI

def main() -> None:
    logging.basicConfig(
        filename='gol.log', filemode='w', level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
    )

    root = tk.Tk()
    logging.info("Instantiated Tkinter")

    engine = GameOfLife()
    logging.info("Instantiated GameOfLife")

    rle_manager = RLEManager()

    gui = GameOfLifeGUI(root, engine, rle_manager)
    logging.info("Instantiated GameOfLifeGUI")

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    logging.info("Starting Tkinter mainloop")
    root.mainloop()

if __name__ == "__main__":
    main()