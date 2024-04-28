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
        self.input.bind('<KeyPress>', self.on_key_press)
        self.error:bool = False
        self.command_stack:list[str] = []
        self.command_stack_pointer:int = 0

    def on_command_enter(self, event) -> None:
        command = self.input_text.get()
        if(len(self.command_stack) == 0 or command != self.command_stack[0]):
            self.command_stack.insert(0, command)
        self.command_stack_pointer = 0
        self.on_command(command)
        if(command == messages.Commands.SCALE_COMMAND 
           or command == messages.Commands.TRIGGER_LEVEL_COMMAND
           or command == messages.Commands.ADJUST_CURS): 
            self.input_text.set(messages.Mode.ADJUST_MODE)
        else: self.input_text.set('')
        if(self.error): self.display_error()
    
    def on_key_press(self, event) -> None:
        if(self.error): 
            self.error = False
            self.set_command_mode()
   
    def set_focus(self) -> None: self.input.focus_set()
    def set_adjust_mode(self) -> None: self.input.configure(state='disabled')

    def set_command_mode(self) -> None: 
        self.input.configure(state='normal')
        self.input.configure(bg=constants.Input.BACKGROUND_COLOR)
        self.input_text.set('')

    def set_command_stack(self) -> None:
        self.input_text.set(self.command_stack[self.command_stack_pointer])
        if(self.command_stack_point < len(self.command_stack) - 1): 
            self.command_stack_pointer += 1

    def clear_input(self) -> None:
        self.input_text.set('')

    def set_error(self, message:str) -> None:
        self.error = True
        self.error_message = message

    def display_error(self) -> None: 
        self.input.configure(bg=constants.Input.ERROR_BACKGROUND_COLOR)
        self.input_text.set(self.error_message)

    def __call__(self) -> None: 
        self.input.grid(row=1, 
            column=0, 
            pady=constants.Application.PADDING, 
            padx=constants.Application.PADDING)
