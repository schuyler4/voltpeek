import tkinter as tk

from voltpeek import constants

from voltpeek.cursors import Cursor_Data
from voltpeek.trigger import TriggerType

class Readout:
    AVERAGE_STRING: str = 'average:'
    RMS_STRING: str = 'rms:'
    BACKGROUND_COLOR: str = 'black'

    def __init__(self, master: tk.Tk, vertical_setting: float, horizontal_setting: float) -> None:
        self.master: tk.Tk = master
        self._vertical_setting: float = vertical_setting
        self._horizontal_setting: float = horizontal_setting
        self.frame: tk.Frame = tk.Frame(self.master, 
            bg=self.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self.status_frame: tk.Frame = tk.Frame(self.frame, 
            bg=self.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self._vertical_text: tk.StringVar = tk.StringVar() 
        self._horizontal_text: tk.StringVar = tk.StringVar()
        self._average_text: tk.StringVar = tk.StringVar()
        self._rms_text: tk.StringVar = tk.StringVar()
        self._status_text: tk.StringVar = tk.StringVar()
        self._fs_text: tk.StringVar = tk.StringVar()
        self._trigger_text: tk.StringVar = tk.StringVar()
        self._probe_text: tk.StringVar = tk.StringVar()
        self._cursor_frame: tk.Frame = tk.Frame(self.frame, 
            bg=self.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS)
        self._cursor_text = {
            'h1': tk.StringVar(),
            'h2': tk.StringVar(),
            'hdelta': tk.StringVar(),
            'v1': tk.StringVar(),
            'v2': tk.StringVar(),
            'vdelta': tk.StringVar()
        }

    def get_vertical_str(self) -> str:
        return str(self._vertical_setting) + ' V/div' 

    def get_horizontal_str(self) -> str:
        return str(self._horizontal_setting) + ' s/div'

    def __call__(self) -> None:
        vertical_label: tk.Label = tk.Label(self.frame, 
            textvariable=self._vertical_text,
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        horizontal_label: tk.Label = tk.Label(self.frame, 
            textvariable=self._horizontal_text,
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        fs_label: tk.Label = tk.Label(self.frame, 
            textvariable=self._fs_text,
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        average_label: tk.Label = tk.Label(self.frame, 
            textvariable=self._average_text,
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        rms_label: tk.Label = tk.Label(self.frame, 
            textvariable=self._rms_text,
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        status_label: tk.Label = tk.Label(self.status_frame, 
            textvariable=self._status_text,
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR)
        trigger_label: tk.Label = tk.Label(self.frame, textvariable=self._trigger_text, 
                                           bg=self.BACKGROUND_COLOR, 
                                           fg=constants.Readout.TEXT_COLOR) 
        probe_label: tk.Label = tk.Label(self.frame, textvariable=self._probe_text, 
                                           bg=self.BACKGROUND_COLOR, 
                                           fg=constants.Readout.TEXT_COLOR) 
        cursor_labels: list[tk.Label] = [tk.Label(self._cursor_frame, 
            textvariable=self._cursor_text[key],
            bg=self.BACKGROUND_COLOR,
            fg=constants.Readout.TEXT_COLOR) for key in self._cursor_text]
        self._vertical_text.set(self.get_vertical_str())  
        self._horizontal_text.set(self.get_horizontal_str()) 
        self._average_text.set(self.AVERAGE_STRING + '----')
        self._rms_text.set(self.RMS_STRING + '----')

        self.status_frame.pack()
        status_label.pack()
        vertical_label.pack()
        horizontal_label.pack()
        fs_label.pack()
        trigger_label.pack()
        probe_label.pack()
        average_label.pack()
        rms_label.pack()

        for label in cursor_labels:
            label.pack()
        self.frame.grid(sticky=tk.N, row=0, column=1, padx=constants.Application.PADDING,
                                                      pady=constants.Application.PADDING)

    def update_settings(self, new_vertical_setting: float, 
                        new_horizontal_setting: float) -> None:
        self._vertical_setting = new_vertical_setting
        self._horizontal_setting = new_horizontal_setting
        self._vertical_text.set(self.get_vertical_str())
        self._horizontal_text.set(self.get_horizontal_str())

    def update_cursors(self, cursor_data: Cursor_Data) -> None:
        for key in cursor_data:
            self._cursor_text[key].set(key + ':' + str(cursor_data[key]))

    def set_average(self, average: float) -> None:
        self._average_text.set(self.AVERAGE_STRING + str(average) + 'V')

    def set_rms(self, rms: float) -> None:
        self._rms_text.set(self.RMS_STRING + str(rms) + 'Vrms')

    def set_fs(self, fs: float) -> None: self._fs_text.set('fs:' + str(fs) + 'S/s')

    def set_status(self, status_str: str) -> None: self._status_text.set(status_str)

    def set_probe(self, probe_div: int) -> None:
        self._probe_text.set('Probe: ' + str(probe_div) + 'X')

    def enable_cursor_readout(self, cursor_data: Cursor_Data) -> None:
        self.update_cursors(cursor_data)
        self._cursor_frame.pack() 

    def set_trigger_type(self, trigger_type: TriggerType):
        if trigger_type == TriggerType.RISING_EDGE:
            self._trigger_text.set('trigger: /') 
        elif trigger_type == TriggerType.FALLING_EDGE:
            self._trigger_text.set('trigger \\')

    def disable_cursor_readout(self) -> None: self._cursor_frame.pack_forget()