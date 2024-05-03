from typing import TypedDict

class AttenuationSettings(TypedDict):
    range_high:float
    range_low:float

class OffsetSettings(TypedDict):
    range_high:float
    range_low:float

class ScopeSpecs(TypedDict):
    attenuation:AttenuationSettings
    offset:OffsetSettings
    resolution:int
    voltage_ref:float
    sample_rate:float
    memory_depth:int

scope_specs:ScopeSpecs = {
    'attenuation': {'range_high':0.008289, 'range_low':0.4976},
    'offset': {'range_high':0.00, 'range_low':0.00},
    'resolution': 256,    
    'voltage_ref': 1.0,
    'sample_rate': 125e6, 
    'memory_depth': 20000
}
