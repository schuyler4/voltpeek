from voltpeek import constants

def get_trigger_voltage(vertical_setting:float, trigger_level:int) -> float:
    pixel_amplitude:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution:float = vertical_setting/pixel_amplitude
    return float(trigger_level*pixel_resolution)

def trigger_code(trigger_voltage:float, v_ref:float, attenuation:float, offset:float):
    max_input_voltage:float = (v_ref/attenuation)/2 - offset    
    return int((trigger_voltage/max_input_voltage)*(constants.Trigger.RESOLUTION-1))
