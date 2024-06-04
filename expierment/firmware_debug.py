import sys
sys.path.append('..')

from voltpeek.serial_scope import Serial_Scope

serial_scope = Serial_Scope(115200)
if serial_scope.pico_connected:
    serial_scope.init_serial()

data = serial_scope.get_scope_force_trigger_data()
print(data)