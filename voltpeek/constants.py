class Application:
    NAME:str = 'Volt Peek'
    PADDING:int = 3

class Window:
    BACKGROUND_COLOR:str = 'black'

class Serial_Protocol:
    DATA_START_COMMAND:str = 'START'
    DATA_END_COMMAND:str = 'END'
    DECODING_SCHEME:str = 'utf8'
    DATA_RECIEVE_DELAY:float = 0.1
    BUFFER_FLUSH_DELAY:float = 1

class Display:
    SIZE:int = 500
    BACKGROUND_COLOR:str = 'black'
    GRID_LINE_COUNT:int = 10
    GRID_LINE_COLOR:str = 'grey'
    TRIGGER_LINE_COLOR:str = 'white'
    CURSOR_COLOR = 'red'
    LAYER:str = '-topmost'

class Input:
    HEIGHT:int = 1
    WIDTH:int = 65
    BACKGROUND_COLOR:str = 'black'
    ERROR_BACKGROUND_COLOR:str = 'red'
    INSERT_COLOR:str = 'white'
    INSERT_WIDTH:int = 10
    TRIGGER_KEY:str = '<Return>'

class Readout:
    BACKGROUND_COLOR = 'black'
    BORDER_COLOR = 'white'
    TEXT_COLOR = 'white'
    BORDER_THICKNESS = 2

class Signal:
    COLOR:str = 'blue'

class KeyCodes:
    CTRL_C:int = 54
    ESC:int = 9
    UP_ARROW:int = 111

class Keys:
    HORIZONTAL_LEFT:str = 'h'    
    HORIZONTAL_RIGHT:str = 'l'
    VERTICAL_UP:str = 'k' 
    VERTICAL_DOWN:str = 'j' 
    EXIT_COMMAND_MODE = (KeyCodes.CTRL_C, KeyCodes.ESC)

class Vertical:
    LARGE_STEP = 1
    SMALL_STEP = 0.1
    MAX_STEP = 24

class Serial_Commands:
    TRIGGER_LEVEL_COMMAND:str = b'l'
    TRIGGER_COMMAND:str = b't'
    FORCE_TRIGGER_COMMAND:str = b'f'
    SIMU_TRIGGER_COMMAND:str = b'S'
    LOW_RANGE_COMMAND:str = b'r' 
    HIGH_RANGE_COMMAND:str = b'R'

class Scale:
    DEFAULT_VERTICAL_INDEX:int = 3 
    DEFAULT_HORIZONTAL_INDEX:int = 7
    LOW_RANGE_VERTICAL_INDEX:int = 1
    VERTICALS = (0.5, 1, 2, 5, 10, 12)
    HORIZONTALS = (1e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3, 10e-3, 100e-3, 1)

class Trigger:
    RESOLUTION:int = 256
