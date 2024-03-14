import time

from serial import Serial
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

from . import messages
from .serial_scope import Serial_Scope
from .measurements import measure_period
from .scope_display import open_display

class User_Interface:
    def plot_trigger_data(self, time_vector:list[float], trigger_data:list[list[int]]):
        print(self.measure_period(trigger_data[0]))
        figure = plt.figure()
        axis = figure.add_subplot(211)
        axis.scatter(time_vector, trigger_data[0])
        cursor = Cursor(axis, color='blue', linewidth=2)
        plt.show()

    def __init__(self):
        pass
        #self.scope = Serial_Scope()
               
    def __call__(self):
        while(True):
            user_input = input(messages.Prompts.PROMPT)
            if(user_input == messages.Commands.EXIT_COMMAND):
                break
            elif(user_input == messages.Commands.TRIGGER_COMMAND):
                open_display()
            else:
                print(messages.Errors.INVALID_COMMAND_ERROR) 
