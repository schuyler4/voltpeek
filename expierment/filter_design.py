import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

fs = 62.5e6
nyq_rate = fs/2
ripple_dB = 10
width = 20e6/nyq_rate
N = 100

cutoff_hz = 10e6

hh = np.array([1/N for _ in range(0, N)]) 
print(hh)
print(N)

ww, HH = signal.freqz(hh)
ff = (ww*fs)/(2*np.pi)

plt.plot(ff, HH)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.show()
