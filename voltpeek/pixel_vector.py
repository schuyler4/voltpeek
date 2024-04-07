from . import constants

def quantize_vertical(vv:list[float], vertical_setting:float) -> list[int]:
    pixel_amplitude:float = (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT)
    pixel_resolution:float = vertical_setting/pixel_amplitude
    return [int(v/pixel_resolution) + constants.Display.SIZE/2 for v in vv] 
