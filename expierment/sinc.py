import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt

from voltpeek.helpers import sinc_interpolation

fs = 1000
tt = np.linspace(0, 1000)*(1/fs)
xx = np.sin(2*np.pi*250*tt)

Ti = 1/10000

interpolated_xx = sinc_interpolation(fs, xx, 10000)
interpolated_tt = Ti*np.linspace(0, 10000, num=10000)
print(interpolated_tt[interpolated_tt.size-1])

plt.scatter(tt, xx)
plt.plot(interpolated_tt, interpolated_xx)
plt.show()