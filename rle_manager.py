import re
import logging
from pathlib import Path

class RLEManager:

    header_re = r"\s*x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+),\s*rule\s*=\s*B(\d+)\/S(\d*)"
    item_re   = r"\d*[bo]?"

    # TODO add check for max rows and cols of the result coordinates
    def __init__(self, folder_path: str = "patterns"):
        self.folder_path = folder_path
        self.available_patterns = []

        # TODO REMOVE?
        self.rows = 0
        self.cols = 0
        self.births = 0
        self.survs = 0

        self.refresh_pattern_list()

    def refresh_pattern_list(self) -> None:
        """Scans the folder for .rle files."""
        path = Path(self.folder_path)
        if not path.exists() or not path.is_dir():
            logging.error("The patterns folder doesn't exist") # 
            return
        
        # Get patterns names
        self.available_patterns = [f.stem for f in path.glob("*.rle")]

    def get_pattern_coords(self, name: str) -> list:
        """Loads the actual coordinates only when requested."""
        try:
            filepath = Path(self.folder_path) / f"{name}.rle"
        except:
            logging.error(f"Couldn't locate file {name}")
        return self.parse_rle(filepath)

    @staticmethod
    def load_file(filepath: Path) -> str:
        try:
            rle_text = Path(filepath).read_text(encoding="utf-8")
            return rle_text
        except:
            logging.error(f"Couldn't read file {filepath}")
            return None

    def parse_rle(self, filepath) -> list:
        """Parses an RLE file and returns a list of (x, y) tuples."""
        file = self.load_file(filepath)
        if file is None:
            logging.error("The read file is empty")
            return []
        file_iter = iter(file.splitlines())
        coords = []
        pattern = ""
        # Getting the pattern dimensions
        for line in file_iter:
            # TODO get details from comments
            if line.strip()[0] == "#": continue # Skipping comments
            else:
                match = re.search(self.header_re, line.strip())
                if match is None:
                    logging.error("Invalid RLE header")
                    return
                
                self.cols   = max(1, min(int(match.group(1)), 100))
                self.rows   = max(1, min(int(match.group(2)), 100))
                self.births = max(1, min(int(match.group(3)), 100))
                self.survs  = max(1, min(int(match.group(4)), 100))
                break   

        # Merge all items into one string
        for line in file_iter:
            if line.strip()[0] == "#": continue
            else:
                pattern += line.strip()
        
        pattern_list = pattern[:-1].split("$")

        r = 0; c = 0

        for row in pattern_list:
            matches = re.finditer(self.item_re, row)

            if matches is None:
                logging.error("There are no patterns.")
                return

            for match in matches:
                matched = match.group()
                if 'o' in matched:
                    if len(matched) > 1:
                        for _ in range(int(matched[:-1])):
                            coords.append((r, c))
                            c += 1
                    else:
                        coords.append((r, c))
                        c += 1
                elif 'b' in matched:
                    if len(matched) > 1:
                        c += int(matched[:-1])
                    else: c += 1
                elif matched.isdigit() and len(matched) == 1:
                    print(matched)
                    r += int(matched) - 1
            r += 1
            c = 0

        return coords