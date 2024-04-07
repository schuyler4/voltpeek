import tkinter as tk

from . import constants 

class Scope_Display:
    def __init__(self, master, settings):
        self.master:tk.Tk = master        
        self.settings = settings
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(
            master, 
            height=constants.Display.SIZE, 
            width=constants.Display.SIZE,  
            bg=constants.Display.BACKGROUND_COLOR)
        self._draw_grid()

    def __call__(self):
        self.canvas.pack()

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
        self.vector:list[float] = vector
        self.draw_vector()

    def update_settings(self, new_settings):
        self.settings = new_settings
        self.draw_vector()

    def draw_vector(self):
        self.canvas.delete('all')
        self._draw_grid()
        pixel_amplitude:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_amplitude = self.settings['vertical']/pixel_amplitude
        for i, point in enumerate(self.vector):
            y = int(point/pixel_amplitude) + constants.Display.SIZE/2
            self.canvas.create_line(i, y, i+1, y, fill=constants.Signal.COLOR) 
