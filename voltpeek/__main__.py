#!/usr/bin/python3

from .interface import User_Interface
from .serial_scope import Serial_Scope

if(__name__ == '__main__'):
    #serial_scope = Serial_Scope(115200, '/dev/ttyACM0')
    #serial_scope.init_serial()
    #simulated_vector:list[int] = serial_scope.get_simulated_vector()
    #print(len(simulated_vector))
    #print(simulated_vector)
    user_scope_interface = User_Interface()
    user_scope_interface()
