from voltpeek import constants

from scipy.interpolate import interp1d
import numpy as np

def quantize_vertical(vv:list[float], vertical_setting:float) -> list[int]:
    pixel_amplitude:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution:float = vertical_setting/pixel_amplitude
    return [int(v/pixel_resolution) + (constants.Display.SIZE/2) for v in vv] 

def FIR_filter(vv:list[float]) -> list[float]:
    N = 2
    hh = np.array([1/N for _ in range(0, N)]) 
    return list(np.convolve(np.array(vv), hh))

def resample_horizontal(vv:list[int], horizontal_setting:float, fs:float) -> list[int]:
    tt:list[float] = [i/fs for i in range(0, len(vv))]
    f = interp1d(tt, vv, kind='linear', fill_value=0, bounds_error=False)
    new_fs:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)/horizontal_setting
    new_tt:list[float] = [i/new_fs for i in range(0, constants.Display.SIZE)]
    new_vv = f(new_tt)
    return new_vv 
