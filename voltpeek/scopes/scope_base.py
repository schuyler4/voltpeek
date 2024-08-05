from abc import ABCMeta, abstractmethod
from typing import TypedDict

class AttenuationSettings(TypedDict):
    range_high:float
    range_low:float

class OffsetSettings(TypedDict):
    range_high:float
    range_low:float

class ScopeSpecs(TypedDict):
    sample_rate:float
    memory_depth:int

class SoftwareScopeSpecs(ScopeSpecs):
    attenuation:AttenuationSettings
    offset:OffsetSettings
    resolution:int
    voltage_ref:float

class ScopeBase(metaclass=ABCMeta):
    @property
    @abstractmethod
    def ID(self) -> str: 
        pass

    @property
    @abstractmethod
    def SCOPE_SPECS(self) -> ScopeSpecs:
        pass

    @abstractmethod
    def get_scope_trigger_data(self):
        pass

    @abstractmethod
    def get_scope_force_trigger_data(self):
        pass

    @abstractmethod
    def set_clock_div(self, clock_div:int) -> None:
        pass