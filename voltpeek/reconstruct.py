from voltpeek import constants

from scipy.interpolate import interp1d

def quantize_vertical(vv: list[float], vertical_setting: float) -> list[int]:
    pixel_amplitude: float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution: float = vertical_setting/pixel_amplitude
    return [int(v/pixel_resolution) + int(constants.Display.SIZE/2) for v in vv] 

def resample_horizontal(vv: list[float], horizontal_setting: float, fs: float, memory_depth: int) -> list[int]:
    tt:list[float] = [i/fs for i in range(0, len(vv))]
    f = interp1d(tt, vv, kind='linear', fill_value=0, bounds_error=False)
    new_T: float = (horizontal_setting)/(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    chop_time: float = (1/fs)*memory_depth - horizontal_setting*constants.Display.GRID_LINE_COUNT
    return f([(i*new_T) + (chop_time/2) for i in range(0, constants.Display.SIZE)])