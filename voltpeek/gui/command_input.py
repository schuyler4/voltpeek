from typing import Callable

import tkinter as tk

from voltpeek import constants
from voltpeek import messages
from voltpeek import commands

class CommandInput:
    HEIGHT: int = 1
    WIDTH: int = 65
    BACKGROUND_COLOR: str = 'black'
    ERROR_BACKGROUND_COLOR: str = 'red'
    INSERT_COLOR: str = 'white'
    INSERT_WIDTH: int = 2
    TRIGGER_KEY: str = '<Return>'

    def __init__(self, master:tk.Tk, on_command: Callable[[str], None], width) -> None:
        self.on_command = on_command
        self.master = master
        self.input_text = tk.StringVar()
        self.frame = tk.Frame(
            master,
            highlightbackground='white',
            highlightcolor='white',
            highlightthickness=2,
            bg=self.BACKGROUND_COLOR,
            width=width,
            height=25
        )
        self.frame.pack_propagate(False)
        
        self.input = tk.Entry(
            self.frame,
            textvariable=self.input_text,
            bg=self.BACKGROUND_COLOR, 
            disabledbackground=self.BACKGROUND_COLOR,
            fg=self.INSERT_COLOR,
            insertbackground=self.INSERT_COLOR,
            insertwidth=0,  # Hide default cursor
            bd=0
        )
        self.input.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.input.bind(self.TRIGGER_KEY, self.on_command_enter)
        self.input.bind('<KeyPress>', self.on_key_press)
        self.error:bool = False
        self.command_stack:list[str] = []
        self.command_stack_pointer:int = 0

    def on_command_enter(self, event) -> None:
        command = self.input_text.get()
        if (len(self.command_stack) == 0 or command != self.command_stack[0]) and command != '':
            self.command_stack.insert(0, command)
        self.command_stack_pointer = 0
        self.on_command(command)
        if command in commands.ADJUST_COMMANDS: 
            self.input_text.set(messages.Mode.ADJUST_MODE)
        else: 
            self.input_text.set('')
        if self.error: 
            self.display_error()
    
    def on_key_press(self, event) -> None:
        if self.error: 
            self.error = False
            self.set_command_mode()
   
    def set_focus(self) -> None: self.input.focus_set()
    def set_adjust_mode(self) -> None: self.input.configure(state='disabled')

    def set_command_mode(self) -> None: 
        self.input.configure(state='normal')
        self.input.configure(bg=self.BACKGROUND_COLOR)
        self.input_text.set('')

    def set_command_stack_increment(self) -> None:
        if len(self.command_stack) > 0:
            if self.command_stack_pointer < len(self.command_stack) - 1 and self.input_text.get() != '':
                self.command_stack_pointer += 1
            self.input_text.set(self.command_stack[self.command_stack_pointer])
            self.input.icursor(tk.END)
            if self.command_stack_pointer < len(self.command_stack) - 1 and self.input_text.get() == '':
                self.command_stack_pointer += 1

    def set_command_stack_decrement(self) -> None:
        if self.command_stack_pointer > 0:
            self.command_stack_pointer -= 1
        self.input_text.set(self.command_stack[self.command_stack_pointer])
        self.input.icursor(tk.END)

    def clear_input(self) -> None: self.input_text.set('')

    def set_error(self, message:str) -> None:
        self.error = True
        self.error_message = message

    def display_error(self) -> None: 
        self.input.configure(bg=self.ERROR_BACKGROUND_COLOR)
        self.input_text.set(self.error_message)

    def __call__(self) -> None: 
        self.frame.grid(
            row=1, 
            column=0,
            pady=constants.Application.PADDING, 
            padx=constants.Application.PADDING
        )