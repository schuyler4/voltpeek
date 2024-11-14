from unittest.mock import MagicMock
from math import sin, pi

from voltpeek.scopes.newt_scope_one import NewtScope_One

class SerialMock(MagicMock):
    def open(self): self.opened = True

    def flush(self):
        pass

    def flushInput(self):
        pass

    def flushOutput(self):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created = True
        self.baudrate = None
        self.port = None
        self.timeout = None
        self._read_index = 0

    def _get_scope_data(self):
        tt = [i*1e-3 for i in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]
        vv = [5*sin(2*pi*100*t) for t in tt]
        vv_adc_in = [(v*(215e3+35.7e3)/(750e3+215e3+35.7e3))+0.5 for v in vv]
        LSB = NewtScope_One.SCOPE_SPECS['voltage_ref']/NewtScope_One.SCOPE_SPECS['resolution']
        return [int(v/LSB) for v in vv_adc_in]

    def read(self):
        continues_buffer = self._get_scope_data()
        quarter_transmit = NewtScope_One.SCOPE_SPECS['memory_depth']//4
        transmit_buffer = []  
        self._read_index += 1