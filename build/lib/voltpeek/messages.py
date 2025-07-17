class Errors:
    SERIAL_PORT_CONNECTION_ERROR:str = 'Could not connect to scope serial port.'
    SCOPE_DISCONNECTED_ERROR:str = 'No Scope is Connected.'
    INVALID_COMMAND_ERROR:str = 'Invalid Command.'

class Messages:
    SERIAL_PORT_CONNECTION_SUCCESS:str = 'Successfully connected to scope.'

class Prompts:
    PROMPT:str = 'scope:'

class Mode:
    ADJUST_MODE: str = '-- ADJUST --'
