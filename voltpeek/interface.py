from typing import Callable
from enum import Enum
from threading import Event
from inspect import signature
import logging
import sys

import tkinter as tk

from voltpeek import messages
from voltpeek import constants
from voltpeek import commands
from voltpeek.measurements import average, rms
from voltpeek.scope_interface import ScopeInterface, ScopeAction
from voltpeek.scopes import get_available_scopes

from voltpeek.gui.scope_display import Scope_Display
from voltpeek.gui.command_input import CommandInput
from voltpeek.gui.readout import Readout

from voltpeek.trigger import Trigger, EdgeType, TriggerType
from voltpeek.cursors import Cursors, Cursor_Data
from voltpeek.scale import Scale

from voltpeek.export import export_png, ExportSettings

from voltpeek.scopes.NS1 import NS1

class Mode(Enum):
    COMMAND = 0
    ADJUST_SCALE = 1
    ADJUST_TRIGGER_LEVEL = 2
    ADJUST_CURSORS = 3

class Scope_Status(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    NEUTRAL = 2
    ARMED = 3
    TRIGGERED = 4

class KeyCodes:
    CTRL_C: int = 54
    CTRL_U: int = 37
    CTRL_D: int = 40
    ESC: int = 9
    UP_ARROW: int = 111
    DOWN_ARROW: int = 116
    ENTER: int = 36

class Keys:
    HORIZONTAL_LEFT:str = 'h'    
    HORIZONTAL_RIGHT:str = 'l'
    VERTICAL_UP:str = 'k' 
    VERTICAL_DOWN:str = 'j' 
    EXIT_COMMAND_MODE = (KeyCodes.CTRL_C, KeyCodes.ESC)

class Event(Enum):
    CONNECT = 0
    SINGLE_TRIGGER = 1
    AUTO_TRIGGER = 2
    NORMAL_TRIGGER = 3
    FORCE_TRIGGER = 4
    STOP = 5
    CHANGE_SCALE = 6
    SET_TRIGGER_LEVEL = 7
    EXIT = 8
    READ_CAL_OFFSETS = 9
    SET_CAL_OFFSETS = 10
    SET_RANGE = 11
    SET_RISING_EDGE_TRIGGER = 12
    SET_FALLING_EDGE_TRIGGER = 13
    SET_AMPLIFIER_GAIN = 14
    RECORD_SAMPLE = 15
    ENABLE_SIGNAL_TRIGGER = 16
    DISABLE_SIGNAL_TRIGGER = 17
    START_RECORD = 18

class UserInterface:
    INVALID_SCOPE_ERROR = 'The scope identifier entered is not supported.'
    SCOPE_NOT_CONNECTED_ERROR = 'The scope is not connected.'
    IMAGE_PLOT_ERROR = 'Cannot plot image. There is no signal displayed.'

    def __init__(self, debug=False) -> None:
        self.debug = debug
        logging.basicConfig(stream=sys.stdout,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
        
        self._build_tk_root()

        self.scale: Scale = Scale()
        self._last_fs = self.scale.fs
        self.scope_trigger: Trigger = Trigger()
        self.cursors: Cursors = Cursors(self._display_size)

        self.scope_display: Scope_Display = Scope_Display(self.root, self.cursors, self._display_size)
        self.command_input: CommandInput = CommandInput(self.root, self.process_command, self._display_size)
        # Readouts are not created until the scopes are connected
        self._readout_frame: tk.Frame = tk.Frame(self.root, bg=constants.Window.BACKGROUND_COLOR)
        self._readout_frame.grid(sticky=tk.N, row=0, column=1, padx=constants.Application.PADDING, pady=constants.Application.PADDING)
        self._readouts: list[Readout] = []

        self.scope_display()
        self.command_input()

        self.mode: Mode = Mode.COMMAND
        self.command_input.set_focus()
        self.serial_scope_connected: bool = False
        self.scope_status = Scope_Status.DISCONNECTED

        self._start_event_queue: list[list[Event]] = []
        self._end_event_queue: list[list[Event]] = []

        self._connect_initiated: bool = False
        self._record_running: bool = False
        self._calibration: bool = False
        self._triggered: bool = False
        self._calibration_step: int = 0

        self._scope_interfaces: list[ScopeInterface] = []

    def _build_tk_root(self) -> None:
        self.root:tk.Tk = tk.Tk()
        self.root.title(__name__.split('.')[0])
        self.root.configure(bg=constants.Window.BACKGROUND_COLOR) 
        self.root.tk.call('tk', 'scaling', 1)
        self.root.after(1, self.check_state)
        self.root.bind('<KeyPress>', self.on_key_press)
        # set the initial graticule size based on the users display
        self._display_size: int = int(0.75*min(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

    def check_state(self):
        if self._connect_initiated:
            for i, scope_interface in enumerate(self._scope_interfaces):
                if scope_interface.disconnected_error:
                    self.command_input.set_error(self.SCOPE_NOT_CONNECTED_ERROR)
                    self.command_input.display_error()
                    scope_interface.clear_disconnected_error()
                    self._connect_initiated = False
                    self._start_event_queue[i] = []
                    self._end_event_queue[i] = []
                else:
                    # The end events must go first otherwise the start events will always have priority.
                    if scope_interface.data_available and len(self._end_event_queue[i]) > 0:
                        if self.debug:
                            logging.info(f'end event: {self._end_event_queue[i][0].name}, scope index: {i}')
                        if self._end_event_queue[i][0] == Event.CONNECT:
                            self._finish_connect(i)
                        if self._end_event_queue[i][0] == Event.AUTO_TRIGGER:
                            self._finish_auto_trigger_cycle(i)
                        if self._end_event_queue[i][0] == Event.NORMAL_TRIGGER:
                            self._finish_normal_trigger_cycle(i)
                        if self._end_event_queue[i][0] == Event.SINGLE_TRIGGER:
                            self._finish_single_trigger(i)
                        if self._end_event_queue[i][0] == Event.CHANGE_SCALE:
                            self._finish_change_scale(i)
                        if self._end_event_queue[i][0] == Event.SET_RISING_EDGE_TRIGGER:
                            self._finish_set_rising_edge_trigger()
                        if self._end_event_queue[i][0] == Event.SET_FALLING_EDGE_TRIGGER:
                            self._finish_set_falling_edge_trigger()
                        if self._end_event_queue[i][0] == Event.RECORD_SAMPLE:
                            self._finish_record_sample(i)
                        self._end_event_queue[i].pop(0)
                    if scope_interface.data_available and len(self._start_event_queue[i]) > 0:
                        if self.debug:
                            logging.info(f'start event: {self._start_event_queue[i][0].name}, scope index: {i}')
                        if self._start_event_queue[i][0] == Event.CONNECT:
                            self._start_connect(i)
                            self._end_event_queue[i].append(Event.CONNECT)
                        if self._start_event_queue[i][0] == Event.SINGLE_TRIGGER:
                            self._start_single_trigger(i)
                            self._end_event_queue[i].append(Event.SINGLE_TRIGGER)
                        if self._start_event_queue[i][0] == Event.AUTO_TRIGGER:
                            self._start_auto_trigger_cycle(i)
                            self._end_event_queue[i].append(Event.AUTO_TRIGGER)
                        if self._start_event_queue[i][0] == Event.NORMAL_TRIGGER:
                            self._start_normal_trigger_cycle(i)
                            self._end_event_queue[i].append(Event.NORMAL_TRIGGER)
                        if self._start_event_queue[i][0] == Event.CHANGE_SCALE:
                            self._start_change_scale(i)
                            self._end_event_queue[i].append(Event.CHANGE_SCALE)
                        if self._start_event_queue[i][0] == Event.SET_TRIGGER_LEVEL:
                            self._start_set_trigger_level(i)
                        if self._start_event_queue[i][0] == Event.READ_CAL_OFFSETS:
                            self._start_read_cal_offsets(i)
                        if self._start_event_queue[i][0] == Event.SET_CAL_OFFSETS:
                            self._start_set_calibration(i)
                        if self._start_event_queue[i][0] == Event.SET_RANGE:
                            self._start_set_range(i)  
                        if self._start_event_queue[i][0] == Event.SET_AMPLIFIER_GAIN:
                            self._start_set_amplifier_gain(i)
                        if self._start_event_queue[i][0] == Event.SET_RISING_EDGE_TRIGGER:
                            self._start_set_rising_edge_trigger(i)
                            self._end_event_queue[i].append(Event.SET_RISING_EDGE_TRIGGER)
                        if self._start_event_queue[i][0] == Event.SET_FALLING_EDGE_TRIGGER:
                            self._start_set_falling_edge_trigger(i)
                            self._end_event_queue[i].append(Event.SET_FALLING_EDGE_TRIGGER)
                        if self._start_event_queue[i][0] == Event.RECORD_SAMPLE:
                            self._start_record_sample(i)
                            self._end_event_queue[i].append(Event.RECORD_SAMPLE)
                        if self._start_event_queue[i][0] == Event.ENABLE_SIGNAL_TRIGGER:
                            self._start_enable_signal_trigger(i)
                        if self._start_event_queue[i][0] == Event.DISABLE_SIGNAL_TRIGGER:
                            self._start_disable_signal_trigger(i)
                        if self._start_event_queue[i][0] == Event.START_RECORD:
                            pass
                        self._start_event_queue[i].pop(0)
        self.root.after(1, self.check_state)

    # TODO: This all needs to be refactored
    def on_key_press(self, event) -> None:
        if self.mode == Mode.ADJUST_SCALE or self.mode == Mode.ADJUST_TRIGGER_LEVEL or self.mode == Mode.ADJUST_CURSORS:
            if (event.keysym == 'Escape') or (event.state & 0x4 and event.keysym == 'c'): 
                if self.mode == Mode.ADJUST_TRIGGER_LEVEL: 
                    self._set_trigger_level()
                self._set_command_mode()
        if self.mode == Mode.ADJUST_SCALE:
            if event.char == Keys.VERTICAL_UP:
                self._update_scale_vert(self.scale.increment_vert)
            elif event.char == Keys.VERTICAL_DOWN:
                self._update_scale_vert(self.scale.decrement_vert)
            elif event.char == Keys.HORIZONTAL_RIGHT:
                self._set_update_scale(self.scale.increment_hor)
            elif event.char == Keys.HORIZONTAL_LEFT:
                self._set_update_scale(self.scale.decrement_hor)
        elif self.mode == Mode.ADJUST_TRIGGER_LEVEL:
            if event.state & 0x4:
                if event.keysym == 'u':
                    self.scope_display.increment_trigger_level_course()
                elif event.keysym == 'd':
                    self.scope_display.decrement_trigger_level_course()
            else:
                if event.char == Keys.VERTICAL_UP:
                    self.scope_display.increment_trigger_level_fine()
                elif event.char == Keys.VERTICAL_DOWN:
                    self.scope_display.decrement_trigger_level_fine()
        elif self.mode == Mode.ADJUST_CURSORS:
            if event.state & 0x4:
                if event.keysym == 'u':
                    self._update_cursor(self.cursors.decrement_hor_course)
                elif event.keysym == 'd':
                    self._update_cursor(self.cursors.increment_hor_course)
            else:
                if event.char == Keys.VERTICAL_UP:
                    self._update_cursor(self.cursors.decrement_hor_fine)
                elif event.char == Keys.VERTICAL_DOWN:
                    self._update_cursor(self.cursors.increment_hor_fine)
                elif event.char == Keys.HORIZONTAL_RIGHT:
                    self._update_cursor(self.cursors.increment_vert_fine)
                elif event.char == Keys.HORIZONTAL_LEFT:
                    self._update_cursor(self.cursors.decrement_vert_fine)
                elif event.keysym == 'less':
                    self._update_cursor(self.cursors.decrement_vert_course)
                elif event.keysym == 'greater':
                    self._update_cursor(self.cursors.increment_vert_course)
        elif self.mode == Mode.COMMAND:
            if event.keycode == KeyCodes.UP_ARROW:
                self.command_input.set_command_stack_increment()
            elif event.keycode == KeyCodes.DOWN_ARROW:
                self.command_input.set_command_stack_decrement()

    def get_commands(self): 
        return {
            commands.EXIT: lambda: exit(),
            commands.CONNECT: lambda identifier: self._connect(identifier),
            commands.SCALE: self._set_adjust_scale_mode, 
            commands.TRIGGER_LEVEL: self._set_adjust_trigger_level_mode,  
            commands.TOGGLE_CURS: self.toggle_cursors, 
            commands.TOGGLE_HCURS: self.toggle_horizontal_cursors, 
            commands.TOGGLE_VCURS: self.toggle_vertical_cursors,
            commands.NEXT_CURS: self.next_cursor, 
            commands.ADJUST_CURS: self._set_adjust_cursor_mode, 
            commands.AUTO_TRIGGER: self._on_auto_trigger_command, 
            commands.NORMAL_TRIGGER: self._on_normal_trigger_command,
            commands.SINGLE_TRIGGER: self._on_single_trigger_command,
            commands.STOP: self._stop_trigger,
            commands.TRIGGER_RISING_EDGE: self._on_trigger_rising_edge_command,
            commands.TRIGGER_FALLING_EDGE: self._on_trigger_falling_edge_command,
            commands.PROBE_1: lambda: self._set_probe(1),
            commands.PROBE_10: lambda: self._set_probe(10),
            commands.CAL: self._on_set_cal_offsets_command,
            commands.PNG: lambda filename: self._run_png_export(filename),
            'record': self._on_record_command
        }

    def process_command(self, command: str) -> None:
        argument = None
        if ' ' in command:
            argument = command.split(' ')[1]
            command = command.split(' ')[0]
        for key in self.get_commands():
            if key == command: 
                sig = signature(self.get_commands()[key])
                if len(sig.parameters) > 0 and argument is not None:
                    self.get_commands()[key](argument)
                    return
                elif argument is None:
                    try:
                        self.get_commands()[key]()
                        return
                    except Exception as _:
                        break
        self.command_input.set_error(messages.Errors.INVALID_COMMAND_ERROR)
    
    ##### START EVENTS #####


    '''
    EVENT: CONNECT
    '''

    def _start_connect(self, scope_index: int) -> None:
        self.scope_status = Scope_Status.CONNECTING
        self._update_scope_status()
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.CONNECT)
        self._scope_interfaces[scope_index].run()

    def _finish_connect(self, scope_index: int) -> None:
        self.scope_status = Scope_Status.NEUTRAL
        self.scale.update_sample_rate(self._scope_interfaces[0].scope.SCOPE_SPECS['sample_rate'], 
                                      self._scope_interfaces[0].scope.SCOPE_SPECS['memory_depth'])
        self._start_event_queue[scope_index].append(Event.CHANGE_SCALE)
        self._start_event_queue[scope_index].append(Event.SET_RISING_EDGE_TRIGGER)
        self._start_event_queue[scope_index].append(Event.SET_TRIGGER_LEVEL)
        self._update_scope_status()
    
    '''
    EVENT: SET RANGE
    '''

    def _start_set_range(self, scope_index: int) -> None:
        for readout in self._readouts:
            readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
        self._scope_interfaces[scope_index].set_full_scale(self.scale.vert*(self.scale.GRID_COUNT/2))
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.SET_RANGE)
        self._scope_interfaces[scope_index].run()

    '''
    EVENT: SET AMPLIFIER GAIN
    '''

    def _start_set_amplifier_gain(self, scope_index: int) -> None:
        for readout in self._readouts:
            readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
        self._scope_interfaces[scope_index].set_full_scale(self.scale.vert*(self.scale.GRID_COUNT/2))
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.SET_AMPLIFIER_GAIN)
        self._scope_interfaces[scope_index].run()

    '''
    EVENT: CHANGE SCALE
    '''

    def _start_change_scale(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_value(self.scale.clock_div)
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.SET_CLOCK_DIV)
        self._scope_interfaces[scope_index].run()
        
    def _finish_change_scale(self, scope_index: int) -> None:
        for readout in self._readouts:
            readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
            readout.set_fs(self.scale.fs)
        if self._scope_interfaces[0].xx is not None and len(self._scope_interfaces[0].xx) > 0:
            fir_length = self._scope_interfaces[0].scope.FIR_LENGTH if self._scope_interfaces[0].scope.DIGITAL_FILTER else None
            self.scope_display.resample_vector(self.scale.hor, self.scale.vert, self._last_fs, 
                                               self._scope_interfaces[0].scope.SCOPE_SPECS['memory_depth'], 
                                               self.scope_trigger.trigger_type, self._triggered,
                                               scope_index, FIR_length=fir_length)

    '''
    EVENT: READ CAL OFFSET
    '''

    def _start_read_cal_offsets(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.READ_CAL_OFFSETS)
        self._scope_interfaces[scope_index].run()

    '''
    EVENT: SET TRIGGER LEVEL
    '''

    def _start_set_trigger_level(self, scope_index: int) -> None:
        for i, scope_interface in enumerate(self._scope_interfaces):
            if i == scope_index:
                scope_interface.set_value(self.scope_display.get_trigger_voltage(self.scale.vert))
                scope_interface.set_scope_action(ScopeAction.SET_TRIGGER_LEVEL)
                scope_interface.run()

    '''
    EVENT: SET RISING EDGE TRIGGER
    '''

    def _start_set_rising_edge_trigger(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.SET_RISING_EDGE_TRIGGER)
        self._scope_interfaces[scope_index].run()
        

    def _finish_set_rising_edge_trigger(self) -> None:
        self.scope_trigger.edge_type = EdgeType.RISING_EDGE
        for readout in self._readouts:
            readout.set_trigger_type(self.scope_trigger.edge_type)

    '''
    EVENT: SET FALLING EDGE TRIGGER
    '''

    def _start_set_falling_edge_trigger(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.SET_FALLING_EDGE_TRIGGER)
        self._scope_interfaces[scope_index].run()

    def _finish_set_falling_edge_trigger(self) -> None:
        self.scope_trigger.edge_type = EdgeType.FALLING_EDGE
        for readout in self._readouts:
            readout.set_trigger_type(self.scope_trigger.edge_type)

    '''
    EVENT: AUTO TRIGGER
    '''

    def _start_auto_trigger_cycle(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.FORCE_TRIGGER)
        self._scope_interfaces[scope_index].fs = self.scale.fs
        self._last_fs = self.scale.fs
        self._scope_interfaces[scope_index].run()

    def _finish_auto_trigger_cycle(self, scope_index: int) -> None:
        self._triggered = False
        self.display_signal(self._scope_interfaces[scope_index].xx, self._triggered, scope_index)
        if self.scope_trigger.trigger_type == TriggerType.AUTO:
            self._start_event_queue[scope_index].append(Event.AUTO_TRIGGER)

    '''
    EVENT: NORMAL TRIGGER
    '''

    def _start_normal_trigger_cycle(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.TRIGGER)
        self._scope_interfaces[scope_index].fs = self.scale.fs
        self._last_fs = self.scale.fs
        self._scope_interfaces[scope_index].run()

    def _finish_normal_trigger_cycle(self, scope_index: int) -> None:
        if len(self._scope_interfaces[scope_index].xx) > 0: 
            self._triggered = True
            self.display_signal(self._scope_interfaces[scope_index].xx, self._triggered, scope_index)
        if self.scope_trigger._trigger_type == TriggerType.NORMAL:
            for start_event_queue in self._start_event_queue:
                # We don't want to over schedule
                if len(start_event_queue) == 0 or start_event_queue[len(start_event_queue) - 1] != Event.NORMAL_TRIGGER:
                    start_event_queue.append(Event.NORMAL_TRIGGER)

    '''
    EVENT: SINGLE TRIGGER
    '''

    def _start_single_trigger(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.TRIGGER)
        self._scope_interfaces[scope_index].fs = self.scale.fs
        self._last_fs = self.scale.fs
        self._scope_interfaces[scope_index].run()

    def _finish_single_trigger(self, scope_index: int) -> None:
        if len(self._scope_interfaces[scope_index].xx) > 0:
            self._triggered = True
            self.display_signal(self._scope_interfaces[scope_index].xx, self._triggered, scope_index)

    '''
    EVENT: RECORD SAMPLE
    '''

    def _start_record_sample(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.RECORD_SAMPLE)
        self._scope_interfaces[scope_index].run()
        self._record_running = True

    def _finish_record_sample(self, scope_index: int) -> None:
        self.scope_display.record = self._scope_interfaces[scope_index]._record
        self.scope_display.resample_record(self.scale.vert)
        if self._record_running:
            self._start_event_queue[scope_index].append(Event.RECORD_SAMPLE)

    '''
    EVENT: READ CAL OFFSETS
    '''

    def _start_set_calibration(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_value(self.scale.vert)
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.SET_CAL_OFFSETS)
        self._scope_interfaces[scope_index].run()

    '''
    EVENT: ENABLE SIGNAL TRIGGER
    '''

    def _start_enable_signal_trigger(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.ENABLE_SIGNAL_TRIGGER)
        self._scope_interfaces[scope_index].run()

    '''
    EVENT: DISABLE SIGNAL TRIGGER   
    '''

    def _start_disable_signal_trigger(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.DISABLE_SIGNAL_TRIGGER)
        self._scope_interfaces[scope_index].run()

    '''
    EVENT: START RECORD
    '''

    def _start_record(self, scope_index: int) -> None:
        self._scope_interfaces[scope_index].set_scope_action(ScopeAction.START_RECORD)
        self._scope_interfaces[scope_index].run()

    ##### END EVENTS #####

    def _connect(self, identifier: str):
        for scope in get_available_scopes():
            if list(scope.keys())[0] == identifier:
                if len(scope[identifier].find_scope_ports()) > 0:
                    for i, connected_device in enumerate(scope[identifier].find_scope_ports()):
                        self._scope_interfaces.append(ScopeInterface(scope[identifier], device=connected_device))
                        self._start_event_queue.append([])
                        self._end_event_queue.append([])
                        self._readouts.append(Readout(self._readout_frame, self.scale.vert, self.scale.hor))
                        self._readouts[len(self._readouts)-1](i)
                    self.scope_display.init_vectors(len(self._scope_interfaces))
                    self._connect_initiated = True
                    for scope_event_queue in self._start_event_queue:
                        scope_event_queue.append(Event.CONNECT)
                        scope_event_queue.append(Event.SET_RANGE)
                        scope_event_queue.append(Event.SET_AMPLIFIER_GAIN)
                    for i, scope_interface in enumerate(self._scope_interfaces):
                        if isinstance(scope_interface.scope, NS1):
                            self._start_event_queue[i].append(Event.READ_CAL_OFFSETS)
                    self._set_update_scale(None)
                    self._update_scope_status()
                    self._update_scope_probe()
                else:
                    self.command_input.set_error(self.SCOPE_NOT_CONNECTED_ERROR)
                return
        self.command_input.set_error(self.INVALID_SCOPE_ERROR)

    def _pause_trigger(self):
        self._trigger_rearm: TriggerType = TriggerType.NONE
        if self.scope_trigger.trigger_type == TriggerType.NORMAL or self.scope_trigger.trigger_type == TriggerType.SINGLE:
            self._trigger_rearm = self.scope_trigger.trigger_type
            self._stop_trigger()

    def _resume_trigger(self, start_event_queue: list[Event]):
        if self._trigger_rearm == TriggerType.NORMAL:
            start_event_queue.append(Event.NORMAL_TRIGGER)
            self.scope_trigger.trigger_type = TriggerType.NORMAL
        elif self._trigger_rearm == TriggerType.SINGLE:
            start_event_queue.append(Event.SINGLE_TRIGGER)
            self.scope_trigger.trigger_type = TriggerType.SINGLE
        self._trigger_rearm = TriggerType.NONE

    def _set_trigger_level(self) -> None:
        self._pause_trigger()
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.SET_TRIGGER_LEVEL)
            self._resume_trigger(start_event_queue)
            if self.debug:
                logging.info('RESUMING NORMAL from set trigger level')

    def _set_adjust_scale_mode(self) -> None:
        self.mode = Mode.ADJUST_SCALE
        self.command_input.set_adjust_mode()
        self.root.focus_set()

    def _set_adjust_cursor_mode(self) -> None:
        if self.cursors.hor_visible or self.cursors.vert_visible:
            self.mode = Mode.ADJUST_CURSORS  
            self.command_input.set_adjust_mode()
            self.root.focus_set()

    def _set_adjust_trigger_level_mode(self) -> None:
        self.mode = Mode.ADJUST_TRIGGER_LEVEL
        self.command_input.set_adjust_mode()
        self.root.focus_set()
        self.scope_display.set_trigger_level(self._display_size/2)

    def _set_command_mode(self) -> None:
        self.mode = Mode.COMMAND
        self.command_input.set_command_mode()
        self.command_input.set_focus()

    def _set_probe(self, probe_div):
        self.scale.probe_div = probe_div
        for readout in self._readouts:
            readout.set_probe(self.scale.probe_div)
            readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
    
    def _update_scope_status(self) -> None: [readout.set_status(self.scope_status.name) for readout in self._readouts] 

    def _update_scope_probe(self) -> None: [readout.set_probe(self.scale.probe_div) for readout in self._readouts]

    def _set_update_scale(self, update_fn: Callable[[], None]) -> None:
        if update_fn is not None:
            update_fn()
        self._pause_trigger()
        self.scale.update_sample_rate(self._scope_interfaces[0].scope.SCOPE_SPECS['sample_rate'], 
                                      self._scope_interfaces[0].scope.SCOPE_SPECS['memory_depth'])
        if self.scope_trigger.trigger_type == TriggerType.AUTO or self.scope_trigger.trigger_type == TriggerType.NORMAL:
            for scope_interface in self._scope_interfaces:
                scope_interface.fs = self.scale.fs
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.CHANGE_SCALE)
            self._resume_trigger(start_event_queue)
            if self.debug:
                logging.info('RESUMING NORMAL from horizontal scale')

    def _update_scale_vert(self, update_fn: Callable[[], None]) -> None:
        if update_fn is not None:
            update_fn()
        self._pause_trigger() 
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.SET_RANGE)
            start_event_queue.append(Event.SET_AMPLIFIER_GAIN)
            self._resume_trigger(start_event_queue)

    def _update_cursor(self, arithmatic_fn: Callable[[], None]) -> None:
        arithmatic_fn()
        self._readouts[0].update_cursors(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))
        self.scope_display.set_cursors(self.cursors)
    
    def _run_png_export(self, filename: str) -> None:
        settings = ExportSettings(vertical_setting=self.scale.vert,
                                  horizontal_setting=self.scale.hor,
                                  probe_div=self.scale.probe_div,
                                  map=self.scope_display.image_map,
                                  cursor_data=self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))
        export_png(settings, filename, self.scope_display.size)

    def _on_auto_trigger_command(self):
        if self.scope_trigger.trigger_type == TriggerType.NORMAL or self.scope_trigger.trigger_type == TriggerType.SINGLE:
            self._stop_trigger()
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.AUTO_TRIGGER)
        self.scope_trigger.trigger_type = TriggerType.AUTO

    def _on_normal_trigger_command(self):
        if self.scope_trigger.trigger_type == TriggerType.AUTO:
            self._stop_trigger()
            for i, start_event_queue in enumerate(self._start_event_queue):
                if i == 0:
                    start_event_queue.append(Event.ENABLE_SIGNAL_TRIGGER)
                else:
                    start_event_queue.append(Event.DISABLE_SIGNAL_TRIGGER)
                start_event_queue.append(Event.NORMAL_TRIGGER)
        else:
            for i, start_event_queue in enumerate(self._start_event_queue):
                if i == 0:
                    start_event_queue.append(Event.ENABLE_SIGNAL_TRIGGER)
                else:
                    start_event_queue.append(Event.DISABLE_SIGNAL_TRIGGER)
                start_event_queue.append(Event.NORMAL_TRIGGER)
        self.scope_trigger.trigger_type = TriggerType.NORMAL
        self.scope_status = Scope_Status.ARMED
        self._update_scope_status()

    def _on_single_trigger_command(self):
        if self.scope_trigger.trigger_type == TriggerType.AUTO or self.scope_trigger.trigger_type == TriggerType.NORMAL:
            self._stop_trigger()
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.SINGLE_TRIGGER)
        self.scope_trigger.trigger_type = TriggerType.SINGLE
        self.scope_status = Scope_Status.ARMED
        self._update_scope_status()

    def _on_trigger_rising_edge_command(self):
        self._pause_trigger()
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.SET_RISING_EDGE_TRIGGER)
            self._resume_trigger(start_event_queue)

    def _on_trigger_falling_edge_command(self):
        self._pause_trigger()
        for start_event_queue in self._start_event_queue:
            start_event_queue.append(Event.SET_FALLING_EDGE_TRIGGER)
            self._resume_trigger(start_event_queue)

    def _on_set_cal_offsets_command(self) -> None: [start_event_queue.append(Event.SET_CAL_OFFSETS) for start_event_queue in self._start_event_queue]

    def _on_record_command(self) -> None: [start_event_queue.append(Event.RECORD_SAMPLE) for start_event_queue in self._start_event_queue]

    def display_signal(self, xx: list[float], triggered: bool, scope_index: int) -> None:
        if xx is not None and len(xx) > 0:
            self._readouts[scope_index].set_average(average(xx))
            self._readouts[scope_index].set_rms(rms(xx))
            self.scope_display.add_vector(xx, scope_index)
            fir_length = self._scope_interfaces[0].scope.FIR_LENGTH if self._scope_interfaces[0].scope.DIGITAL_FILTER else None
            self.scope_display.resample_vector(self.scale.hor, self.scale.vert, self.scale.fs, 
                                               self._scope_interfaces[0].scope.SCOPE_SPECS['memory_depth'], 
                                               self.scope_trigger.trigger_type, triggered,
                                               scope_index, FIR_length=fir_length)
            self.scope_status = Scope_Status.TRIGGERED
            self._update_scope_status()
    
    def _stop_trigger(self) -> None:
        if self.scope_trigger.trigger_type == TriggerType.NORMAL or self.scope_trigger.trigger_type == TriggerType.SINGLE:
            for scope_interface in self._scope_interfaces:
                scope_interface.stop_trigger()
            for end_event_queue in self._end_event_queue:
                if len(end_event_queue) > 0:
                    if end_event_queue[0] == Event.NORMAL_TRIGGER or end_event_queue[0] == Event.SINGLE_TRIGGER:
                        end_event_queue.pop(0)
        if self.debug:
            logging.info('STOP')
        self.scope_trigger.trigger_type = TriggerType.NONE

    # TODO: Refactor the three methods below that are very similar.
    def toggle_cursors(self) -> None:
        self.cursors.toggle() 
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible or self.cursors.vert_visible: 
            self._readouts[0].enable_cursor_readout(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))   
        else: 
            self._readouts[0].disable_cursor_readout()

    def toggle_horizontal_cursors(self) -> None:
        self.cursors.toggle_hor()
        if self.cursors.hor_visible:
            self._readouts[0].enable_cursor_readout(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))  
        elif not self.cursors.vert_visible: 
            self._readouts[0].disable_cursor_readout()
        else:
            self._readouts[0].disable_horizontal_cursor_readout()
            self.cursors.next_cursor()
        self.scope_display.set_cursors(self.cursors)

    def toggle_vertical_cursors(self) -> None:
        self.cursors.toggle_vert()
        if self.cursors.vert_visible:
            self._readouts[0].enable_cursor_readout(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))   
        elif not self.cursors.hor_visible: 
            self._readouts[0].disable_cursor_readout()
        else:
            self._readouts[0].disable_vertical_cursor_readout()
            self.cursors.next_cursor()
        self.scope_display.set_cursors(self.cursors)

    def next_cursor(self) -> None:
        self.cursors.next_cursor()
        self.scope_display.set_cursors(self.cursors)

    def __call__(self) -> None: self.root.mainloop()