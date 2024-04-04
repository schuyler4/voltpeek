def inverse_quantize(code:int, resolution:float, voltage_ref:float) -> float:
    return float((voltage_ref/resolution)*code)

def zero(x:float, voltage_ref:float) -> float: return x - (voltage_ref/2)
def reamplify(x:float, attenuator_range:float) -> float: return x*(1/attenuator_range)

def reconstruct(xx:list[int], specs) -> list[float]:
    pass
