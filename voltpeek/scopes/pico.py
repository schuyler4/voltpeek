from typing import Optional

from serial.tools import list_ports

class Pico:
    PICO_VID = 0x2E8A

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

    @classmethod
    def find_scope_ports(cls) -> list[str]: return [port.device for port in list_ports.comports() if port.vid == cls.PICO_VID]