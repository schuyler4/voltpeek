import tkinter as tk

from . import constants 

class Scope_Display:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(self.master)
        self.canvas = tk.Canvas(
            master, 
            height=constants.Display.SIZE, 
            width=constants.Display.SIZE,  
            bg=constants.Display.BACKGROUND_COLOR)
        self.draw_grid()
        self.canvas.pack()

    def draw_grid(self):
        grid_spacing:int = constants.Display.SIZE/constants.Display.GRID_LINE_COUNT
        for i in range(1, constants.Display.GRID_LINE_COUNT+1):
            # Draw Vertical Grid Lines
            self.canvas.create_line(grid_spacing*i, 
                0, grid_spacing*i, constants.Display.SIZE, fill='white')
            # Draw Horizontal Grid Lines
            self.canvas.create_line(0, grid_spacing*i, 
                constants.Display.SIZE, grid_spacing*i, fill='white')

def open_display():
    root = tk.Tk()
    scope_display = Scope_Display(root)
    root.mainloop()
