import time

from voltpeek.scopes import NS1

ns1 = NS1(115200, '/dev/ttyACM0')

ns1.connect()
ns1.read_calibration_offsets()
ns1.set_clock_div(1)

full_scale = 5
start = time.time()
vv = ns1.get_scope_force_trigger_data(full_scale)
end = time.time()
Ts = 1/(62.5e6)

tt = [Ts*i for i in range(0, ns1.SCOPE_SPECS['memory_depth']-(ns1.FIR_LENGTH-1))]

print(1/(end - start))
import matplotlib.pyplot as plt
plt.scatter(tt[:-1], vv[:-1])
plt.show()