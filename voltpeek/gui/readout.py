import tkinter as tk
from tkinter import ttk

from voltpeek import constants

from voltpeek.cursors import Cursor_Data
from voltpeek.trigger import TriggerType

from voltpeek.helpers import engineering_units

class Readout:
    AVERAGE_STRING: str = 'average: '
    RMS_STRING: str = 'rms: '
    PROBE_STRING: str = 'probe: '
    TRIGGER_STRING: str = 'trigger: '
    BACKGROUND_COLOR: str = 'black'

    def __init__(self, master: tk.Tk, vertical_setting: float, horizontal_setting: float) -> None:
        self.master: tk.Tk = master
        self._vertical_setting: float = vertical_setting
        self._horizontal_setting: float = horizontal_setting
        self.frame: tk.Frame = tk.Frame(
            self.master, 
            bg=self.BACKGROUND_COLOR,
            highlightbackground=constants.Readout.BORDER_COLOR,
            highlightthickness=constants.Readout.BORDER_THICKNESS
        )
        self._status_text: tk.StringVar = tk.StringVar()
        self._vertical_text: tk.StringVar = tk.StringVar() 
        self._horizontal_text: tk.StringVar = tk.StringVar()
        self._fs_text: tk.StringVar = tk.StringVar()
        self._trigger_text: tk.StringVar = tk.StringVar()
        self._probe_text: tk.StringVar = tk.StringVar()
        self._average_text: tk.StringVar = tk.StringVar()
        self._rms_text: tk.StringVar = tk.StringVar()
        self._cursor_text = {
            'h1': tk.StringVar(),
            'h2': tk.StringVar(),
            'hdelta': tk.StringVar(),
            'v1': tk.StringVar(),
            'v2': tk.StringVar(),
            'vdelta': tk.StringVar(),
            '1/vdelta': tk.StringVar()
        }
        self.status_separator = ttk.Separator(self.frame, orient='horizontal')
        self.cursor_separator = ttk.Separator(self.frame, orient='horizontal')
        self._create_labels()

    def _create_labels(self):
        label_style = {
            'bg': self.BACKGROUND_COLOR,
            'fg': 'white',
            'padx': 5,
            'pady': 2,
            'font': ('Arial', 10),
            'anchor': 'w'
        }
        self.status_label = tk.Label(
            self.frame,
            textvariable=self._status_text,
            **label_style
        )
        self.main_labels = [
            tk.Label(self.frame, textvariable=self._vertical_text, **label_style),
            tk.Label(self.frame, textvariable=self._horizontal_text, **label_style),
            tk.Label(self.frame, textvariable=self._fs_text, **label_style),
            tk.Label(self.frame, textvariable=self._trigger_text, **label_style),
            tk.Label(self.frame, textvariable=self._probe_text, **label_style),
            tk.Label(self.frame, textvariable=self._average_text, **label_style),
            tk.Label(self.frame, textvariable=self._rms_text, **label_style),
        ]
        self.cursor_labels = []
        for key in self._cursor_text:
            label = tk.Label(
                self.frame,
                textvariable=self._cursor_text[key],
                **label_style
            )
            self.cursor_labels.append(label)

    def get_vertical_str(self) -> str: 
        return f'{self._vertical_setting} V/div'

    def get_horizontal_str(self) -> str: 
        return f'{engineering_units(self._horizontal_setting)} s/div'

    def set_average(self, average: float) -> None: 
        self._average_text.set(f"{self.AVERAGE_STRING}{average:.3f} V")

    def set_rms(self, rms: float) -> None: 
        self._rms_text.set(f"{self.RMS_STRING}{rms:.3f} Vrms")

    def set_fs(self, fs: float) -> None: 
        self._fs_text.set(f"{engineering_units(fs)}S/s")

    def set_probe(self, probe_div: int) -> None: 
        self._probe_text.set(f"{self.PROBE_STRING}{probe_div}X")

    def set_trigger_type(self, trigger_type: TriggerType):
        trigger_symbol = '/' if trigger_type == TriggerType.RISING_EDGE else '\\'
        self._trigger_text.set(f"{self.TRIGGER_STRING}{trigger_symbol}")

    def update_cursors(self, cursor_data: Cursor_Data) -> None:
        cursor_visible = False
        base_row = len(self.main_labels) + 2  # +2 for status and separator
        for key in cursor_data:
            if cursor_data[key] != '':
                cursor_visible = True
                break
        
        if cursor_visible:
            self.cursor_separator.grid(row=base_row, column=0, sticky='ew', pady=2)
            base_row += 1
        else:
            self.cursor_separator.grid_remove()
        
        for i, key in enumerate(cursor_data):
            if cursor_data[key] != '':
                formatted_value = f"{key}: {cursor_data[key]}"
                self._cursor_text[key].set(formatted_value)
                self.cursor_labels[i].grid(row=base_row + i, column=0, sticky='ew')
            else:
                self.cursor_labels[i].grid_remove()

    def __call__(self, scope_index: int) -> None:
        self.status_label.grid(row=0, column=0, sticky='ew')
        self.status_separator.grid(row=1, column=0, sticky='ew', pady=2)
        for i, label in enumerate(self.main_labels):
            label.grid(row=i+2, column=0, sticky='ew')
        self._vertical_text.set(self.get_vertical_str())
        self._horizontal_text.set(self.get_horizontal_str())
        self._average_text.set(f"{self.AVERAGE_STRING}----")
        self._rms_text.set(f"{self.RMS_STRING}----")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(sticky=tk.N, row=scope_index, column=1, padx=constants.Application.PADDING, pady=constants.Application.PADDING)

    def update_settings(self, new_vertical_setting: float, new_horizontal_setting: float) -> None:
        self._vertical_setting = new_vertical_setting
        self._horizontal_setting = new_horizontal_setting
        self._vertical_text.set(self.get_vertical_str())
        self._horizontal_text.set(self.get_horizontal_str())

    def set_status(self, status_str: str) -> None: self._status_text.set(status_str)

    def enable_cursor_readout(self, cursor_data: Cursor_Data) -> None: 
        self.update_cursors(cursor_data)

    def disable_cursor_readout(self) -> None:
        self.cursor_separator.grid_remove()
        for label in self.cursor_labels:
            label.grid_remove()

    def disable_horizontal_cursor_readout(self) -> None:
        for i in range(0, 3):  # h1, h2, hdelta
            self.cursor_labels[i].grid_remove()

    def disable_vertical_cursor_readout(self) -> None:
        for i in range(3, 7):  # v1, v2, vdelta, 1/vdelta
            self.cursor_labels[i].grid_remove() 