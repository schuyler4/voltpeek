from typing import Optional

from voltpeek import constants

from scipy.interpolate import interp1d
import numpy as np

def inverse_quantize(code: float, resolution: float, voltage_ref: float) -> float:
    return float((voltage_ref/resolution)*code) - 6e-3

def zero(x: float, voltage_ref: float) -> float: return x - 0.5 

def reamplify(x: float, attenuator_range: float) -> float: 
    return x*(1/attenuator_range)

def quantize_vertical(vv: list[float], vertical_setting: float) -> list[int]:
    pixel_amplitude: float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution: float = vertical_setting/pixel_amplitude
    return [int(v/pixel_resolution) + int(constants.Display.SIZE/2) for v in vv] 

def FIR_filter(vv: list[int]) -> list[float]:
    N = 50
    hh = np.array([1/N for _ in range(0, N)]) 
    return list(np.convolve(np.array(vv), hh))

def resample_horizontal(vv: list[float], horizontal_setting: float, fs: float) -> list[int]:
    tt:list[float] = [i/fs for i in range(0, len(vv))]
    f = interp1d(tt, vv, kind='linear', fill_value=0, bounds_error=False)
    new_T: float = (horizontal_setting*2)/(constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    new_tt: list[float] = [i*new_T for i in range(0, constants.Display.SIZE)]
    new_vv = f(new_tt)
    return new_vv

def reconstruct(xx: list[float], specs, vertical_setting: float) -> list[float]:
    attenuation: Optional[float] = None
    offset: Optional[float] = None
    if vertical_setting <= constants.Scale.VERTICALS[constants.Scale.LOW_RANGE_VERTICAL_INDEX]:
        attenuation = specs['attenuation']['range_low']
        offset = specs['offset']['range_low']
    else: 
        attenuation = specs['attenuation']['range_high']
        offset = specs['offset']['range_high']
    # TODO: Make this more functional
    reconstructed_signal: list[float] = []
    for x in xx:
        adc_input = inverse_quantize(x, specs['resolution'], specs['voltage_ref'])
        zeroed = zero(adc_input, specs['voltage_ref'])
        if offset is not None:
            reconstructed_signal.append(reamplify(zeroed, attenuation) - offset)
    return reconstructed_signal     
