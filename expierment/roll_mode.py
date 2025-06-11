import time

from voltpeek.scopes import NS1

ns1 = NS1(115200, '/dev/ttyACM0')

ns1.connect()
ns1.read_calibration_offsets()
ns1.set_clock_div(1)

samples = []
full_scale = 5
for i in range(0, 1000):
    start = time.time()
    sample = ns1.record_sample(10)
    samples.append(sample)
    end = time.time()
    print(1/(end - start))