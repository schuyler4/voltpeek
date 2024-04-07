from typing import Callable

import tkinter as tk

from . import constants
from . import messages

class Command_Input:
    def __init__(self, master:tk.Tk, on_command: Callable[[str], None]) -> None:
        self.on_command:Callable[[str], None] = on_command
        self.master:tk.Tk = master
        self.input_text:tk.StringVar = tk.StringVar()
        self.input:tk.Entry = tk.Entry(master, 
            textvariable=self.input_text,
            width=constants.Input.WIDTH, 
            bg=constants.Input.BACKGROUND_COLOR, 
            disabledbackground=constants.Input.BACKGROUND_COLOR,
            fg=constants.Input.INSERT_COLOR, 
            insertbackground=constants.Input.INSERT_COLOR, 
            insertwidth=constants.Input.INSERT_WIDTH)       
        self.input.bind(constants.Input.TRIGGER_KEY, self.on_command_enter)

    def on_command_enter(self, event) -> None:
        command = self.input_text.get()
        self.on_command(command)
        if(command == messages.Commands.SCALE_COMMAND):
            self.input_text.set(messages.Mode.ADJUST_MODE)
        else:
            self.input_text.set('')
   
    def set_focus(self) -> None:
        self.input.focus_set()

    def set_adjust_mode(self) -> None: self.input.configure(state='disabled')

    def set_command_mode(self) -> None: 
        self.input.configure(state='normal')
        self.input_text.set('')

    def __call__(self) -> None: self.input.pack()
