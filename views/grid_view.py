import logging
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
from styles import Styles

class GridView:

    def __init__(
            self, grid_canvas: tk.Canvas,
            cell_size: int,
            rows: int,
            cols: int,
            get_sliced_grid: callable,
            toggle_cell: callable
        ):

        self._grid_canvas = grid_canvas
        
        self.toggle_cell = toggle_cell
        self.get_sliced_grid = get_sliced_grid

        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # Image handling
        self.tk_img = None
        self.canvas_img_id = None
        self.palette = np.array([Styles.CLR_DEAD_CELL, Styles.CLR_ALIVE_CELL], dtype=np.uint8)

        self._dragging = False
        self._initial_center_done = False

        self._initialization()

    def refresh(self) -> None:
        """Refreshes the grid view.

        This method should be called whenever the underlying grid data changes and
        the visual representation needs to be updated.
        """
        self._draw_cells()

    def _initialization(self) -> None:
        self._grid_canvas.bind("<Button-1>",        self._start_pan)
        self._grid_canvas.bind("<ButtonRelease-1>", self._on_cell_click)
        self._grid_canvas.bind("<B1-Motion>",       self._do_pan)
        self._grid_canvas.bind("<MouseWheel>",      self._zoom)
        self._grid_canvas.bind("<Configure>",       self._on_canvas_configure)

        self._grid_canvas.after_idle(self._initial_render)

    def _initial_render(self) -> None:
        """Performs the initial rendering of the GUI.

        This method is called after the main loop starts to ensure that the canvas
        has been properly initialized before drawing the cells.
        """

        _, _, view_w, view_h = self._get_viewport(0)

        # If canvas not yet laid out, try again shortly
        if view_w <= 1 or view_h <= 1:
            self._grid_canvas.after(50, self._initial_render)
            return

        if not self._initial_center_done and not self._dragging:
            self._center_canvas()
            self._draw_cells()
            self._initial_center_done = True

    def _on_canvas_configure(self, event) -> None:
        # Don't interfere while the user is actively panning
        if self._dragging:
            return

        grid_w, grid_h = self._get_visual_grid_size()
        if grid_w <= event.width and grid_h <= event.height:
            self._center_canvas()
            self._draw_cells()

    def _center_canvas(self) -> None:
        """Centers the canvas in the window.

        This method adjusts the canvas view to center the visual grid within the
        available space.
        """

        _, _, view_w, view_h = self._get_viewport(0)
        grid_w,  grid_h      = self._get_visual_grid_size()
        total_w, total_h     = self._sync_scrollregion(view_w, view_h, grid_w, grid_h)

        if grid_w > view_w:
            left = (grid_w - view_w) / 2
            self._grid_canvas.xview_moveto(left / total_w)
        else:
            self._grid_canvas.xview_moveto(0)

        if grid_h > view_h:
            top = (grid_h - view_h) / 2
            self._grid_canvas.yview_moveto(top / total_h)
        else:
            self._grid_canvas.yview_moveto(0)

    def _get_viewport(self, event: tk.Event | int = 0) -> tuple[float, float, float, float]:
        """Calculates viewport metrics for the canvas.

        Args:
            event: The mouse event to calculate the viewport for.
                   If 0, uses the top-left corner of the canvas.

        Returns:
            A tuple containing the left, top, width, and height of the visible
            area in canvas coordinates.
        """
        self._grid_canvas.update_idletasks()

        if event != 0:
            x_canvas = self._grid_canvas.canvasx(event.x)
            y_canvas = self._grid_canvas.canvasy(event.y)
        else:
            x_canvas = self._grid_canvas.canvasx(0)
            y_canvas = self._grid_canvas.canvasy(0)

        view_w = max(1, self._grid_canvas.winfo_width())
        view_h = max(1, self._grid_canvas.winfo_height())

        return x_canvas, y_canvas, view_w, view_h
    
    def _get_visual_grid_size(self) -> tuple[float, float]:
        """Calculates the pixel size of the entire visual grid.

        Returns:
            A tuple containing the width and height of the visual grid in pixels.
        """
        cell_size = max(1, self.cell_size)

        grid_w = self.cols * cell_size
        grid_h = self.rows * cell_size

        return grid_w, grid_h
    
    def _sync_scrollregion(self, view_w, view_h, grid_w, grid_h) -> tuple[float, float]:
        """Synchronizes the canvas scrollregion with the visual grid size.

        Args:
            view_w: The width of the visible area.
            view_h: The height of the visible area.
            grid_w: The width of the visual grid.
            grid_h: The height of the visual grid.

        Returns:
            A tuple containing the total width and height of the scrollregion.
        """
        total_w = max(grid_w, view_w)
        total_h = max(grid_h, view_h)

        self._grid_canvas.configure(scrollregion=(0, 0, total_w, total_h))

        return total_w, total_h
    
    def _zoom(self, event: tk.Event) -> None:
        """_zooms the canvas in or out.

        Args:
            event (tk.Event): The mouse wheel event.
        """
        if hasattr(event, "delta"):
            direction = 1 if event.delta > 0 else -1
        else:
            direction = 1 if event.num == 4 else -1 if event.num == 5 else 0
        if direction == 0:
            return

        old_cell = max(1, int(self.cell_size))
        factor   = 1.1 if direction > 0 else 0.9

        # Get the current view metrics before _zooming
        x_canvas,     y_canvas, view_w, view_h = self._get_viewport(event)
        old_grid_w,   old_grid_h   = self._get_visual_grid_size()
        offset_x_old, offset_y_old = self._get_visual_grid_offsets(view_w, view_h, old_grid_w, old_grid_h)

        # Relative position inside the visual grid
        rel_x = (x_canvas - offset_x_old) / old_cell
        rel_y = (y_canvas - offset_y_old) / old_cell

        # Compute new cell size (clamp >= 1)
        new_cell = max(1, int(round(old_cell * factor)))

        # If rounding doesn't change size, step by 1
        if new_cell == old_cell:
            new_cell = max(1, old_cell + (1 if direction > 0 else -1))

        self.cell_size = new_cell

        # Update canvas scrollregion to the new visual grid size
        new_grid_w,   new_grid_h   = self._get_visual_grid_size()
        total_w,      total_h      = self._sync_scrollregion(view_w, view_h, new_grid_w, new_grid_h)
        offset_x_new, offset_y_new = self._get_visual_grid_offsets (view_w, view_h, new_grid_w, new_grid_h)

        new_x_canvas = offset_x_new + rel_x * new_cell
        new_y_canvas = offset_y_new + rel_y * new_cell

        new_x_left = new_x_canvas - event.x
        new_y_top  = new_y_canvas - event.y

        frac_x = 0.0 if total_w == 0 else new_x_left / total_w
        frac_y = 0.0 if total_h == 0 else new_y_top  / total_h
        frac_x = max(0.0, min(1.0, frac_x))
        frac_y = max(0.0, min(1.0, frac_y))

        self._grid_canvas.xview_moveto(frac_x)
        self._grid_canvas.yview_moveto(frac_y)

        # Redraw the image at the new scale
        self._draw_cells()

    ##### Cells Pan and _zoom #####

    def _start_pan(self, event: tk.Event) -> None:
        """Starts panning the canvas.

        Args:
            event (tk.Event): The mouse event.
        """
        logging.info("Mouse left button was clicked")
        self._dragging = False
        self._grid_canvas.scan_mark(round(event.x), round(event.y))

    def _do_pan(self, event: tk.Event) -> None:
        """Performs panning of the canvas.

        Args:
            event (tk.Event): The mouse event.
        """
        logging.info("Mouse left button pressed and moving")
        self._dragging = True
        self._grid_canvas.scan_dragto(event.x, event.y, gain=1)
        self._draw_cells()

    @staticmethod
    def _get_visual_grid_offsets(view_w, view_h, grid_w, grid_h) -> tuple[float, float]:
        """Calculates centering offsets for the visual grid.

        Args:
            view_w: The width of the visible area.
            view_h: The height of the visible area.
            grid_w: The width of the visual grid.
            grid_h: The height of the visual grid.
        
        Returns:
            A tuple containing the x and y offsets to center the visual grid within the visible area.
        """
        offset_x = max(0, (view_w - grid_w) // 2)
        offset_y = max(0, (view_h - grid_h) // 2)

        return offset_x, offset_y
    
    def _draw_cells(self) -> None:
        """Draws the cells on the canvas.

        This method calculates the visible portion of the visual grid, colorizes it,
        and renders it on the canvas. It also handles centering for small visual grids
        and keeps the scroll region in sync with the grid size.
        """
        # Get the current visible pixel coordinates of the canvas viewport
        x_canvas, y_canvas, view_w, view_h = self._get_viewport(0)
        grid_w, grid_h = self._get_visual_grid_size()
        
        # Fallback
        if view_w <= 1: view_w = grid_w
        if view_h <= 1: view_h = grid_h

        # Sync scrollregion
        self._sync_scrollregion(view_w, view_h, grid_w, grid_h)

        # Map pixel coordinates to NumPy grid indices
        start_col = max(0, int(x_canvas // self.cell_size))
        end_col   = min(self.cols, int((x_canvas + view_w) // self.cell_size) + 1)
        
        start_row = max(0, int(y_canvas // self.cell_size))
        end_row   = min(self.rows, int((y_canvas + view_h) // self.cell_size) + 1)
        
        # Slice the array
        visible_grid = self.get_sliced_grid(slice(start_row, end_row), slice(start_col, end_col))

        # Colorize the visible grid
        img_array = self.palette[visible_grid.astype(np.uint8)]
        img = Image.fromarray(img_array, mode='RGB')

        # Resize the visible portion
        target_w = (end_col - start_col) * self.cell_size
        target_h = (end_row - start_row) * self.cell_size
        
        img = img.resize((int(target_w), int(target_h)), resample=Image.NEAREST)
        self.tk_img = ImageTk.PhotoImage(img)

        # Compute centering offset for small grids
        offset_x, offset_y = self._get_visual_grid_offsets(view_w, view_h, grid_w, grid_h)

        # Calculate where this cropped image belongs
        img_x = offset_x + start_col * self.cell_size
        img_y = offset_y + start_row * self.cell_size

        # Update image and shift its coordinates to match the scroll position
        if self.canvas_img_id is None:
            self.canvas_img_id = self._grid_canvas.create_image(img_x, img_y, image=self.tk_img, anchor="nw")
        else:
            self._grid_canvas.itemconfig(self.canvas_img_id, image=self.tk_img)
            self._grid_canvas.coords(self.canvas_img_id, img_x, img_y)

    def _on_cell_click(self, event: tk.Event) -> None:
        """Handles cell click events.

        Toggles the state of the clicked cell.

        Args:
            event (tk.Event): The mouse event.
        """
        if self._dragging:
            logging.info("Mouse released after dragging, not toggling cell")
            #self._dragging = False
            return
        
        x_canvas, y_canvas, view_w, view_h = self._get_viewport(event)
        grid_w,   grid_h   = self._get_visual_grid_size()
        offset_x, offset_y = self._get_visual_grid_offsets(view_w, view_h, grid_w, grid_h)

        c = int((x_canvas - offset_x) // self.cell_size)
        r = int((y_canvas - offset_y) // self.cell_size)

        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            logging.warning(f"Clicked outside of the visual grid bounds, r: {r}, c: {c}")
            return

        logging.info(f"A cell was clicked, r: {r}, c: {c}")

        self.toggle_cell(r, c)