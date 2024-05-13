import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

fs = 125e6
nyq_rate = fs/2
ripple_dB = 10
width = 20e6/nyq_rate
N, beta = signal.kaiserord(ripple_dB, width)

cutoff_hz = 10e6

hh = signal.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
print(hh)
print(N)

ww, HH = signal.freqz(hh)
ff = (ww*fs)/(2*np.pi)

plt.plot(ff, HH)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.show()
