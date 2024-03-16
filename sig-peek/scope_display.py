import tkinter as tk

from . import constants 

class Scope_Display:
    def __init__(self, master, settings):
        self.master = master        
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

    def draw_signal(self, signal:list[float]):
        pixel_amplitude:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
        pixel_amplitude = self.settings['vertical']/pixel_amplitude
        for i, point in enumerate(signal):
            y = int(point/pixel_amplitude) + constants.Display.SIZE/2
            self.canvas.create_line(i, y, i+1, y, fill='blue') 

def open_display(signal, settings):
    root = tk.Tk()
    scope_display = Scope_Display(root, settings)
    scope_display.draw_signal(signal)
    scope_display()
    root.mainloop()
