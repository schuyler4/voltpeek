from threading import Event
from ctypes import byref, c_int, c_byte, cdll, sizeof, c_double, create_string_buffer 
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
        self.hdwf = c_int()
        self.sts = c_byte()
        self.handle = c_int()
        self.dwf = cdll.LoadLibrary('libdwf.so')
        self.cAvailable = c_int()
        self.cLost = c_int()
        self.cCorrupted = c_int()
        self.gdSamples1 = (c_double*self.SCOPE_SPECS['memory_depth'])()
        self._stop: Event = Event()
        self._clock_div = 1

    def connect(self):
        self.dwf.FDwfDeviceOpen(c_int(-1), byref(self.hdwf))
        self.dwf.FDwfDeviceAutoConfigureSet(self.hdwf, c_int(0))

    def get_scope_trigger_data(self, full_scale: float):
        self.cAvailable = c_int()
        self.cLost = c_int()
        self.cCorrupted = c_int()
        self.gdSamples1 = (c_double*self.SCOPE_SPECS['memory_depth'])()
        acq_frequency = c_double(self.SCOPE_SPECS['sample_rate']/self._clock_div)
        self.dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(0), c_int(1))
        self.dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, c_int(3)) # record
        sRecord = self.SCOPE_SPECS['memory_depth']/acq_frequency.value
        self.dwf.FDwfAnalogInRecordLengthSet(self.hdwf, c_double(sRecord)) # -1 infinite record length
        self.dwf.FDwfAnalogInTriggerPositionSet(self.hdwf, c_double(-0.5*sRecord)) # -0.25 = trigger at 25%
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(1), c_int(1))
        iSample = 0 
        while True:
            if self._stop.is_set():
                self._stop.clear()
                return []
            if self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(1), byref(self.sts)) != 1:
                print("FDwfAnalogInStatus Error")
                szerr = create_string_buffer(512)
                self.dwf.FDwfGetLastErrorMsg(szerr)
                print(szerr.value)
                break
            self.dwf.FDwfAnalogInStatusRecord(self.hdwf, byref(self.cAvailable), byref(self.cLost), byref(self.cCorrupted))
            iSample += self.cLost.value
            iSample %= self.SCOPE_SPECS['memory_depth']
            iBuffer = 0
            while self.cAvailable.value > 0:
                cSamples = self.cAvailable.value
                if iSample+self.cAvailable.value > self.SCOPE_SPECS['memory_depth']:
                    cSamples = self.SCOPE_SPECS['memory_depth']-iSample
                self.dwf.FDwfAnalogInStatusData2(self.hdwf, c_int(0), byref(self.gdSamples1, sizeof(c_double)*iSample), 
                                                c_int(iBuffer), c_int(cSamples))
                iBuffer += cSamples
                self.cAvailable.value -= cSamples
                iSample += cSamples
                iSample %= self.SCOPE_SPECS['memory_depth']
            if self.sts.value == constants.DwfStateDone.value:
                break
        if iSample != 0:
            self.gdSamples1 = self.gdSamples1[iSample:]+self.gdSamples1[:iSample]
        return np.fromiter(self.gdSamples1, dtype=np.cfloat).real

    def get_scope_force_trigger_data(self, full_scale: float):
        sample_array = (c_double*self.SCOPE_SPECS['memory_depth'])()
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(1), c_int(1))
        while True:
            self.dwf.FDwfAnalogInStatus(self.hdwf, c_int(1), byref(self.sts))
            if self.sts.value == constants.DwfStateDone.value:
                break
        self.dwf.FDwfAnalogInStatusData(self.hdwf, 0, sample_array, self.SCOPE_SPECS['memory_depth'])
        return np.fromiter(sample_array, dtype=np.cfloat).real

    def set_trigger_voltage(self, trigger_voltage: float, full_scale: float) -> None:
        self.dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, c_byte(2))
        self.dwf.FDwfAnalogInTriggerTypeSet(self.hdwf, c_int(0))
        self.dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, c_int(0))
        self.dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, c_double(trigger_voltage))
        self.dwf.FDwfAnalogInTriggerHysteresisSet(self.hdwf, c_double(0.01))
        self.dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, c_int(0)) 
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(1), c_int(0))

    def set_clock_div(self, clock_div: int) -> None:
        self.dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(self.SCOPE_SPECS['sample_rate']/clock_div))
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(1), c_int(1))
        self._clock_div = clock_div
    
    def set_range(self, full_scale: float) -> None:
        self.dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(-1), c_double(full_scale))
        self.dwf.FDwfAnalogInConfigure(self.hdwf, c_int(1), c_int(1))

    def stop_trigger(self):
        self._stop.set()

    def disconnect(self) -> None: 
        self.dwf.FDwfDeviceCloseAll()