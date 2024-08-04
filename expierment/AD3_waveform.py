import ctypes
import time
from sys import path
from os import sep
import numpy as np

dwf = ctypes.cdll.LoadLibrary('libdwf.so')
hdwf = ctypes.c_int()
sts = ctypes.c_byte()
constants_path = sep + "usr" + sep + "share" + sep + "digilent" + sep + "waveforms" + sep + "samples" + sep + "py"

path.append(constants_path)
import dwfconstants as constants # type: ignore

class AD3:
    def __init__(self):
        self.handle = ctypes.c_int()

    def connect(self):
        dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(hdwf))
        cBufMax = ctypes.c_int()
        dwf.FDwfDeviceAutoConfigureSet(hdwf, ctypes.c_int(0))
        dwf.FDwfAnalogInBufferSizeInfo(hdwf, 0, ctypes.byref(cBufMax))
        dwf.FDwfAnalogInConfigure(hdwf, ctypes.c_int(1), ctypes.c_int(1))
        dwf.FDwfAnalogInFrequencySet(hdwf, ctypes.c_double(20000000.0))
        dwf.FDwfAnalogInBufferSizeSet(hdwf, ctypes.c_int(4000)) 
        dwf.FDwfAnalogInChannelEnableSet(hdwf, ctypes.c_int(-1), ctypes.c_int(1))
        dwf.FDwfAnalogInChannelRangeSet(hdwf, ctypes.c_int(-1), ctypes.c_double(5))
        time.sleep(2)

    def force_trigger(self):
        sample_array = (ctypes.c_double*4000)()
        dwf.FDwfAnalogInConfigure(hdwf, ctypes.c_int(1), ctypes.c_int(1))
        while True:
            dwf.FDwfAnalogInStatus(hdwf, ctypes.c_int(1), ctypes.byref(sts))
            if sts.value == constants.DwfStateDone.value :
                break
        dwf.FDwfAnalogInStatusData(hdwf, 0, sample_array, 4000)
        dwf.FDwfDeviceCloseAll()
        return np.fromiter(sample_array, dtype=np.cfloat)
        
ad3 = AD3()
ad3.connect()
print(ad3.force_trigger())