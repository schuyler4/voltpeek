from voltpeek import constants

from scipy.interpolate import interp1d
import numpy as np

def quantize_vertical(vv: list[float], vertical_setting: float) -> list[int]:
    pixel_amplitude: float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution: float = vertical_setting/pixel_amplitude
    return [int(v/pixel_resolution) + int(constants.Display.SIZE/2) for v in vv] 

def resample_horizontal(vv: list[float], horizontal_setting: float, fs: float) -> list[int]:
    tt:list[float] = [i/fs for i in range(0, len(vv))]
    f = interp1d(tt, vv, kind='linear', fill_value=0, bounds_error=False)
    new_T: float = (horizontal_setting)/(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    new_tt: list[float] = [i*new_T for i in range(0, constants.Display.SIZE)]
    new_vv = f(new_tt)
    return new_vv