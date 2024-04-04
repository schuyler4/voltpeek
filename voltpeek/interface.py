from math import sin, pi

from serial import Serial
import tkinter as tk

from . import messages
from . import constants
from .serial_scope import Serial_Scope
from .measurements import measure_period
from .scope_display import Scope_Display
from .command_input import Command_Input

interface_settings = {
    'vertical': 0.25, # V/div
    'horizontal':0.001 # s/div 
}

scope_settings = {
    'sample_rate': 100000000, # S/s
    'memory_depth': 65540 # Points
}

# (1/Fs)*Nsamples >= Thorizontal*10
# Ts = (Thorizontal*10)/Nsamples
# Fs = Nsamples/(Thorizontal*10)
def max_sample_rate(t_horizontal): 
    return constants.Display.SIZE/(t_horizontal*constants.Display.GRID_LINE_COUNT)
    
def generate_trigger_vector() -> list[float]:
    FREQUENCY = 500 # Hz
    Fs:float = max_sample_rate(interface_settings['horizontal'])
    return [sin(2*pi*(i/Fs)*FREQUENCY) for i in range(0, constants.Display.SIZE)]

class User_Interface:
    def __init__(self) -> None:
        self.build_tk_root() 
        self.scope_display:Scope_Display = Scope_Display(self.root, interface_settings)
        self.command_input:Command_Input = Command_Input(self.root, self.process_command)
        self.scope_display()
        self.command_input()

    def build_tk_root(self) -> None:
        self.root:tk.Tk = tk.Tk()
        self.root.title(constants.Application.NAME)
        self.root.attributes(constants.Display.LAYER, True)
        self.root.configure(bg=constants.Window.BACKGROUND_COLOR) 
    
    def process_command(self, command:str) -> None:
        for key in self.commands:
            if(key == command): self.commands[key]()
    
    def call_display(self) -> None:
        self.scope_display()
        self.command_input()

    #TODO: show an error to the user if the scope does not connect
    #TODO: Prevent the app from freezing during connection
    @staticmethod
    def connect_serial_scope() -> None:
        User_Interface.serial_scope = Serial_Scope(115200, '/dev/ttyACM0')
        User_Interface.serial_scope.init_serial()

    #TODO: don't allow this to do anything if the scope is not connected
    # and throw an error
    @staticmethod
    def simu_trigger() -> None:
        scope_specs = {
            'range': {
                'range_high':0.008289,
                'range_low':0.4976,
            },
            'resolution': 256    
            'voltage_ref': 1.0
        }

        xx:list[int] = User_Interface.serial_scope.get_simulated_vector() 
        print(xx)

    def __call__(self) -> None:
        self.call_display()
        self.root.mainloop()

    commands = {
        messages.Commands.EXIT_COMMAND: exit,
        messages.Commands.CONNECT_COMMAND: connect_serial_scope,
        messages.Commands.SIMU_TRIGGER_COMMAND: simu_trigger    
    }
