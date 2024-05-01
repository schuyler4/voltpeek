import tkinter as tk

from voltpeek import messages
from voltpeek import constants

from voltpeek.cursors import Cursor_Data

class Readout:
    def __init__(self, master, vertical_setting:float, horizontal_setting:float) -> None:
        self.master:tk.Tk = master
        self._vertical_setting:float = vertical_setting
        self._horizontal_setting:float = horizontal_setting
        self.frame:tk.Frame = tk.Frame(self.master, 
            bg=constants.Readout.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self.status_frame:tk.Frame = tk.Frame(self.frame, 
            bg=constants.Readout.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self._vertical_text:tk.StringVar = tk.StringVar() 
        self._horizontal_text:tk.StringVar = tk.StringVar()
        self._average_text:tk.StringVar = tk.StringVar()
        self._status_text:tk.StringVar = tk.StringVar()
        self._cursor_frame:tk.Frame = tk.Frame(self.frame, 
            bg=constants.Readout.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self._cursor_text:Cursor_Data = {
            'h1': tk.StringVar(),
            'h2': tk.StringVar(),
            'hdelta': tk.StringVar(),
            'v1': tk.StringVar(),
            'v2': tk.StringVar(),
            'vdelta': tk.StringVar()
        }

    def get_vertical_str(self) -> str:
        return str(self._vertical_setting) + ' ' + messages.Units.VERTICAL_UNIT

    def get_horizontal_str(self) -> str:
        return str(self._horizontal_setting) + ' ' + messages.Units.HORIZONTAL_UNIT

    def __call__(self) -> None:
        vertical_label:tk.Label = tk.Label(self.frame, 
            textvariable=self._vertical_text,
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        horizontal_label:tk.Label = tk.Label(self.frame, 
            textvariable=self._horizontal_text,
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        average_label:tk.Label = tk.Label(self.frame, 
            textvariable=self._average_text,
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        status_label:tk.Label = tk.Label(self.status_frame, 
            textvariable=self._status_text,
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        cursor_labels:list[tk.Label] = [tk.Label(self._cursor_frame, 
            textvariable=self._cursor_text[key],
            bg=constants.Readout.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR) for key in self._cursor_text]
        self._vertical_text.set(self.get_vertical_str())  
        self._horizontal_text.set(self.get_horizontal_str()) 
        self._average_text.set(messages.Measurements.AVERAGE + messages.Measurements.NO_DATA)
        self.status_frame.pack()
        status_label.pack()
        vertical_label.pack()
        horizontal_label.pack()
        average_label.pack()
        for label in cursor_labels:
            label.pack()
        self.frame.grid(sticky=tk.N, row=0, column=1, padx=constants.Application.PADDING,
                                                      pady=constants.Application.PADDING)

    def update_settings(self, new_vertical_setting:float, new_horizontal_setting:float) -> None:
        self._vertical_setting = new_vertical_setting
        self._horizontal_setting = new_horizontal_setting
        self._vertical_text.set(self.get_vertical_str())
        self._horizontal_text.set(self.get_horizontal_str())

    def update_cursors(self, cursor_data) -> None:
        for key in cursor_data:
            self._cursor_text[key].set(key + ':' + str(cursor_data[key]))

    def set_average(self, average:float) -> None:
        self._average_text.set(messages.Measurements.AVERAGE + str(average))

    def set_status(self, status_str:str) -> None:
        self._status_text.set(status_str)

    def enable_cursor_readout(self, cursor_data) -> None:
        self.update_cursors(cursor_data)
        self._cursor_frame.pack() 

    def disable_cursor_readout(self) -> None:
        self._cursor_frame.pack_forget()
