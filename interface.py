import time

from serial import Serial
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

from . import messages

class Serial_Interface:
    BAUDRATE:int = 115200
    DELAY:float = 1
    DATA_RECIEVE_DELAY:float = 0.1
    PORT:str = '/dev/ttyACM0'
    DECODING_SCHEME:str = 'utf8'
     
    DATA_START_COMMAND:str = 'START'
    DATA_END_COMMAND:str = 'END'
    
    def init_serial(self) -> bool:
        try:
            self.serial_port:Serial = Serial()
            self.serial_port.baudrate = self.BAUDRATE
            self.serial_port.port = self.PORT
            self.serial_port.timeout = self.DELAY
            self.serial_port.open()
            # Delays are required around the serial buffer flush
            time.sleep(self.DELAY)
            self.serial_port.flush()
            time.sleep(self.DELAY)
            print(messages.SERIAL_PORT_CONNECTION_SUCCESS)
            return True
        except:
            print(messages.SERIAL_PORT_CONNECTION_ERROR)
            return False


    def read_serial_data(self) -> list[str]:
        logging_data:bool = False
        recieved_data:list[str] = []
        while True:
            try:
                data_string:str = self.serial_port.readline().decode(self.DECODING_SCHEME)    
                if(self.DATA_START_COMMAND in data_string):
                    logging_data = True
                elif(self.DATA_END_COMMAND in data_string):
                    logging_data = False
                    break
                else:
                    recieved_data.append(data_string)
            except:
                pass 
        return recieved_data


    def get_scope_specs(self):
        self.serial_port.write(b's')
        time.sleep(self.DATA_RECIEVE_DELAY)
        recieved_specs:list[str] = self.read_serial_data()
        fs = int(''.join(c for c in recieved_specs[0] if c.isdigit()))
        self.specs['fs'] = fs
        print('sample rate: ' + str(self.specs['fs']) + 'S/s')


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

   
    def get_time_vector(self, channel_data_length:int) -> list[float]:
        sampling_period:float = 1/self.specs['fs']  
        print(sampling_period)
        times:list[float] = []
        for i in range(0, channel_data_length):
            times.append(sampling_period*i)
        return times
    

    # This is for the logic analyser. The scope will be easier. 
    def plot_trigger_data(self, time_vector:list[float], trigger_data:list[list[int]]):
        '''
        plt.figure(1)
        fig, axs = plt.subplots(len(trigger_data), sharex=True, sharey=True)
        for i, sample_data in enumerate(trigger_data):
            if(len(time_vector) == len(sample_data)): 
                axs[i].scatter(time_vector, sample_data) 
        plt.show()
        '''
        print(self.measure_period(trigger_data[0]))
        figure = plt.figure()
        axis = figure.add_subplot(211)
        axis.scatter(time_vector, trigger_data[0])
        cursor = Cursor(axis, color='blue', linewidth=2)
        plt.show()


    def measure_period(self, trace:list[int]) -> float:
        sampling_period:float = 1/self.specs['fs']
        period_start:bool = False
        period_cycle:bool = False
        measured_period:float = 0
        for sample in trace:
            if(sample and not period_start):
                period_start = True
            elif(not sample and period_start and not period_cycle):
                period_cycle = True 
            elif(sample and period_start and period_cycle):
                return measured_period
            if(period_start):
                measured_period += sampling_period
        return None
               
    
    def __init__(self):
        self.error:bool = False
        self.specs:dict = {'fs':None, 'Resolution':None, 'Ref':None}
        

    def __call__(self):
        self.error = not self.init_serial()
        self.get_scope_specs()
        while(not self.error):
            user_input = input(messages.PROMPT)
            if(user_input == messages.EXIT_COMMAND):
                break
            elif(user_input == messages.TRIGGER_COMMAND):
                trigger_data:list[list[int]] = self.get_scope_trigger_data()
                times = self.get_time_vector(len(trigger_data[0]))
                self.plot_trigger_data(times, trigger_data)
            else:
                print(messages.INVALID_COMMAND_ERROR) 
