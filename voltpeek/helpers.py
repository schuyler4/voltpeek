from . import constants
from math import sin, pi

# (1/Fs)*Nsamples >= Thorizontal*10
# Ts = (Thorizontal*10)/Nsamples
# Fs = Nsamples/(Thorizontal*10)
def max_sample_rate(t_horizontal:float): 
    return constants.Display.SIZE/(t_horizontal*constants.Display.GRID_LINE_COUNT)
    
def generate_trigger_vector(t_horizontal:float) -> list[float]:
    FREQUENCY = 500 # Hz
    Fs:float = max_sample_rate(t_horizontal)
    return [sin(2*pi*(i/Fs)*FREQUENCY) for i in range(0, constants.Display.SIZE)]
