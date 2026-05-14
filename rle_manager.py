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

        self.refresh_pattern_list()

    def refresh_pattern_list(self) -> None:
        """Scans the folder for .rle files."""
        path = Path(self.folder_path)
        if not path.exists() or not path.is_dir():
            logging.error("The patterns folder doesn't exist") # 
            return
        
        # Get patterns names
        self.available_patterns = [f.stem for f in path.glob("*.rle")]

    def load_file(self, filename: str) -> str:
        if filename not in self.available_patterns:
            logging.error("This pattern doesn't exist.")
            return None
        
        try:
            filepath = Path(self.folder_path) / f"{filename}.rle"
            rle_text = Path(filepath).read_text(encoding="utf-8")
            return rle_text
        except:
            logging.error(f"Couldn't read file {filepath}")
            return None
        
    def parse_rle(self, pattern_name) -> list[str, tuple[int, int], int, int]:
        """Parses an RLE file and returns a list of (x, y) tuples."""

        file = self.load_file(pattern_name)
        if file is None:
            logging.error("The read file is empty")
            return ""
        
        file_iter = iter(file.splitlines())
        
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
                
                cols    = max(1, min(int(match.group(1)), 100))
                rows    = max(1, min(int(match.group(2)), 100))
                birth   = {int(char) for char in match.group(3)}
                survive = {int(char) for char in match.group(4)}

                break

        # Defaulting to Moore (8 neighbors)
        if len(birth) > 8 + 1 and all(x > 8 for x in birth):
            logging.error("Invalid birth rule")
            return

        if len(survive) > 8 + 1 and all(x > 8 for x in survive):
            logging.error("Invalid survive rule")
            return
            
        center = (round(rows / 2), round(cols / 2))

        # Merge all items into one string
        for line in file_iter:
            if line.strip()[0] == "#": continue
            else:
                pattern += line.strip()

        return [pattern, center, birth, survive]

    def calcuate_coords(self, pattern_str: str, center: tuple[int, int]) -> list[tuple[int, int]]:
        pattern_list = pattern_str[:-1].split("$")
        
        r = -center[0]; c = -center[1]

        coords = []

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
                    r += int(matched) - 1
            r += 1
            c = -center[1]

        return coords
    
    def get_configs(self, pattern_name: str) -> list:
        pattern_str, center, birth, survive = self.parse_rle(pattern_name)
        coords = self.calcuate_coords(pattern_str, center)
        return [coords, birth, survive]