'''
<h2>Commands:</h2>

<b>exit</b> - Exit the voltpeek program. <br><br>

<b>connect</b> {scope identifier} - Connect voltpeek to an oscilloscope. For example "connect NS1" would be used to connect to the NS1. <br><br>

<b>auto</b> - Auto Trigger the oscilloscope. This will continuously retrigger the scope without a trigger event. <br><br>

<b>normal</b> - Normal Trigger the oscilloscope. This will continuously retrigger the scope, but only when there is a trigger event. <br><br>

<b>single</b> - Single Trigger the oscilloscope. This will capture a single waveform when there is a trigger event. <br><br>

<b>stop</b> - Stop any armed or continues trigger. <br><br>

<b>scale</b> - Enter adjust mode to adjust the horizontal and vertical scales. <br><br>

<b>triglevel</b> - Enter adjust mode to adjust the trigger level. <br><br>

<b>trigrising</b> - Trigger on a rising edge. <br><br>

<b>trigfalling</b> - Trigger on a falling edge. <br><br>

<b>togglecurs</b> - Toggle both the horizontal and vertical cursors. <br><br>

<b>togglehcurs</b> - Toggle just the horizontal cursors. <br><br>

<b>togglevcurs</b> - Toggle just the vertical cursors. <br><br>

<b>nextcurs</b> - Increment the selected cursor. <br><br>

<b>adjustcurs</b> - Enter adjust mode to adjust the selected cursor. <br><br>

<b>probe1</b> - Multiply readings and scales by 1. <br><br>

<b>probe10</b> - Multiply readings and scales by 10. <br><br>

<b>cal</b> - Recalibrate the oscilloscope offsets. Scope input must be disconnected. <br><br>

<b>png</b> - Export a png of the current graticule display. <br><br>
'''

EXIT_COMMAND: str = 'exit'
CONNECT_COMMAND: str = 'connect'
AUTO_TRIGGER_COMMAND: str = 'auto'
NORMAL_TRIGGER_COMMAND: str = 'normal'
SINGLE_TRIGGER_COMMAND: str = 'single'
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
ROLL: str = 'roll'

ADJUST_COMMANDS: tuple[str, str, str] = (SCALE_COMMAND, TRIGGER_LEVEL_COMMAND, ADJUST_CURS)