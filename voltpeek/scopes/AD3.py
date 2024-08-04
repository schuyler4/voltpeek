import time
import ctypes
from sys import path
from os import sep

import numpy as np

from voltpeek.scopes.scope_base import ScopeBase, ScopeSpecs

constants_path = sep + "usr" + sep + "share" + sep + "digilent" + sep + "waveforms" + sep + "samples" + sep + "py"

path.append(constants_path)
import dwfconstants as constants # type: ignore

class AD3(ScopeBase):
    ID: str = 'AD3'
    SCOPE_SPECS: ScopeSpecs = {'sample_rate':125000000, 'memory_depth':32768}  

    def __init__(self):
        self.handle = ctypes.c_int()
        self.hdwf = ctypes.c_int()
        self.sts = constants.c_byte()
        self.dwf = ctypes.cdll.LoadLibrary('libdwf.so')

    def connect(self):
        self.dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(self.hdwf))
        cBufMax = ctypes.c_int()
        self.dwf.FDwfDeviceAutoConfigureSet(self.hdwf, ctypes.c_int(0))
        self.dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, 0, ctypes.byref(cBufMax))
        self.dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, ctypes.c_double(20000000.0))
        self.dwf.FDwfAnalogInBufferSizeSet(self.hdwf, ctypes.c_int(4000)) 
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, ctypes.c_int(-1), ctypes.c_int(1))
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, ctypes.c_int(-1), ctypes.c_double(5))
        time.sleep(2)

    def get_scope_trigger_data(self):
        pass 

    def get_scope_force_trigger_data(self):
        sample_array = (ctypes.c_double*4000)()
        self.dwf.FDwfAnalogInConfigure(self.hdwf, ctypes.c_int(1), ctypes.c_int(1))
        while True:
            self.dwf.FDwfAnalogInStatus(self.hdwf, ctypes.c_int(1), ctypes.byref(self.sts))
            if self.sts.value == constants.DwfStateDone.value:
                break
        self.dwf.FDwfAnalogInStatusData(self.hdwf, 0, sample_array, 4000)
        self.dwf.FDwfDeviceCloseAll()
        return np.fromiter(sample_array, dtype=np.cfloat)

    def set_clock_div(self, clock_div:int) -> None:
        pass