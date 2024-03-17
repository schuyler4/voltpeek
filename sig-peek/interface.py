import time
from math import sin, pi

from serial import Serial

from . import messages
from . import constants
from .serial_scope import Serial_Scope
from .measurements import measure_period
from .scope_display import Scope_Display_Thread

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
    def __init__(self):
        signal = generate_trigger_vector()
        self.display = Scope_Display_Thread(interface_settings, signal)
               
    def __call__(self):
        while(True):
            user_input = input(messages.Prompts.PROMPT)
            if(user_input == messages.Commands.EXIT_COMMAND):
                exit()    
            elif(user_input == messages.Commands.TRIGGER_COMMAND):
                self.display.start()
            else:
                print(messages.Errors.INVALID_COMMAND_ERROR) 
