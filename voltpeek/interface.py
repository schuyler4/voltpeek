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

class User_Interface:
    interface_settings = {
        'vertical': 5, # V/div
        'horizontal':0.001 # s/div 
    }

    #TODO: refactor the below two functions because they are basically the 
    # same code twice
    def _increment_vertical(self) -> None: 
        vertical = self.interface_settings['vertical']
        LARGE_STEP = constants.Vertical.LARGE_STEP
        SMALL_STEP = constants.Vertical.SMALL_STEP
        if(vertical >= LARGE_STEP and vertical < constants.Vertical.MAX_STEP): 
            self.interface_settings['vertical'] += LARGE_STEP
        elif(vertical <= LARGE_STEP and vertical >= SMALL_STEP):
            self.interface_settings['vertical'] += SMALL_STEP
            self.interface_settings['vertical'] = round(self.interface_settings['vertical'],2)

    def _decrement_vertical(self) -> None: 
        vertical = self.interface_settings['vertical']
        LARGE_STEP = constants.Vertical.LARGE_STEP
        SMALL_STEP = constants.Vertical.SMALL_STEP
        if(vertical > LARGE_STEP): self.interface_settings['vertical'] -= LARGE_STEP
        elif(vertical <= LARGE_STEP and vertical > SMALL_STEP):
            self.interface_settings['vertical'] -= SMALL_STEP
            self.interface_settings['vertical'] = round(self.interface_settings['vertical'],2)

    def _increment_horizontal(self) -> None:
        self.interface_settings['horizontal'] *= 2

    def _decrement_horizontal(self) -> None:
        self.interface_settings['horizontal'] /= 2

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
        self.vv = None

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
                elif(event.char == constants.Keys.HORIZONTAL_RIGHT):
                    self._update_scale(self._increment_horizontal)
                elif(event.char == constants.Keys.HORIZONTAL_LEFT):
                    self._update_scale(self._decrement_horizontal)

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
        if(self.vv is not None):
            fs:int = 50000
            v_vertical:float = self.interface_settings['vertical']
            h_horizontal:float = self.interface_settings['horizontal']
            vertical_encode:list[int] = quantize_vertical(self.vv, v_vertical)
            horizontal_encode:list[int] = resample_horizontal(vertical_encode, h_horizontal, fs) 
            print(horizontal_encode)
            self.scope_display.set_vector(horizontal_encode) 

    def get_commands(self): return {
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
        self.scope_display.set_vector(quantize_vertical(vv, v_vertical))

    def fake_trigger(self) -> None: 
        fs:int = 50000
        t_horizontal:float = self.interface_settings['horizontal']
        v_vertical:float = self.interface_settings['vertical']
        self.vv:list[float] = generate_trigger_vector(t_horizontal)
        vertical_encoding:list[int] = quantize_vertical(self.vv, v_vertical)
        horizontal_encoding:list[int] = resample_horizontal(vertical_encoding, t_horizontal, fs)
        self.scope_display.set_vector(quantize_vertical(self.vv, v_vertical)) 

    def __call__(self) -> None:
        self.call_display()
        self.root.mainloop()
