class Errors:
    SERIAL_PORT_CONNECTION_ERROR:str = 'Could not connect to scope serial port.'
    SCOPE_DISCONNECTED_ERROR:str = 'No Scope is Connected.'
    INVALID_COMMAND_ERROR:str = 'Invalid Command.'

class Messages:
    SERIAL_PORT_CONNECTION_SUCCESS:str = 'Successfully connected to scope.'

class Prompts:
    PROMPT:str = 'scope:'

class Commands:
    EXIT_COMMAND:str = 'exit'
    TRIGGER_COMMAND:str = 'trigger'
    SIMU_TRIGGER_COMMAND:str = 'simutrigger'
    CONNECT_COMMAND:str = 'connect'
    SCALE_COMMAND:str = 'scale'
    FAKE_TRIGGER_COMMAND:str = 'faketrigger'
    
class Units:
    VERTICAL_UNIT = 'V/div'
    HORIZONTAL_UNIT = 's/div'

class Mode:
    ADJUST_MODE:str = '-- ADJUST --'
