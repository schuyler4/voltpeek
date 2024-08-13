from ctypes import byref, c_int, c_byte, cdll, c_double  
from sys import path
from os import sep

import numpy as np

from voltpeek.scopes.scope_base import ScopeBase, ScopeSpecs

# TODO: This is not cross platform yet
constants_path = sep + 'usr' + sep + 'share' + sep + 'digilent' + sep + 'waveforms' + sep + 'samples' + sep + 'py'

path.append(constants_path)
import dwfconstants as constants # type: ignore

class AD3(ScopeBase):
    ID: str = 'AD3'
    SCOPE_SPECS: ScopeSpecs = {'sample_rate':125000000, 'memory_depth':4000}  

    def __init__(self):
        self.scope_interface = c_int()
        self.status = c_byte()
        self.driver_interface = cdll.LoadLibrary('libdwf.so')
        self._clock_div: int = 1
        self._trigger_voltage: float = 0.0

    def connect(self):
        self.driver_interface.FDwfDeviceOpen(c_int(-1), byref(self.scope_interface))
        self.driver_interface.FDwfDeviceAutoConfigureSet(self.scope_interface, c_int(0))

    def get_scope_force_trigger_data(self, full_scale: float):
        sample_array = (c_double*self.SCOPE_SPECS['memory_depth'])()
        self.driver_interface.FDwfAnalogInConfigure(self.scope_interface, c_int(1), c_int(1))
        while True:
            self.driver_interface.FDwfAnalogInStatus(self.scope_interface, c_int(1), byref(self.status))
            if self.status.value == constants.DwfStateDone.value:
                break
        self.driver_interface.FDwfAnalogInStatusData(self.scope_interface, 0, sample_array, self.SCOPE_SPECS['memory_depth'])
        return np.fromiter(sample_array, dtype=np.cfloat).real

    def get_scope_trigger_data(self, full_scale: float): 
        self._enable_trigger()
        trigger_data = self.get_scope_force_trigger_data(full_scale)
        self._disable_trigger()
        return trigger_data

    def set_trigger_voltage(self, trigger_voltage: float, full_scale: float) -> None:
        self._trigger_voltage = trigger_voltage

    def _disable_trigger(self):
        self.driver_interface.FDwfAnalogInTriggerSourceSet(self.scope_interface, c_byte(0))
        self.driver_interface.FDwfAnalogInConfigure(self.scope_interface, c_int(1), c_int(0))

    def _enable_trigger(self):
        self.driver_interface.FDwfAnalogInTriggerSourceSet(self.scope_interface, c_byte(2))
        self.driver_interface.FDwfAnalogInTriggerTypeSet(self.scope_interface, c_int(0))
        self.driver_interface.FDwfAnalogInTriggerChannelSet(self.scope_interface, c_int(0))
        self.driver_interface.FDwfAnalogInTriggerLevelSet(self.scope_interface, c_double(self._trigger_voltage))
        self.driver_interface.FDwfAnalogInTriggerHysteresisSet(self.scope_interface, c_double(0.1))
        self.driver_interface.FDwfAnalogInTriggerConditionSet(self.scope_interface, constants.trigcondRisingPositive) 
        self.driver_interface.FDwfAnalogInTriggerPositionSet(self.scope_interface, c_double(0))
        self.driver_interface.FDwfAnalogInConfigure(self.scope_interface, c_int(1), c_int(0))

    def set_clock_div(self, clock_div: int) -> None:
        self.driver_interface.FDwfAnalogInFrequencySet(self.scope_interface, c_double(self.SCOPE_SPECS['sample_rate']/clock_div))
        self.driver_interface.FDwfAnalogInConfigure(self.scope_interface, c_int(1), c_int(1))
        self._clock_div = clock_div
        self.set_trigger_voltage(self._trigger_voltage, 0)
    
    def set_range(self, full_scale: float) -> None:
        self.driver_interface.FDwfAnalogInChannelRangeSet(self.scope_interface, c_int(-1), c_double(full_scale))
        self.driver_interface.FDwfAnalogInConfigure(self.scope_interface, c_int(1), c_int(1))

    def stop(self): pass

    def stop_trigger(self): pass

    def disconnect(self) -> None: self.driver_interface.FDwfDeviceCloseAll()