import matplotlib.pyplot as plt
from typing import Optional
from threading import Event

from serial import Serial
from serial.tools import list_ports

from .. import constants

from voltpeek.scopes.scope_base import ScopeBase, SoftwareScopeSpecs

class NewtScope_One(ScopeBase):
    DECODING_SCHEME: str = constants.Serial_Protocol.DECODING_SCHEME
    DATA_START_COMMAND: str = constants.Serial_Protocol.DATA_START_COMMAND 
    DATA_END_COMMAND: str = constants.Serial_Protocol.DATA_END_COMMAND
    DATA_RECIEVE_DELAY: float = constants.Serial_Protocol.DATA_RECIEVE_DELAY
    BUFFER_FLUSH_DELAY: float = constants.Serial_Protocol.BUFFER_FLUSH_DELAY
    PICO_VID: int = 0x2E8A
    POINT_COUNT: int = 20000

    ID = 'NS1'
    SCOPE_SPECS: SoftwareScopeSpecs = {
        'attenuation': {'range_high':0.03568, 'range_low':0.2505},
        'offset': {'range_high':0.515, 'range_low':0.511},
        'resolution': 256,    
        'voltage_ref': 1.0,
        'sample_rate': 62.5e6, 
        'memory_depth': 20000
    }

    LOW_RANGE_THRESHOLD: float = 2

    def __init__(self, baudrate: int=115200, port: Optional[str]=None):
        self.baudrate: int = baudrate
        self.port: Optional[str] = None
        self.error: bool = False
        self._stop: Event = Event()

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
        except Exception as e:
            self.error = True

    def read_glob_data(self) -> str:
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        self._stop.clear()
        codes: list[str] = []
        while len(codes) < self.POINT_COUNT: 
            if self._stop.is_set():
                print('stopped while waiting for data')
                self._stop.clear()
                return []
            new_data = self.serial_port.read(self.serial_port.inWaiting())
            '''
            USED for on data receive debugging.

            if new_data != b'':
                print(new_data) 
            '''
            codes += list(new_data)
        return codes

    def get_scope_trigger_data(self) -> list[int]:
        self.serial_port.write(constants.Serial_Commands.TRIGGER_COMMAND) 
        return self.read_glob_data()

    def get_scope_force_trigger_data(self) -> list[int]:
        self.serial_port.write(constants.Serial_Commands.FORCE_TRIGGER_COMMAND) 
        return self.read_glob_data()

    def set_range(self, full_scale: float) -> None:
        # TODO: Optimize so we only send a flip command when necessary
        if full_scale <= self.LOW_RANGE_THRESHOLD: 
            self.serial_port.write(constants.Serial_Commands.LOW_RANGE_COMMAND)
        else:
            self.serial_port.write(constants.Serial_Commands.HIGH_RANGE_COMMAND)

    def request_low_range(self) -> None: 
        self.serial_port.write(constants.Serial_Commands.LOW_RANGE_COMMAND)

    def request_high_range(self) -> None:
        self.serial_port.write(constants.Serial_Commands.HIGH_RANGE_COMMAND)

    def set_trigger_code(self, trigger_code:int) -> None:
        self.serial_port.write(constants.Serial_Commands.TRIGGER_LEVEL_COMMAND) 
        self.serial_port.write(bytes(str(trigger_code) + '\0', 'utf-8')) 

    def set_clock_div(self, clock_div:int) -> None:
        self.serial_port.write(constants.Serial_Commands.CLOCK_DIV_COMMAND) 
        self.serial_port.write(bytes(str(clock_div) + '\0', 'utf-8')) 

    def set_calibration_offsets(self, calibration_offsets_str:str):
        self.serial_port.write(constants.Serial_Commands.SET_CAL_COMMAND)
        self.serial_port.write(bytes(str(calibration_offsets_str) + '\0', 'utf-8')) 

    def stop(self): self.serial_port.write(constants.Serial_Commands.STOP_COMMAND)

    def read_calibration_offsets(self) -> list[int]:
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        self.serial_port.write(constants.Serial_Commands.READ_CAL_COMMAND)
        offset_bytes: list[str] = []
        while len(offset_bytes) < 4:
            offset_bytes += list(self.serial_port.read(self.serial_port.inWaiting()))
        return offset_bytes

    def stop_trigger(self): 
        self.stop()
        self._stop.set()

    @property
    def stopped(self): return self._stop.is_set()