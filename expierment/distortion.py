from voltpeek.scopes import NS1

ns1 = NS1(115200, '/dev/ttyACM0')

ns1.connect()
ns1.read_calibration_offsets()
ns1.set_clock_div(1)

full_scale = 5
vv = ns1.get_scope_force_trigger_data(full_scale)
Ts = 1/(62.5e6)

tt = [Ts*i for i in range(0, ns1.SCOPE_SPECS['memory_depth'])]

import matplotlib.pyplot as plt
plt.scatter(tt[:-2], vv[:-2], s=0.1)
plt.show()