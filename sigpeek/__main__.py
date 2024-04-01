#!/usr/bin/python3
from .interface import User_Interface
from .serial_scope import Serial_Scope

if(__name__ == '__main__'):
    #serial_scope = Serial_Scope(115200, '/dev/ttyACM0')
    #serial_scope.init_serial()
    #trigger_data = serial_scope.get_scope_trigger_data()
    #print(trigger_data[1]) 
    #print(trigger_data[2])
    #print(trigger_data[3])
    user_scope_interface = User_Interface()
    user_scope_interface()
