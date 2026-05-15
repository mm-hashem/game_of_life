import re
import logging
from pathlib import Path
from typing import List, Tuple, Set, Optional

class RLEManager:
    """Manages RLE (Run-Length Encoded) patterns for Life-like games.

    This class provides functionality to load, parse, and convert RLE files
    containing patterns into coordinate lists.
    """

    header_re = r"\s*x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+),\s*rule\s*=\s*B(\d+)\/S(\d*)"
    item_re   = r"\d*[bo]?"

    # TODO add check for max rows and cols of the result coordinates
    def __init__(self, folder_path: str = "patterns"):
        """Initializes the RLEManager with a folder path for patterns.

        Args:
            folder_path: Path to the directory containing .rle files.
                Defaults to "patterns".
        """
        self.folder_path = folder_path
        self.available_patterns = []

        self.refresh_pattern_list()

    def refresh_pattern_list(self) -> None:
        """Scans the folder for .rle files and updates the available patterns list."""
        path = Path(self.folder_path)
        if not path.exists() or not path.is_dir():
            logging.error("The patterns folder doesn't exist") # 
            return
        
        # Get patterns names
        self.available_patterns = [f.stem for f in path.glob("*.rle")]

    def load_file(self, filename: str) -> Optional[str]:
        """Loads the content of an RLE file.

        Args:
            filename: Name of the pattern file without extension.

        Returns:
            The content of the file as a string, or None if loading fails.
        """
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
        
    def parse_rle(self, pattern_name: str) -> Optional[Tuple[str, Tuple[int, int], Set[int], Set[int]]]:
        """Parses an RLE file and extracts pattern data.

        Uses iteration to read through the file lines, extract the header
        information, and concatenate the pattern lines into a single string.

        Args:
            pattern_name: Name of the pattern to parse.

        Returns:
            A tuple containing:
            - pattern_str: The encoded pattern string.
            - center: Center coordinates as (row, col).
            - birth: Set of birth rule numbers.
            - survive: Set of survive rule numbers.
            Or None if parsing fails.
        """

        file = self.load_file(pattern_name)
        if file is None:
            logging.error("The read file is empty")
            return None
        
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
                    return None
                
                cols    = max(1, int(match.group(1)))
                rows    = max(1, int(match.group(2)))
                birth   = {int(char) for char in match.group(3)}
                survive = {int(char) for char in match.group(4)}

                break

        # Defaulting to Moore (8 neighbors)
        if len(birth) > 8 + 1 and all(x > 8 for x in birth):
            logging.error("Invalid birth rule")
            return None

        if len(survive) > 8 + 1 and all(x > 8 for x in survive):
            logging.error("Invalid survive rule")
            return None
            
        center = (round(rows / 2), round(cols / 2))

        # Merge all items into one string
        for line in file_iter:
            if line.strip()[0] == "#": continue
            else:
                pattern += line.strip()

        return (pattern, center, birth, survive)

    def calculate_coords(self, pattern_str: str, center: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Calculates coordinates from RLE pattern string.

        Args:
            pattern_str: The RLE encoded pattern string.
            center: Center coordinates as (row, col).

        Returns:
            List of (row, col) tuples representing live cells.
        """
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
    
    def get_configs(self, pattern_name: str) -> Optional[Tuple[List[Tuple[int, int]], Set[int], Set[int]]]:
        """Gets configuration data for a pattern.

        Args:
            pattern_name: Name of the pattern.

        Returns:
            A tuple containing:
            - coords: List of (row, col) coordinates.
            - birth: Set of birth rule numbers.
            - survive: Set of survive rule numbers.
            Or None if parsing fails.
        """
        parsed = self.parse_rle(pattern_name)
        if parsed is None:
            return None
        pattern_str, center, birth, survive = parsed
        coords = self.calculate_coords(pattern_str, center)
        return (coords, birth, survive)