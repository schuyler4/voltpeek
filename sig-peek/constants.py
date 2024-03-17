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
    GRID_LINE_COLOR:str = 'white'
    
