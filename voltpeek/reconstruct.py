from . import constants

def inverse_quantize(code:int, resolution:float, voltage_ref:float) -> float:
    return float((voltage_ref/resolution)*code)

def zero(x:float, voltage_ref:float) -> float: return x - (voltage_ref/2)

def reamplify(x:float, attenuator_range:float) -> float: 
    return x*(1/attenuator_range)

def reconstruct(xx:list[int], specs, vertical_setting:float) -> list[float]:
    attenuation:float = None
    if(vertical_setting <= constants.Scale.VERTICALS[constants.Scale.LOW_RANGE_VERTICAL_INDEX]):
        attenuation = specs['range']['range_low']
    else: 
        attenuation = specs['range']['range_high']

    # TODO: Make this more functional
    reconstructed_signal = []
    for x in xx:
        adc_input = inverse_quantize(x, specs['resolution'], specs['voltage_ref'])
        zeroed = zero(adc_input, specs['voltage_ref'])
        reconstructed_signal.append(reamplify(zeroed, attenuation))
    return reconstructed_signal     
