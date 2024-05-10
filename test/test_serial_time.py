import sys
sys.path.append('..')

import time

# Must be run with the scope connected

from voltpeek.serial_scope import Serial_Scope

serial_scope = Serial_Scope(115200)
serial_scope.init_serial()

start_time = time.time()

data = serial_scope.read_glob_data()

print(time.time() - start_time)