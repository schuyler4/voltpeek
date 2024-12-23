from unittest.mock import MagicMock
from math import sin, pi

from voltpeek.scopes.NS1 import NS1

class SerialMock(MagicMock):
    def open(self): self.opened = True

    def flush(self):
        pass

    def flushInput(self):
        pass

    def flushOutput(self):
        pass

    def inWaiting(self):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created = True
        self.baudrate = None
        self.port = None
        self.timeout = None
        self._read_index = 0

    def _get_scope_data(self): return [300 for _ in range(0, NS1.SCOPE_SPECS['memory_depth'])]

    def read(self, in_waiting):
        continues_buffer = self._get_scope_data()
        quarter_transmit = NS1.SCOPE_SPECS['memory_depth']//4
        transmit_buffer = [continues_buffer[:quarter_transmit], 
                           continues_buffer[quarter_transmit:2*quarter_transmit], 
                           continues_buffer[2*quarter_transmit:3*quarter_transmit],
                           continues_buffer[3*quarter_transmit:]]  
        self._read_index += 1
        if self._read_index == 5:
            self._read_index = 1
        return transmit_buffer[self._read_index-1]