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
    'attenuation': {'range_high':0.03568, 'range_low':0.2505},
    'offset': {'range_high':0.515, 'range_low':0.511},
    'resolution': 256,    
    'voltage_ref': 1.0,
    'sample_rate': 62.5e6, 
    'memory_depth': 20000
}
