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

class Keys:
    HORIZONTAL_LEFT:str = 'h'    
    HORIZONTAL_RIGHT:str = 'l'
    VERTICAL_UP:str = 'k' 
    VERTICAL_DOWN:str = 'j' 
    EXIT_COMMAND_MODE = (KeyCodes.CTRL_C, KeyCodes.ESC)

class Vertical:
    LARGE_STEP = 1
    SMALL_STEP = 0.1
    MAX_STEP = 6
