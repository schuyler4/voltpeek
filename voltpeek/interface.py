from typing import Callable
from enum import Enum

import tkinter as tk

from . import messages
from . import constants
from .serial_scope import Serial_Scope
from .measurements import measure_period
from .scope_display import Scope_Display
from .command_input import Command_Input
from .readout import Readout
from .reconstruct import reconstruct
from .helpers import generate_trigger_vector

class Mode(Enum):
    COMMAND = 0
    ADJUST_SCALE = 1

class User_Interface:
    interface_settings = {
        'vertical': 5, # V/div
        'horizontal':0.001 # s/div 
    }

    def _increment_vertical(self) -> None: 
        vertical = self.interface_settings['vertical']
        if(vertical > 1): self.interface_settings['vertical'] += 1
        elif(vertical <= 1 and vertical > 0.1):
            self.interface_settings['vertical'] += 0.1

    def _decrement_vertical(self) -> None: 
        vertical = self.interface_settings['vertical']
        if(vertical > 1): self.interface_settings['vertical'] -= 1
        elif(vertical <= 1 and vertical > 0.1):
            self.interface_settings['vertical'] -= 0.1

    scope_settings = {
        'sample_rate': 100000000, # S/s
        'memory_depth': 65540 # Points
    }

    def __init__(self) -> None:
        self.build_tk_root() 
        self.scope_display:Scope_Display = Scope_Display(self.root, self.interface_settings)
        self.command_input:Command_Input = Command_Input(self.root, self.process_command)
        self.readout:Readout = Readout(self.root, self.interface_settings)
        self.readout()
        self.scope_display()
        self.command_input()
        self.mode:Mode = Mode.COMMAND
        self.command_input.set_focus()

    def build_tk_root(self) -> None:
        self.root:tk.Tk = tk.Tk()
        self.root.title(constants.Application.NAME)
        self.root.attributes(constants.Display.LAYER, True)
        self.root.configure(bg=constants.Window.BACKGROUND_COLOR) 
        self.root.bind('<KeyPress>', self.on_key_press)

    def on_key_press(self, event) -> None:
        if(self.mode == Mode.ADJUST_SCALE):
            if(event.keycode in constants.Keys.EXIT_COMMAND_MODE): self._set_command_mode()
            else:
                if(event.char == constants.Keys.VERTICAL_UP):
                    self._update_scale(self._increment_vertical)    
                elif(event.char == constants.Keys.VERTICAL_DOWN):
                    self._update_scale(self._decrement_vertical)    

    def process_command(self, command:str) -> None:
        for key in self.get_commands():
            if(key == command): self.get_commands()[key]()
    
    def call_display(self) -> None:
        self.scope_display()
        self.command_input()

    def _set_adjust_scale_mode(self) -> None:
        self.mode = Mode.ADJUST_SCALE
        self.command_input.set_adjust_mode()
        self.root.focus_set()

    def _set_command_mode(self) -> None:
        self.mode = Mode.COMMAND
        self.command_input.set_command_mode()
        self.command_input.set_focus()

    def _update_scale(self, arithmatic_fn: Callable[[None], None]) -> None:
        arithmatic_fn()
        self.readout.update_settings(self.interface_settings)
        self.scope_display.update_settings(self.interface_settings)

    def get_commands(self):
        return {
            messages.Commands.EXIT_COMMAND: exit,
            messages.Commands.CONNECT_COMMAND: self.connect_serial_scope,
            messages.Commands.SIMU_TRIGGER_COMMAND: self.simu_trigger,    
            messages.Commands.SCALE_COMMAND: self._set_adjust_scale_mode, 
            messages.Commands.FAKE_TRIGGER_COMMAND: self.fake_trigger
        }
            
    #TODO: show an error to the user if the scope does not connect
    #TODO: Prevent the app from freezing during connection
    def connect_serial_scope(self) -> None:
        self.serial_scope = Serial_Scope(115200, '/dev/ttyACM0')
        self.serial_scope.init_serial()

    #TODO: don't allow this to do anything if the scope is not connected
    # and throw an error
    def simu_trigger(self) -> None:
        scope_specs = {
            'range': {
                'range_high':0.008289,
                'range_low':0.4976,
            },
            'resolution': 256,    
            'voltage_ref': 1.0
        }

        xx:list[int] = self.serial_scope.get_simulated_vector() 
        vv:list[float] = reconstruct(xx, scope_specs)
        print(vv)
        self.scope_display.set_vector(vv)

    def fake_trigger(self) -> None: 
        t_horizontal = self.interface_settings['horizontal']
        self.scope_display.set_vector(generate_trigger_vector(t_horizontal)) 

    def __call__(self) -> None:
        self.call_display()
        self.root.mainloop()
