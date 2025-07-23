from typing import Optional
from threading import Event
from time import sleep

from serial import Serial

import numpy as np
from numpy.typing import NDArray

from voltpeek.scopes.scope_base import ScopeBase, SoftwareScopeSpecs
from voltpeek.scopes.pico import Pico

class NS0(ScopeBase, Pico):
    DIGITAL_FILTER = False
    ID = 'NS0'

    SCOPE_SPECS: SoftwareScopeSpecs = {
        'sample_rate':500e3, 
        'memory_depth':16384, 
        'voltage_ref': 3.3, 
        'resolution': 4096
    }

    TRIGGER_LEVEL_COMMAND: bytes = b'l'
    TRIGGER_COMMAND: bytes = b't'
    FORCE_TRIGGER_COMMAND: bytes = b'f'
    STOP_COMMAND: bytes = b'S'
    LOW_RANGE_COMMAND: bytes = b'r' 
    HIGH_RANGE_COMMAND: bytes = b'R'
    AMPLIFIER_GAIN_COMMAND: bytes = b'A'
    AMPLIFIER_UNITY_COMMAND: bytes = b'a'
    CLOCK_DIV_COMMAND: bytes = b'c'
    SET_CAL_COMMAND: bytes = b'C'
    READ_CAL_COMMAND: bytes = b'k'
    RISING_EDGE_TRIGGER_COMMAND: bytes = b'/'
    FALLING_EDGE_TRIGGER_COMMAND: bytes = b'\\'
    RECORD_SAMPLE: bytes = b'o'
    START_RECORD: bytes = b'O'
    ENABLE_SIGNAL_TRIGGER_COMMAND: bytes = b'I'
    DISABLE_SIGNAL_TRIGGER_COMMAND: bytes = b'i'

    def __init__(self, baudrate: int=115200, port: Optional[str]=None):
        self.baudrate = baudrate
        self.port: Optional[str] = port
        self.error: bool = False
        self._stop: Event = Event()
        self._xx: list[float] = []
        self._cal_offset = 0

    def connect(self) -> None:
        try:
            if self.port is None:
                self.port = self.find_pico_serial_port() 
            # TODO: raise an error if the port stays none
            self.serial_port: Serial = Serial(timeout=1)
            self.serial_port.baudrate = self.baudrate
            self.serial_port.port = self.port
            self.serial_port.timeout = 100 #ms
            self.serial_port.open()
            self._purge_serial_buffers()
        except Exception as _:
            print('NS0 connect exception')
            print(_)
            self.error = True

    def read_glob_data(self):
        #self._stop.clear()
        codes: list[str] = []
        while len(codes) < self.SCOPE_SPECS['memory_depth']: 
            if self._stop.is_set():
                self._purge_serial_buffers()
                self._stop.clear()
                return None
            try:
                new_data = self.serial_port.read(self.serial_port.inWaiting())
                if new_data is None:
                    # This is probably dead code
                    return None
                else:
                    codes += list(new_data)
                    sleep(0.0001)
            except (OSError, IOError) as _:
                return None
            except Exception as _:
                return None
        if self._stop.is_set():
            self._purge_serial_buffers()
            self._stop.clear()
            return None
        return codes
    
    def _purge_serial_buffers(self):
        while self.serial_port.in_waiting:
            self.serial_port.read(self.serial_port.inWaiting())
        self.serial_port.reset_input_buffer()
        self.serial_port.reset_output_buffer()

    def get_scope_trigger_data(self):
        pass

    def _reconstruct(self, codes: list[int]) -> NDArray:
        LSB: float = self.SCOPE_SPECS['voltage_ref']/self.SCOPE_SPECS['resolution']
        return np.multiply(np.array(codes), LSB)
    
    def get_scope_force_trigger_data(self, full_scale: float, offset_null=True) -> list[float]:
        self._purge_serial_buffers()
        self.serial_port.write(self.FORCE_TRIGGER_COMMAND) 
        new_codes = self.read_glob_data()
        if new_codes is not None and len(new_codes) == self.SCOPE_SPECS['memory_depth']:
            self._xx = self._reconstruct(new_codes)
        return self._xx 

    def set_clock_div(self, clock_div: int) -> None:
        pass

    def set_trigger_voltage(self, trigger_voltage: float, full_scale: float) -> None:
        pass

    def set_range(self, full_scale) -> None:
        pass

    def set_amplifier_gain(self, full_scale) -> None:
        pass

    def set_rising_edge_trigger(self) -> None:
        pass

    def set_falling_edge_trigger(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def stop_trigger(self) -> None: self._stop.set()