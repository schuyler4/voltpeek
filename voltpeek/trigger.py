from voltpeek import constants
from enum import Enum

def get_trigger_voltage(vertical_setting: float, trigger_level: int) -> float:
    pixel_division:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution:float = vertical_setting/pixel_division
    return float((trigger_level - (constants.Display.SIZE/2))*pixel_resolution)

def trigger_code(trigger_voltage: float, v_ref: float, attenuation: float, offset: float):
    max_input_voltage:float = (v_ref/attenuation)/2   
    return int(((trigger_voltage + max_input_voltage)/(max_input_voltage*2))*
                                        (constants.Trigger.RESOLUTION-1))

class TriggerType(Enum):
    RISING_EDGE = 0 
    FALLING_EDGE = 1

class Trigger:
    def __init__(self) -> None:
        self._trigger_type: TriggerType = TriggerType.RISING_EDGE
        self._trigger_height: int = 0

    @property
    def trigger_height(self) -> int: return self._trigger_height

    @property
    def trigger_type(self) -> int: return self._trigger_type

    @trigger_type.setter
    def trigger_type(self, trigger_type: TriggerType):
        self._trigger_type = trigger_type 
