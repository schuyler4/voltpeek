import tkinter as tk

from voltpeek import constants 
from voltpeek.cursors import Cursors

#TODO: Make this more OO
class Scope_Display:
    def __init__(self, master):
        self.master:tk.Tk = master        
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(
            self.frame, 
            height=constants.Display.SIZE, 
            width=constants.Display.SIZE,  
            bg=constants.Display.BACKGROUND_COLOR)
        self._draw_grid()
        self.vector = None

    def __call__(self):
        self.canvas.pack()
        self.frame.grid(row=0, column=0, pady=constants.Application.PADDING)

    def _draw_grid(self):
        grid_spacing:int = constants.Display.SIZE/constants.Display.GRID_LINE_COUNT
        for i in range(1, constants.Display.GRID_LINE_COUNT+1):
            # Draw Vertical Grid Lines
            self.canvas.create_line(grid_spacing*i, 0, grid_spacing*i, 
                constants.Display.SIZE, fill=constants.Display.GRID_LINE_COLOR)
            # Draw Horizontal Grid Lines
            self.canvas.create_line(0, grid_spacing*i, 
                constants.Display.SIZE, grid_spacing*i, fill=constants.Display.GRID_LINE_COLOR)

    def set_vector(self, vector:list[float]):
        self.vector:list[int] = vector
        self._redraw()
        self._draw_vector()

    def set_trigger_level(self, trigger_level) -> None:
        self.trigger_level:int = trigger_level
        self._redraw()
        if(self.vector is not None):
            self._draw_vector()
        self._draw_trigger_level()

    def get_trigger_level(self) -> int: return constants.Display.SIZE - self.trigger_level

    def increment_trigger_level(self) -> None:
        if(self.trigger_level < constants.Display.SIZE):
            self.set_trigger_level(self.trigger_level - 1)
        
    def decrement_trigger_level(self) -> None: 
        if(self.trigger_level > 0): self.set_trigger_level(self.trigger_level + 1)

    def _redraw(self) -> None:
        self.canvas.delete('all')
        self._draw_grid()

    def _draw_vector(self):
        self._redraw()
        for i, point in enumerate(self.vector):
            self.canvas.create_line(i-1, constants.Display.SIZE - point, i+2, 
                constants.Display.SIZE - point, fill=constants.Signal.COLOR) 
            self.canvas.create_line(i-1, constants.Display.SIZE - point + 1, i+2, 
                constants.Display.SIZE - point + 1, fill=constants.Signal.COLOR) 
            self.canvas.create_line(i-1, constants.Display.SIZE - point - 1, i+2, 
                constants.Display.SIZE - point-1, fill=constants.Signal.COLOR) 

    def _draw_horizontal_line(self, position, color):
        self.canvas.create_line(0, position, constants.Display.SIZE, position,
            fill=color)

    def _draw_vertical_line(self, position, color):
        self.canvas.create_line(position, 0, position, constants.Display.SIZE, fill=color)

    def _draw_trigger_level(self):
        self._draw_horizontal_line(self.trigger_level, constants.Display.TRIGGER_LINE_COLOR)

    def set_cursors(self, cursors:Cursors):
        self._redraw()
        if(cursors.hor_visible):
            self._draw_horizontal_line(cursors.hor1_pos, constants.Display.CURSOR_COLOR)  
            self._draw_horizontal_line(cursors.hor2_pos, constants.Display.CURSOR_COLOR)
        if(cursors.vert_visible):
            self._draw_vertical_line(cursors.vert1_pos, constants.Display.CURSOR_COLOR)
            self._draw_vertical_line(cursors.vert2_pos, constants.Display.CURSOR_COLOR)
