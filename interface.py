import time

from serial import Serial
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

from . import messages
from .serial_scope import Serial_Scope

class User_Interface:
    def plot_trigger_data(self, time_vector:list[float], trigger_data:list[list[int]]):
        print(self.measure_period(trigger_data[0]))
        figure = plt.figure()
        axis = figure.add_subplot(211)
        axis.scatter(time_vector, trigger_data[0])
        cursor = Cursor(axis, color='blue', linewidth=2)
        plt.show()


    def measure_period(self, trace:list[int]) -> float:
        sampling_period:float = 1/self.specs['fs']
        period_start:bool = False
        period_cycle:bool = False
        measured_period:float = 0
        for sample in trace:
            if(sample and not period_start):
                period_start = True
            elif(not sample and period_start and not period_cycle):
                period_cycle = True 
            elif(sample and period_start and period_cycle):
                return measured_period
            if(period_start):
                measured_period += sampling_period
        return None


    def __init__(self):
        self.scope = Serial_Scope()
               
    
    def __call__(self):
        while(not self.scope.error):
            user_input = input(messages.PROMPT)
            if(user_input == messages.EXIT_COMMAND):
                break
            elif(user_input == messages.TRIGGER_COMMAND):
                trigger_data:list[list[int]] = self.scope.get_scope_trigger_data()
                times = self.scope.get_time_vector(len(trigger_data[0]))
                self.plot_trigger_data(times, trigger_data)
            else:
                print(messages.INVALID_COMMAND_ERROR) 
