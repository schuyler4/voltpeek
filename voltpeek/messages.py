class Errors:
    SERIAL_PORT_CONNECTION_ERROR:str = 'Could not connect to scope serial port.'
    SCOPE_DISCONNECTED_ERROR:str = 'No Scope is Connected.'
    INVALID_COMMAND_ERROR:str = 'Invalid Command.'

class Messages:
    SERIAL_PORT_CONNECTION_SUCCESS:str = 'Successfully connected to scope.'

class Prompts:
    PROMPT:str = 'scope:'

class Commands:
    EXIT_COMMAND: str = 'exit'
    FORCE_TRIGGER_COMMAND: str = 'ftrigger'
    TRIGGER_COMMAND: str = 'trigger'
    AUTO_TRIGGER_COMMAND: str = 'atrigger'
    SIMU_TRIGGER_COMMAND: str = 'simutrigger'
    CONNECT_COMMAND: str = 'connect'
    SCALE_COMMAND: str = 'scale'
    FAKE_TRIGGER_COMMAND: str = 'faketrigger'
    TRIGGER_LEVEL_COMMAND: str = 'triglevel'
    TRIGGER_RISING_EDGE_COMMAND: str = 'trigrising'
    TRIGGER_FALLING_EDGE_COMMAND: str = 'trigfalling'
    TOGGLE_CURS: str = 'togglecurs'
    TOGGLE_HCURS: str = 'togglehcurs'
    TOGGLE_VCURS: str = 'togglevcurs'
    ADJUST_CURS: str = 'adjustcurs'
    NEXT_CURS: str = 'nextcurs'
    STOP: str = 'stop'
    
class Mode:
    ADJUST_MODE: str = '-- ADJUST --'
