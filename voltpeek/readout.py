import tkinter as tk

from . import messages
from . import constants

class Readout:
    def __init__(self, master, settings):
        self.master:tk.Tk = master
        self._settings = settings
        self.frame:tk.Frame = tk.Frame(self.master, 
            bg=constants.Readout.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self._vertical_text:tk.StringVar = tk.StringVar() 
        self._horizontal_text:tk.StringVar = tk.StringVar()

    def get_vertical_str(self) -> str:
        return str(self._settings['vertical']) + ' ' + messages.Units.VERTICAL_UNIT

    def get_horizontal_str(self) -> str:
        return str(self._settings['horizontal']) + ' ' + messages.Units.HORIZONTAL_UNIT
      
    def __call__(self):
        vertical_label:tk.Label = tk.Label(self.frame, 
            textvariable=self._vertical_text,
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        horizontal_label:tk.Label = tk.Label(self.frame, 
            textvariable=self._horizontal_text,
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        self._vertical_text.set(self.get_vertical_str())  
        self._horizontal_text.set(self.get_horizontal_str()) 
        vertical_label.pack()
        horizontal_label.pack()
        self.frame.pack()

    def update_settings(self, new_settings):
        self._settings = new_settings
        self._vertical_text.set(self.get_vertical_str())
        self._horizontal_text.set(self.get_horizontal_str())
