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
from .pixel_vector import quantize_vertical, resample_horizontal
from .helpers import generate_trigger_vector

class Mode(Enum):
    COMMAND = 0
    ADJUST_SCALE = 1

class Scale:
    max_vertical_index = len(constants.Scale.VERTICALS) - 1
    max_hor_index = len(constants.Scale.HORIZONTALS) - 1

    def __init__(self):
        self.vertical_index = constants.Scale.DEFAULT_VERTICAL_INDEX 
        self.horizontal_index = constants.Scale.DEFAULT_HORIZONTAL_INDEX

    def increment_vert(self) -> None:
        if(self.vertical_index < self.max_vertical_index): self.vertical_index += 1     

    def decrement_vert(self) -> None:
        if(self.vertical_index > 0): self.vertical_index -= 1

    def increment_hor(self) -> None:
        if(self.horizontal_index < self.max_hor_index): self.horizontal_index += 1

    def decrement_hor(self) -> None:
        if(self.horizontal_index > 0): self.horizontal_index -= 1

    def get_vert(self) -> float:
        return constants.Scale.VERTICALS[self.vertical_index]
    
    def get_hor(self) -> float:
        return constants.Scale.HORIZONTALS[self.horizontal_index]

class User_Interface:
    def __init__(self) -> None:
        self.scale = Scale()
        self.build_tk_root() 
        self.scope_display:Scope_Display = Scope_Display(self.root)
        self.command_input:Command_Input = Command_Input(self.root, self.process_command)
        self.readout:Readout = Readout(self.root, self.scale.get_vert(), self.scale.get_hor())
        self.readout()
        self.scope_display()
        self.command_input()
        self.mode:Mode = Mode.COMMAND
        self.command_input.set_focus()
        self.vv = None
        self.serial_scope_connected:bool = False

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
                    self._update_scale(self.scale.increment_vert)
                elif(event.char == constants.Keys.VERTICAL_DOWN):
                    self._update_scale(self.scale.decrement_vert)
                elif(event.char == constants.Keys.HORIZONTAL_RIGHT):
                    self._update_scale(self.scale.increment_hor)
                elif(event.char == constants.Keys.HORIZONTAL_LEFT):
                    self._update_scale(self.scale.decrement_hor)

    def process_command(self, command:str) -> None:
        for key in self.get_commands():
            if(key == command): 
                self.get_commands()[key]()
                return
        self.command_input.set_error(messages.Errors.INVALID_COMMAND_ERROR)
    
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
        self.readout.update_settings(self.scale.get_vert(), self.scale.get_hor())
        if(self.vv is not None):
            fs:int = 125000000 
            v_vertical:float = self.scale.get_vert()
            h_horizontal:float = self.scale.get_hor()
            vertical_encode:list[int] = quantize_vertical(self.vv, v_vertical)
            horizontal_encode:list[int] = resample_horizontal(vertical_encode, h_horizontal, fs) 
            self.scope_display.set_vector(horizontal_encode) 

    def get_commands(self): return {
            messages.Commands.EXIT_COMMAND: exit,
            messages.Commands.CONNECT_COMMAND: self.connect_serial_scope,
            messages.Commands.SIMU_TRIGGER_COMMAND: self.simu_trigger,    
            messages.Commands.SCALE_COMMAND: self._set_adjust_scale_mode, 
            messages.Commands.FAKE_TRIGGER_COMMAND: self.fake_trigger,
            messages.Commands.TRIGGER_COMMAND: self.trigger
        }
            
    #TODO: show an error to the user if the scope does not connect
    #TODO: Prevent the app from freezing during connection
    def connect_serial_scope(self) -> None:
        self.serial_scope = Serial_Scope(115200, '/dev/ttyACM0')
        self.serial_scope.init_serial()
        self.serial_scope_connected = True

    #TODO: refactor these trigger methods that are basically the same
    def trigger(self) -> None:
        if(self.serial_scope_connected):
            scope_specs = {
                'range': {'range_high':0.008289, 'range_low':0.4976},
                'resolution': 256,    
                'voltage_ref': 1.0
            }
            xx:list[int] = self.serial_scope.get_scope_trigger_data()
            self.vv:list[float] = reconstruct(xx, scope_specs)
            v_vertical:float = self.scale.get_vertical()
            self.scope_display.set_vector(quantize_vertical(self.vv, v_vertical))
        else: self.command_input.set_error(messages.Errors.SCOPE_DISCONNECTED_ERROR)

    def simu_trigger(self) -> None:
        if(self.serial_scope_connected):
            scope_specs = {
                'range': {'range_high':0.008289, 'range_low':0.4976},
                'resolution': 256,    
                'voltage_ref': 1.0
            }
            xx:list[int] = self.serial_scope.get_simulated_vector() 
            self.vv:list[float] = reconstruct(xx, scope_specs)
            v_vertical:float = self.scale.get_vert()
            self.scope_display.set_vector(quantize_vertical(self.vv, v_vertical))
        else: self.command_input.set_error(messages.Errors.SCOPE_DISCONNECTED_ERROR) 

    def fake_trigger(self) -> None: 
        fs:int = 50000
        t_horizontal:float = self.scale.get_hor()
        v_vertical:float = self.scale.get_vert()
        self.vv:list[float] = generate_trigger_vector(t_horizontal)
        vertical_encoding:list[int] = quantize_vertical(self.vv, v_vertical)
        self.scope_display.set_vector(quantize_vertical(self.vv, v_vertical)) 

    def __call__(self) -> None: self.root.mainloop()
