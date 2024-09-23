from typing import Optional

import tkinter as tk

from voltpeek import constants 
from voltpeek.cursors import Cursors

class Scope_Display:
    BACKGROUND_COLOR = (0, 0, 0)
    GRID_LINE_COLOR = (128, 128, 128)
    SIGNAL_COLOR = (17, 176, 249)

    def _hex_string_from_rgb(self, rgb: tuple[int]): return '#%02x%02x%02x' % rgb

    def __init__(self, master, cursors) -> None:
        self.master:tk.Tk = master        
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(self.frame, height=constants.Display.SIZE, width=constants.Display.SIZE, 
                                bg=self._hex_string_from_rgb(self.BACKGROUND_COLOR))
        self._draw_grid()
        self.vector:Optional[list[int]] = None
        self.cursors:Optional[Cursors] = cursors

    def __call__(self):
        self.canvas.pack()
        self.frame.grid(row=0, column=0, pady=constants.Application.PADDING)

    def _draw_grid(self) -> None:
        grid_spacing:int = int(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        for i in range(1, constants.Display.GRID_LINE_COUNT+1):
            # Draw Vertical Grid Lines
            self.canvas.create_line(grid_spacing*i, 0, grid_spacing*i, constants.Display.SIZE, 
                                    fill=self._hex_string_from_rgb(self.GRID_LINE_COLOR))
            # Draw Horizontal Grid Lines
            self.canvas.create_line(0, grid_spacing*i,  constants.Display.SIZE, grid_spacing*i, 
                                    fill=self._hex_string_from_rgb(self.GRID_LINE_COLOR))

    def set_cursors(self, cursors:Cursors):
        self.cursors = cursors
        self._redraw()

    def set_vector(self, vector:list[int]):
        self.vector = vector
        self._redraw()

    def set_trigger_level(self, trigger_level) -> None:
        self.trigger_level:int = trigger_level
        self._redraw()
        if self.vector is not None:
            self._draw_vector()
        self._draw_trigger_level()

    def get_trigger_level(self) -> int: return constants.Display.SIZE - self.trigger_level

    def increment_trigger_level(self) -> None:
        if self.trigger_level < constants.Display.SIZE:
            self.set_trigger_level(self.trigger_level - 1)
        
    def decrement_trigger_level(self) -> None: 
        if self.trigger_level > 0: self.set_trigger_level(self.trigger_level + 1)

    def _draw_horizontal_cursors(self) -> None:
        self._draw_horizontal_line(self.cursors.hor1_pos, constants.Display.CURSOR_COLOR)  
        self._draw_horizontal_line(self.cursors.hor2_pos, constants.Display.CURSOR_COLOR)

    def _draw_vertical_cursors(self) -> None:
        self._draw_vertical_line(self.cursors.vert1_pos, constants.Display.CURSOR_COLOR)
        self._draw_vertical_line(self.cursors.vert2_pos, constants.Display.CURSOR_COLOR)

    def _redraw(self) -> None:
        self.canvas.delete('all')
        self._draw_grid()
        if self.vector is not None:
            self._draw_vector()
        if self.cursors.hor_visible:
            self._draw_horizontal_cursors()
        if self.cursors.vert_visible:
            self._draw_vertical_cursors()

    def _draw_vector(self):
        for i, point in enumerate(self.vector):
            if point > 0: 
                # TODO: Possibly refactor this so un-captured points are actually deleted from the
                # signal vector.
                self.canvas.create_line(i-1, constants.Display.SIZE - point, i+2, 
                                        constants.Display.SIZE - point, 
                                        fill=self._hex_string_from_rgb(self.SIGNAL_COLOR)) 
                self.canvas.create_line(i-1, constants.Display.SIZE - point + 1, i+2, 
                                        constants.Display.SIZE - point + 1, 
                                        fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))
                self.canvas.create_line(i-1, constants.Display.SIZE - point - 1, i+2, 
                                        constants.Display.SIZE - point-1, 
                                        fill=self._hex_string_from_rgb(self.SIGNAL_COLOR))

    def _draw_horizontal_line(self, position, color): 
        self.canvas.create_line(0, position, constants.Display.SIZE, position, fill=color)

    def _draw_vertical_line(self, position, color): 
        self.canvas.create_line(position, 0, position, constants.Display.SIZE, fill=color)

    def _draw_trigger_level(self): self._draw_horizontal_line(self.trigger_level, constants.Display.TRIGGER_LINE_COLOR)

    @property
    def image_map(self):
        map: list[list[tuple[int]]] = [[self.BACKGROUND_COLOR for _ in range(0, constants.Display.SIZE)] 
                                       for _ in range(0, constants.Display.SIZE)]
        grid_spacing: int = int(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        # Draw the grid lines.
        for y, row in enumerate(map):
            for x, _ in enumerate(row):
                if y % grid_spacing == 0 or x % grid_spacing == 0 or x == len(map) - 1 or y == len(row) - 1:
                    map[y][x] = self.GRID_LINE_COLOR
        # Draw the signal.
        if self.vector is not None:
            for x, point in enumerate(self.vector):
                for x_padding in range(-1, 2):
                    for y_padding in range(-1, 2):
                        y_point: int = constants.Display.SIZE - int(point) + y_padding
                        x_point: int = int(x) + x_padding
                        if y_point >= 0 and y_point < constants.Display.SIZE and x_point >= 0 and x_point < constants.Display.SIZE: 
                            map[y_point][x_point] = self.SIGNAL_COLOR 
        return map