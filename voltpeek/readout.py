import tkinter as tk

from . import messages

class Readout:
    def __init__(self, master, settings):
        self.master:tk.Tk = master
        self._settings = settings
        self.frame:tk.Frame = tk.Frame(self.master)
        self._vertical_text:tk.StringVar = tk.StringVar() 
        self._horizontal_text:tk.StringVar = tk.StringVar()

    def get_vertical_str(self) -> str:
        return str(self._settings['vertical']) + ' ' + messages.Units.VERTICAL_UNIT

    def get_horizontal_str(self) -> str:
        return str(self._settings['horizontal']) + ' ' + messages.Units.HORIZONTAL_UNIT
      
    def __call__(self):
        vertical_label:tk.Label = tk.Label(self.frame, textvariable=self._vertical_text)
        horizontal_label:tk.Label = tk.Label(self.frame, textvariable=self._horizontal_text)
        self._vertical_text.set(self.get_vertical_str())  
        self._horizontal_text.set(self.get_horizontal_str()) 
        vertical_label.pack()
        horizontal_label.pack()
        self.frame.pack(side='right')

    def update_settings(self, new_settings):
        self._settings = new_settings
        self._vertical_text.set(self.get_vertical_str())
        self._horizontal_text.set(self.get_horizontal_str())
