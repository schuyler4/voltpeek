from typing import Optional
from threading import Event
from time import sleep

import numpy as np
from serial import Serial
from serial.tools import list_ports

from voltpeek.scopes.scope_base import ScopeBase, SoftwareScopeSpecs

from voltpeek.measurements import average
from voltpeek.helpers import pad_zero, twos_complement_base10_encode

class NS1(ScopeBase):
    PICO_VID: int = 0x2E8A
    FIR_LENGTH = 6

    ID = 'NS1'
    SCOPE_SPECS: SoftwareScopeSpecs = {
        'attenuation': {'range_high':0.0372, 'range_low':0.2185},
        'offset': {'range_high':0, 'range_high_gain':0, 'range_low':0, 'range_low_gain':0},
        'resolution': 256,    
        'voltage_ref': 1.0,
        'sample_rate': 62.5e6, 
        'memory_depth': 16384, 
        'trigger_resolution': 256, 
        'bias': 0.5
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

    LOW_RANGE_THRESHOLD: float = 4
    CAL_DELAY = 0.1
    CAL_BITS = 13

    def __init__(self, baudrate: int=115200, port: Optional[str]=None):
        self.baudrate: int = baudrate
        self.port: Optional[str] = None
        self.error: bool = False
        self._stop: Event = Event()
        self._xx: list[float] = []

    def pico_connected(self) -> bool:
        ports = list_ports.comports()
        for port in ports:
            if port.vid == self.PICO_VID:
                return True
        return False
    
    def find_pico_serial_port(self) -> Optional[str]:
        ports = list_ports.comports()
        for port in ports:
            if port.vid == self.PICO_VID:
                return port.device
        return None

    def connect(self) -> None:
        try:
            if self.port is None:
                self.port = self.find_pico_serial_port() 
            # TODO: raise an error if the port stays none
            self.serial_port: Serial = Serial()
            self.serial_port.baudrate = self.baudrate
            self.serial_port.port = self.port
            self.serial_port.timeout = 0
            self.serial_port.open()
            self.serial_port.flush()
        except Exception as _:
            self.error = True

    def read_glob_data(self):
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        self._stop.clear()
        codes: list[str] = []
        while len(codes) < self.SCOPE_SPECS['memory_depth']: 
            if self._stop.is_set():
                self._stop.clear()
                return None
            new_data = self.serial_port.read(self.serial_port.inWaiting())
            codes += list(new_data)
        if self._stop.is_set():
            self._stop.clear()
        return codes
    
    def _FIR_filter(self, xx: list[int]):
        if len(xx) > 0:
            filtered_signal = np.convolve(xx, np.array([1/self.FIR_LENGTH for _ in range(0, self.FIR_LENGTH)]))
            return filtered_signal[self.FIR_LENGTH-1:len(filtered_signal)]
        else:
            return []

    def _reconstruct(self, xx: list[float], full_scale: float, offset_null: bool=True, force_low_range=False) -> list[float]:
        if full_scale <= self.LOW_RANGE_THRESHOLD or force_low_range:
            attenuation = self.SCOPE_SPECS['attenuation']['range_low']
            if full_scale == 1:
                offset = self.SCOPE_SPECS['offset']['range_low_gain']
            else:
                offset = self.SCOPE_SPECS['offset']['range_low']
        else: 
            attenuation = self.SCOPE_SPECS['attenuation']['range_high']
            if full_scale == 5:
                offset = self.SCOPE_SPECS['offset']['range_high_gain']
            else:
                offset = self.SCOPE_SPECS['offset']['range_high']
        # Adjust for amplification 
        if full_scale == 5 or full_scale == 1:
            attenuation *= 2
        LSB: float = self.SCOPE_SPECS['voltage_ref']/self.SCOPE_SPECS['resolution']
        zeroed_adc_input = np.subtract(np.multiply(np.array(xx), LSB), self.SCOPE_SPECS['bias'])
        if offset is not None and offset_null:
            reconstructed_signal = np.add(np.multiply(zeroed_adc_input, 1/attenuation), offset)
        else:
            reconstructed_signal = np.multiply(zeroed_adc_input, 1/attenuation)
        return reconstructed_signal

    def get_scope_trigger_data(self, full_scale: float) -> list[float]:
        self.serial_port.write(self.TRIGGER_COMMAND) 
        new_codes = self.read_glob_data()
        if new_codes is not None and len(new_codes) == self.SCOPE_SPECS['memory_depth']:
            self._xx = self._reconstruct(self._FIR_filter(new_codes), full_scale)
        return self._xx

    def get_scope_force_trigger_data(self, full_scale: float, offset_null=True) -> list[float]:
        self.serial_port.write(self.FORCE_TRIGGER_COMMAND) 
        new_codes = self.read_glob_data()
        if len(new_codes) > 0:
            self._xx = self._reconstruct(self._FIR_filter(new_codes), full_scale, offset_null=offset_null)
        return self._xx 

    def set_range(self, full_scale: float) -> None:
        # TODO: Optimize so we only send a flip command when necessary
        if full_scale <= self.LOW_RANGE_THRESHOLD: 
            self.serial_port.write(self.LOW_RANGE_COMMAND)
        else:
            self.serial_port.write(self.HIGH_RANGE_COMMAND)

    def _set_high_range(self) -> None: self.serial_port.write(self.HIGH_RANGE_COMMAND)
    def _set_low_range(self) -> None: self.serial_port.write(self.LOW_RANGE_COMMAND)

    def set_amplifier_gain(self, full_scale: float) -> None:
        # TODO: Optimize so we only send a gain command when necessary
        if full_scale == 5 or full_scale == 1:
            self.serial_port.write(self.AMPLIFIER_GAIN_COMMAND)
        else:
            self.serial_port.write(self.AMPLIFIER_UNITY_COMMAND)

    def _set_amplifier_gain_on(self) -> None: self.serial_port.write(self.AMPLIFIER_GAIN_COMMAND)
    def _set_amplifier_gain_off(self) -> None: self.serial_port.write(self.AMPLIFIER_UNITY_COMMAND)

    def set_trigger_voltage(self, trigger_voltage: float, full_scale: float) -> None:
        if full_scale <= self.LOW_RANGE_THRESHOLD:
            attenuation = self.SCOPE_SPECS['attenuation']['range_low']
        else: 
            attenuation = self.SCOPE_SPECS['attenuation']['range_high']
        # TODO: Add error handling for non-compliant trigger voltages
        max_input_voltage: float = (self.SCOPE_SPECS['voltage_ref']/attenuation)/2   
        trigger_code: int = int(((trigger_voltage + max_input_voltage)/(max_input_voltage*2))*(self.SCOPE_SPECS['trigger_resolution']-1))
        self.serial_port.write(self.TRIGGER_LEVEL_COMMAND) 
        self.serial_port.write(bytes(str(trigger_code) + '\0', 'utf-8')) 

    def set_clock_div(self, clock_div:int) -> None:
        # TODO: Check for non-compliant clock divs
        self.serial_port.write(self.CLOCK_DIV_COMMAND) 
        self.serial_port.write(bytes(str(clock_div) + '\0', 'utf-8')) 

    def _encode_calibration_offsets(self) -> str:
        range_high: int = twos_complement_base10_encode(int(self.SCOPE_SPECS['offset']['range_high']*1000), self.CAL_BITS)
        range_high_gain: int = twos_complement_base10_encode(int(self.SCOPE_SPECS['offset']['range_high_gain']*1000), self.CAL_BITS)
        range_low: int = twos_complement_base10_encode(int(self.SCOPE_SPECS['offset']['range_high']*1000), self.CAL_BITS)
        range_low_gain: int = twos_complement_base10_encode(int(self.SCOPE_SPECS['offset']['range_low_gain']*1000), self.CAL_BITS)
        return pad_zero(str(range_high)) + pad_zero(str(range_high_gain)) + pad_zero(str(range_low)) + pad_zero(str(range_low_gain))

    def set_calibration_offsets(self, full_scale:float) -> None:
        self._set_amplifier_gain_off()
        self._set_high_range()
        sleep(self.CAL_DELAY)
        self.SCOPE_SPECS['offset']['range_high'] = -1*average(self.get_scope_force_trigger_data(10, offset_null=False))
        self._set_amplifier_gain_on()
        sleep(self.CAL_DELAY)
        self.SCOPE_SPECS['offset']['range_high_gain'] = -1*average(self.get_scope_force_trigger_data(5, offset_null=False))
        self._set_amplifier_gain_off()
        self._set_low_range()
        sleep(self.CAL_DELAY)
        self.SCOPE_SPECS['offset']['range_low'] = -1*average(self.get_scope_force_trigger_data(2, offset_null=False))
        self._set_amplifier_gain_on()
        sleep(self.CAL_DELAY)
        self.SCOPE_SPECS['offset']['range_low_gain'] = -1*average(self.get_scope_force_trigger_data(1, offset_null=False))
        self._set_amplifier_gain_off()
        self._set_high_range()
        self.serial_port.write(self.SET_CAL_COMMAND)
        self.serial_port.write(bytes(self._encode_calibration_offsets() + '\0', 'utf-8'))
        # Reset to the starting vertical setting
        self.set_amplifier_gain(full_scale)
        self.set_range(full_scale)

    def set_rising_edge_trigger(self) -> None: self.serial_port.write(self.RISING_EDGE_TRIGGER_COMMAND)

    def set_falling_edge_trigger(self) -> None: self.serial_port.write(self.FALLING_EDGE_TRIGGER_COMMAND)

    def stop(self): 
        self.serial_port.write(self.STOP_COMMAND)
        self.serial_port.flush()

    def read_calibration_offsets(self) -> list[int]:
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        self.serial_port.write(self.READ_CAL_COMMAND)
        offset_bytes: list[str] = []
        while len(offset_bytes) < 8:
            offset_bytes += list(self.serial_port.read(self.serial_port.inWaiting()))
        '''
        if self._scope_interface.calibration_ints is not None:
            high_range_offset_int: int = self._scope_interface.calibration_ints[1] << 8 | self._scope_interface.calibration_ints[0]
            low_range_offset_int: int = self._scope_interface.calibration_ints[3] << 8 | self._scope_interface.calibration_ints[2]
            self._scope_interface.scope.SCOPE_SPECS['offset']['range_high'] = high_range_offset_int/10000
            self._scope_interface.scope.SCOPE_SPECS['offset']['range_low'] = low_range_offset_int/1000
        '''
        print(offset_bytes)
        return offset_bytes

    def stop_trigger(self): 
        self.stop()
        self._stop.set()

    @property
    def stopped(self): return self._stop.is_set()

    def disconnect(self) -> None:
        pass