'''
Commands:

exit - Exit the voltpeek program.

connect {scope identifier} - Connect voltpeek to an oscilloscope. For example "connect NS1" would be used to connect to the NS1.

atrigger - Auto Trigger the oscilloscope. This will continuously retrigger the scope without a trigger event.

ntrigger - Normal Trigger the oscilloscope. This will continuously retrigger the scope, but only when there is a trigger event.

strigger - Single Trigger the oscilloscope. This will capture a single waveform when there is a trigger event.

stop - Stop any armed or continues trigger.

scale - Enter adjust mode to adjust the horizontal and vertical scales.

triglevel - Enter adjust mode to adjust the trigger level.

trigrising - Trigger on a rising edge.

trigfalling - Trigger on a falling edge.

togglecurs - Toggle both the horizontal and vertical cursors.

togglehcurs - Toggle just the horizontal cursors.

togglevcurs - Toggle just the vertical cursors.

nextcurs - Increment the selected cursor.

adjustcurs - Enter adjust mode to adjust the selected cursor.

probe1 - Multiply readings and scales by 1.

probe10 - Multiply readings and scales by 10.

cal - Recalibrate the oscilloscope offsets. Scope input must be disconnected.

png - Export a png of the current graticule display.
'''

EXIT_COMMAND: str = 'exit'
CONNECT_COMMAND: str = 'connect'
AUTO_TRIGGER_COMMAND: str = 'atrigger'
NORMAL_TRIGGER_COMMAND: str = 'ntrigger'
SINGLE_TRIGGER_COMMAND: str = 'strigger'
STOP: str = 'stop'
SCALE_COMMAND: str = 'scale'
TRIGGER_LEVEL_COMMAND: str = 'triglevel'
TRIGGER_RISING_EDGE_COMMAND: str = 'trigrising'
TRIGGER_FALLING_EDGE_COMMAND: str = 'trigfalling'
TOGGLE_CURS: str = 'togglecurs'
TOGGLE_HCURS: str = 'togglehcurs'
TOGGLE_VCURS: str = 'togglevcurs'
NEXT_CURS: str = 'nextcurs'
ADJUST_CURS: str = 'adjustcurs'
PROBE_1: str = 'probe1'
PROBE_10: str = 'probe10'
CAL: str = 'cal'
PNG: str = 'png'

ADJUST_COMMANDS: tuple[str, str, str] = (SCALE_COMMAND, TRIGGER_LEVEL_COMMAND, ADJUST_CURS)