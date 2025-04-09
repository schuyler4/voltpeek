from serial import Serial
from serial.tools import list_ports

def find_pico_serial_port():
    ports = list_ports.comports()
    for port in ports:
        if port.vid == 0x2E8A:
            return port.device
    return None

serial_port = Serial()
serial_port.baudrate = 115200
serial_port.port = find_pico_serial_port()
serial_port.timeout = 100 #ms
serial_port.write_timeout = 0 #ms
serial_port.open()

serial_port.write(b'f')

codes = []
code_detected = False

while 1: 
    new_data = serial_port.read(serial_port.inWaiting())
    if new_data != b'':
        code_detected = True
        codes += new_data
        print(codes)
    elif code_detected:
        break

print(len(codes))