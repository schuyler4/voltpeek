class Errors:
    SERIAL_PORT_CONNECTION_ERROR:str = 'Could not connect to scope serial port.'
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
    
