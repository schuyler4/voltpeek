import time

from serial import Serial 

from . import messages
from . import constants

class Serial_Scope:
    DECODING_SCHEME:str = constants.Serial_Protocol.DECODING_SCHEME
    DATA_START_COMMAND:str = constants.Serial_Protocol.DATA_START_COMMAND 
    DATA_END_COMMAND:str = constants.Serial_Protocol.DATA_END_COMMAND
    DATA_RECIEVE_DELAY:float = constants.Serial_Protocol.DATA_RECIEVE_DELAY
    BUFFER_FLUSH_DELAY:float = constants.Serial_Protocol.BUFFER_FLUSH_DELAY

    def __init__(self, baudrate, port):
        self.baudrate:int = baudrate
        self.port:str = port
        self.error:bool = False
    
    def init_serial(self):
        try:
            self.serial_port:Serial = Serial()
            self.serial_port.baudrate = self.baudrate
            self.serial_port.port = self.port
            self.serial_port.timeout = self.BUFFER_FLUSH_DELAY
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
        #TODO: Add a timeout error
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
                self.error = True 
        return recieved_data

    def get_scope_specs(self):
        self.serial_port.write(b's')
        time.sleep(self.DATA_RECIEVE_DELAY)
        recieved_specs:list[str] = self.read_serial_data()
        fs = int(''.join(c for c in recieved_specs[0] if c.isdigit()))
        self.specs['fs'] = fs
        print('sample rate: ' + str(self.specs['fs']) + 'S/s')

    #TODO: Get rid of this entire method
    def parse_trigger_data_channel(self, channel_data:str) -> list[int]:
        integer_channel_data:list[int] = []
        for c in channel_data: 
            if(c == '1'):
                integer_channel_data.append(1)
            elif(c == '0'):
                integer_channel_data.append(0)
        return integer_channel_data

    def get_scope_trigger_data(self) -> list[list[int]]:
        self.serial_port.write(b't') 
        time.sleep(self.DATA_RECIEVE_DELAY) 
        recieved_trigger_data:list[str] = self.read_serial_data()
        parsed_trigger_data:list[list[int]] = []
        for channel in recieved_trigger_data:
            parsed_trigger_data.append(self.parse_trigger_data_channel(channel))
        return parsed_trigger_data

    def get_simulated_vector(self) -> list[int]:
        self.serial_port.write(b'S')
        time.sleep(self.DATA_RECIEVE_DELAY)
        recieved_vector:list[int] = [int(x) for x in self.read_serial_data()]
        return recieved_vector

    def get_time_vector(self, channel_data_length:int) -> list[float]:
        sampling_period:float = 1/self.specs['fs']  
        print(sampling_period)
        times:list[float] = []
        for i in range(0, channel_data_length):
            times.append(sampling_period*i)
        return times
