import tkinter as tk

from voltpeek import constants 

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

    # TODO: There is a bug below maybe
    def set_vector(self, vector:list[float]):
        self.vector:list[int] = vector
        self._redraw()
        self._draw_vector()

    def set_trigger_level(self, trigger_level):
        self.trigger_level:int = trigger_level
        self._redraw()
        self._draw_vector()
        self._draw_trigger_level()

    def _redraw(self) -> None:
        self.canvas.delete('all')
        self._draw_grid()

    def _draw_vector(self):
        for i, point in enumerate(self.vector):
            self.canvas.create_line(i, 
                constants.Display.SIZE - point, 
                i+1, constants.Display.SIZE - point, 
                fill=constants.Signal.COLOR) 

    def _draw_trigger_level(self):
        self.canvas.create_line(0, 
            trigger_level, 
            constants.Display.SIZE, 
            self.trigger_level,
            fill=constants.Display.TRIGGER_LINE_COLOR)
