from math import log10, floor, isnan

import numpy as np

def two_sig_figs(number: float) -> float:
    if isnan(number):
        return float('NaN')
    elif number == 0:
        return number
    else:
        return round(number, -int(floor(log10(abs(number)))) + 1)

def engineering_units(number: float) -> str:
    if abs(number) < 1e9 and abs(number) >= 1e6:
        return str(number/1000000) + 'M'
    elif abs(number) < 1e6 and abs(number) >= 1e3:
        return str(number/1000) + 'k'
    elif abs(number) < 1000 and abs(number) >= 1:
        return str(number)
    elif abs(number) < 1 and abs(number) >= 1e-3:
        # These numbers must be rounded to avoid some strange floating point problems.
        return str(round(number*1000, 9)) + 'm'
    elif abs(number) < 1e-3 and abs(number) >= 1e-6:
        return str(round(number*1000000, 9)) + 'u'
    elif abs(number) < 1e-6 and abs(number) >= 1e-9:
        return str(round(number*1000000000, 9)) + 'n'
    elif number == 0:
        return str(number)
    else:
        return None

#https://gist.github.com/fschwar4/eb462151da065178144d53fe65e8c9fc
def sinc_interpolation(fs: float, x, new_length: int):
    X = np.fft.rfft(x)
    X_padded = np.zeros(new_length // 2 + 1, dtype=complex)
    X_padded[:X.shape[0]] = X
    x_interpolated = np.fft.irfft(X_padded, n=new_length)
    return x_interpolated*(new_length/len(x))