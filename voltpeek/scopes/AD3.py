import time
import ctypes
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
        self.hdwf = ctypes.c_int()
        self.sts = ctypes.c_byte()
        self.handle = ctypes.c_int()
        self.dwf = ctypes.cdll.LoadLibrary('libdwf.so')

    def connect(self):
        self.dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(self.hdwf))
        cBufMax = ctypes.c_int()
        self.dwf.FDwfDeviceAutoConfigureSet(self.hdwf, ctypes.c_int(0))
        self.dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, 0, ctypes.byref(cBufMax))
        self.dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))
        self.dwf.FDwfAnalogInBufferSizeSet(self.hdwf, ctypes.c_int(self.SCOPE_SPECS['memory_depth'])) 
        # Only channel 1 is supported for now.
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ctypes.c_int(-1), ctypes.c_int(1))

    def get_scope_trigger_data(self):
        pass 

    def get_scope_force_trigger_data(self, full_scale:float):
        sample_array = (ctypes.c_double*self.SCOPE_SPECS['memory_depth'])()
        self.dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))
        while True:
            self.dwf.FDwfAnalogInStatus(self.hdwf, ctypes.c_int(1), ctypes.byref(self.sts))
            if self.sts.value == constants.DwfStateDone.value:
                break
        self.dwf.FDwfAnalogInStatusData(self.hdwf, 0, sample_array, self.SCOPE_SPECS['memory_depth'])
        return np.fromiter(sample_array, dtype=np.cfloat).real

    def set_clock_div(self, clock_div: int) -> None:
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, ctypes.c_double(self.SCOPE_SPECS['sample_rate']/clock_div))
        self.dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))
    
    def set_range(self, full_scale: float) -> None:
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, ctypes.c_int(-1), ctypes.c_double(full_scale))
        self.dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))

    def disconnect(self) -> None: 
        self.dwf.FDwfDeviceCloseAll()