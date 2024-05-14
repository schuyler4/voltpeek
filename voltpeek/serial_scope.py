from typing import Optional

import time

from serial import Serial
from serial.tools import list_ports

from . import messages
from . import constants

class Serial_Scope:
    DECODING_SCHEME: str = constants.Serial_Protocol.DECODING_SCHEME
    DATA_START_COMMAND: str = constants.Serial_Protocol.DATA_START_COMMAND 
    DATA_END_COMMAND: str = constants.Serial_Protocol.DATA_END_COMMAND
    DATA_RECIEVE_DELAY: float = constants.Serial_Protocol.DATA_RECIEVE_DELAY
    BUFFER_FLUSH_DELAY: float = constants.Serial_Protocol.BUFFER_FLUSH_DELAY
    PICO_VID: int = 0x2E8A
    POINT_COUNT: int = 20000

    def __init__(self, baudrate: int, port: Optional[str]=None):
        self.baudrate: int = baudrate
        self.port: Optional[str] = None
        self.error: bool = False

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

    def init_serial(self) -> None:
        try:
            if self.port is None:
                self.port = self.find_pico_serial_port() 
            # TODO: raise an error if the port stays none
            self.serial_port: Serial = Serial()
            self.serial_port.baudrate = self.baudrate
            self.serial_port.port = self.port
            self.serial_port.timeout = 0
            self.serial_port.open()
            # Delays are required around the serial buffer flush
            time.sleep(self.BUFFER_FLUSH_DELAY)
            self.serial_port.flush()
            time.sleep(self.BUFFER_FLUSH_DELAY)
            print(messages.Messages.SERIAL_PORT_CONNECTION_SUCCESS)
        except Exception as e:
            print(e)
            self.error = True
            print(messages.Errors.SERIAL_PORT_CONNECTION_ERROR)

    def read_serial_data(self) -> list[str]:
        logging_data:bool = False
        recieved_data:list[str] = []
        #TODO: Add a timeout error, maybe
        while True:
            try:
                data_string:str = self.serial_port.readline().decode(self.DECODING_SCHEME)    
                start_command_present = self.DATA_START_COMMAND in data_string
                logging_data = True if start_command_present else logging_data
                logging_data = False if self.DATA_END_COMMAND in data_string else logging_data
                if(logging_data and len(data_string) > 0 and not start_command_present): 
                    recieved_data.append(data_string)
                if not logging_data: break
            except:
                print('data recieve error')
                self.error = True 
        return recieved_data

    def read_glob_data(self) -> str:
        self.serial_port.write(constants.Serial_Commands.FORCE_TRIGGER_COMMAND) 
        codes: list[str] = []
        while(len(codes) < self.POINT_COUNT): 
            codes += list(self.serial_port.read(self.serial_port.inWaiting()))
        return codes

    def is_digits(self, s:str) -> bool: 
        for c in list(s): 
            if(c in '0123456789'): return True 
        return False
        
    def get_digits(self, s:str) -> str:
        return ''.join(list(filter(lambda c: c in '0123456789', list(s)))) 

    # TODO: Refactor these methods that are basically the same
    def get_scope_trigger_data(self) -> list[int]:
        self.serial_port.write(constants.Serial_Commands.TRIGGER_COMMAND) 
        time.sleep(self.DATA_RECIEVE_DELAY) 
        recieved_trigger_data:list[str] = self.read_serial_data()
        print('made it out of loop')
        # TODO: make this more functional
        samples = []
        for sample in recieved_trigger_data:
            if(self.is_digits(sample)): samples.append(int(self.get_digits(sample)))
        return samples

    def get_scope_force_trigger_data(self) -> list[int]:
        self.serial_port.write(constants.Serial_Commands.FORCE_TRIGGER_COMMAND) 
        recieved_trigger_data: list[int] = self.read_glob_data()
        return recieved_trigger_data 

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