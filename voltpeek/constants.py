class Application:
    NAME:str = 'Volt Peek'

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
    WIDTH:int = 75
    BACKGROUND_COLOR:str = 'black'
    INSERT_COLOR:str = 'white'
    INSERT_WIDTH:int = 10
    TRIGGER_KEY:str = '<Return>'

class Signal:
    COLOR:str = 'blue'

class Keys:
    HORIZONTAL_LEFT:str = 'h'    
    HORIZONTAL_RIGHT:str = 'l'
    VERTICAL_UP:str = 'k' 
    VERTICAL_DOWN:str = 'j' 
