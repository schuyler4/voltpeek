EXIT_COMMAND: str = 'exit'
FORCE_TRIGGER_COMMAND: str = 'ftrigger'
TRIGGER_COMMAND: str = 'trigger'
AUTO_TRIGGER_COMMAND: str = 'atrigger'
NORMAL_TRIGGER_COMMAND: str = 'ntrigger'
SINGLE_TRIGGER_COMMAND: str = 'strigger'
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
PROBE_1: str = 'probe1'
PROBE_10: str = 'probe10'
STOP: str = 'stop'
HELP: str = 'help'

ADJUST_COMMANDS: tuple[str, str, str] = (SCALE_COMMAND, TRIGGER_LEVEL_COMMAND, ADJUST_CURS)

COMMAND_DOCS = {
    EXIT_COMMAND: 'Exit the program.',
    FORCE_TRIGGER_COMMAND: 'Force a single trigger from NewtScope.', 
    AUTO_TRIGGER_COMMAND: '''Run NewtScope in auto trigger mode. That is, get trigger data 
                            at a fixed rate.''', 
    CONNECT_COMMAND: 'Connect to NewtScope.', 
    SCALE_COMMAND: 'Adjust the horizontal and vertical scale.', 
    TRIGGER_LEVEL_COMMAND: 'Adjust the trigger level',
    TRIGGER_RISING_EDGE_COMMAND: 'Set to trigger on a rising edge.', 
    TRIGGER_FALLING_EDGE_COMMAND: 'Set to trigger on a falling edge.', 
    TOGGLE_CURS: 'Toggle the horizontal and vertical cursors', 
    TOGGLE_HCURS: 'Toggle the horizontal cursors.', 
    TOGGLE_VCURS: 'Toggle the vertical cursors.',
    ADJUST_CURS: 'Adjust the selected cursor.', 
    NEXT_CURS: 'Increment the selected cursor.',
    PROBE_1: 'Change to a 1x probe.',
    PROBE_10: 'Change to a 10x probe.', 
    STOP: 'Freeze NewtScope triggering.' 
}
