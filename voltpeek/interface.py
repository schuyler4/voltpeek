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

from voltpeek.trigger import Trigger, TriggerType
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
        self.readout: Readout = Readout(self.root, self.scale.vert, self.scale.hor)

        self.readout()
        self.scope_display()
        self.command_input()

        self.mode: Mode = Mode.COMMAND
        self.command_input.set_focus()
        self.serial_scope_connected: bool = False
        self.scope_status = Scope_Status.DISCONNECTED
        self._update_scope_status()
        self._update_scope_probe()

        self._start_event_queue: list[Event] = []
        self._end_event_queue: list[Event] = []

        self._connect_initiated = False
        self._auto_trigger_running = False
        self._normal_trigger_running = False
        self._record_running = False
        self._calibration = False
        self._triggered = False
        self._calibration_step = 0

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
            if self._scope_interface.disconnected_error:
                self.command_input.set_error(self.SCOPE_NOT_CONNECTED_ERROR)
                self.command_input.display_error()
                self._scope_interface.clear_disconnected_error()
                self._connect_initiated = False
                self._set_disconnected()
                self._start_event_queue = []
                self._end_event_queue = []
            else:
                # The end events must go first otherwise the start events will always have priority.
                if self._scope_interface.data_available and len(self._end_event_queue) > 0:
                    if self.debug:
                        logging.info(f'end event: {self._end_event_queue[0].name}')
                    if self._end_event_queue[0] == Event.CONNECT:
                        self.finish_connect()
                    if self._end_event_queue[0] == Event.AUTO_TRIGGER:
                        self._finish_auto_trigger_cycle()
                    if self._end_event_queue[0] == Event.NORMAL_TRIGGER:
                        self._finish_normal_trigger_cycle()
                    if self._end_event_queue[0] == Event.SINGLE_TRIGGER:
                        self._finish_single_trigger()
                    if self._end_event_queue[0] == Event.CHANGE_SCALE:
                        self._render_update_scale()
                    if self._end_event_queue[0] == Event.SET_RISING_EDGE_TRIGGER:
                        self._finish_set_rising_edge_trigger()
                    if self._end_event_queue[0] == Event.SET_FALLING_EDGE_TRIGGER:
                        self._finish_set_falling_edge_trigger()
                    if self._end_event_queue[0] == Event.RECORD_SAMPLE:
                        self._finish_record_sample()
                    self._end_event_queue.pop(0)
                if self._scope_interface.data_available and len(self._start_event_queue) > 0:
                    if self.debug:
                        logging.info(f'start event: {self._start_event_queue[0].name}')
                    if self._start_event_queue[0] == Event.STOP:
                        self._stop_trigger()
                    if self._start_event_queue[0] == Event.CONNECT:
                        self.start_connect()
                        self._end_event_queue.append(Event.CONNECT)
                    if self._start_event_queue[0] == Event.SINGLE_TRIGGER:
                        self._start_single_trigger()
                        self._end_event_queue.append(Event.SINGLE_TRIGGER)
                    if self._start_event_queue[0] == Event.AUTO_TRIGGER:
                        self._start_auto_trigger_cycle()
                        self._end_event_queue.append(Event.AUTO_TRIGGER)
                    if self._start_event_queue[0] == Event.NORMAL_TRIGGER:
                        self._start_normal_trigger_cycle()
                        self._end_event_queue.append(Event.NORMAL_TRIGGER)
                    if self._start_event_queue[0] == Event.FORCE_TRIGGER:
                        self._start_force_trigger()
                        self._end_event_queue.append(Event.FORCE_TRIGGER)
                    if self._start_event_queue[0] == Event.CHANGE_SCALE:
                        self._start_update_scale_hor()
                        self._end_event_queue.append(Event.CHANGE_SCALE)
                    if self._start_event_queue[0] == Event.SET_TRIGGER_LEVEL:
                        self._start_set_trigger_level()
                    if self._start_event_queue[0] == Event.READ_CAL_OFFSETS:
                        self._start_read_cal_offsets()
                    if self._start_event_queue[0] == Event.SET_CAL_OFFSETS:
                        self._start_set_calibration()
                    if self._start_event_queue[0] == Event.SET_RANGE:
                        self._start_set_range()  
                    if self._start_event_queue[0] == Event.SET_AMPLIFIER_GAIN:
                        self._start_set_amplifier_gain()
                    if self._start_event_queue[0] == Event.SET_RISING_EDGE_TRIGGER:
                        self._start_set_rising_edge_trigger()
                        self._end_event_queue.append(Event.SET_RISING_EDGE_TRIGGER)
                    if self._start_event_queue[0] == Event.SET_FALLING_EDGE_TRIGGER:
                        self._start_set_falling_edge_trigger()
                        self._end_event_queue.append(Event.SET_FALLING_EDGE_TRIGGER)
                    if self._start_event_queue[0] == Event.RECORD_SAMPLE:
                        self._start_record_sample()
                        self._end_event_queue.append(Event.RECORD_SAMPLE)
                    self._start_event_queue.pop(0)
        self.root.after(1, self.check_state)

    # TODO: This all needs to be refactored
    def on_key_press(self, event) -> None:
        if self.mode == Mode.ADJUST_SCALE or self.mode == Mode.ADJUST_TRIGGER_LEVEL or self.mode == Mode.ADJUST_CURSORS:
            if (event.keysym == 'Escape') or (event.state & 0x4 and event.keysym == 'c'): 
                if self.mode == Mode.ADJUST_TRIGGER_LEVEL: 
                    self._start_event_queue.append(Event.SET_TRIGGER_LEVEL)
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

    def process_command(self, command:str) -> None:
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
        self.readout.set_probe(self.scale.probe_div)
        self.readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
    
    def _update_scope_status(self) -> None: self.readout.set_status(self.scope_status.name)

    def _update_scope_probe(self) -> None: self.readout.set_probe(self.scale.probe_div)

    def _set_update_scale(self, update_fn: Callable[[], None]) -> None:
        if update_fn is not None:
            update_fn()
        self.scale.update_sample_rate(self._scope_interface.scope.SCOPE_SPECS['sample_rate'], 
                                      self._scope_interface.scope.SCOPE_SPECS['memory_depth'])
        if self._auto_trigger_running or self._normal_trigger_running:
            self._scope_interface.fs = self.scale.fs
        self._start_event_queue.append(Event.CHANGE_SCALE)

    def _start_read_cal_offsets(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.READ_CAL_OFFSETS)
        self._scope_interface.run()

    def _start_update_scale_hor(self) -> None:
        self._scope_interface.set_value(self.scale.clock_div)
        self._scope_interface.set_scope_action(ScopeAction.SET_CLOCK_DIV)
        self._scope_interface.run()

    def _update_scale_vert(self, update_fn: Callable[[], None]) -> None:
        update_fn()
        self._start_event_queue.append(Event.SET_RANGE)
        self._start_event_queue.append(Event.SET_AMPLIFIER_GAIN)
        self._render_update_scale()

    def _start_set_calibration(self) -> None:
        self._scope_interface.set_value(self.scale.vert)
        self._scope_interface.set_scope_action(ScopeAction.SET_CAL_OFFSETS)
        self._scope_interface.run()

    def _start_set_range(self) -> None:
        self._scope_interface.set_full_scale(self.scale.vert*(self.scale.GRID_COUNT/2))
        self._scope_interface.set_scope_action(ScopeAction.SET_RANGE)
        self._scope_interface.run()
    
    def _start_set_amplifier_gain(self) -> None:
        self._scope_interface.set_full_scale(self.scale.vert*(self.scale.GRID_COUNT/2))
        self._scope_interface.set_scope_action(ScopeAction.SET_AMPLIFIER_GAIN)
        self._scope_interface.run()

    def _render_update_scale(self) -> None:
        self.readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
        self.readout.set_fs(self.scale.fs)
        if self._scope_interface.xx is not None and len(self._scope_interface.xx) > 0:
            self.scope_display.resample_vector(self.scale.hor, self.scale.vert, self._last_fs, 
                                               self._scope_interface.scope.SCOPE_SPECS['memory_depth'], 
                                               self.scope_trigger.trigger_type, self._triggered,
                                               self._scope_interface.scope.FIR_LENGTH)

    def _update_cursor(self, arithmatic_fn: Callable[[], None]) -> None:
        arithmatic_fn()
        self.readout.update_cursors(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))
        self.scope_display.set_cursors(self.cursors)
    
    def _connect(self, identifier: str):
        for scope in get_available_scopes():
            if list(scope.keys())[0] == identifier:
                for connected_device in scope[identifier].find_scope_ports():
                    self._scope_interfaces.append(ScopeInterface(scope[identifier], device=connected_device))
                self._connect_initiated = True
                self._start_event_queue.append(Event.CONNECT)
                self._start_event_queue.append(Event.SET_RANGE)
                self._start_event_queue.append(Event.SET_AMPLIFIER_GAIN)
                if isinstance(self._scope_interfaces[0].scope, NS1):
                    self._start_event_queue.append(Event.READ_CAL_OFFSETS)
                self._set_update_scale(None)
                return
        self.command_input.set_error(self.INVALID_SCOPE_ERROR)

    def _set_fir(self, new_length: int): self._fir_length = new_length

    def _run_png_export(self, filename: str) -> None:
        settings = ExportSettings(vertical_setting=self.scale.vert,
                                  horizontal_setting=self.scale.hor,
                                  probe_div=self.scale.probe_div,
                                  map=self.scope_display.image_map,
                                  cursor_data=self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))
        export_png(settings, filename, self.scope_display.size)

    def _on_auto_trigger_command(self):
        if self._normal_trigger_running:
            self._stop_trigger()
            self._start_event_queue += [Event.AUTO_TRIGGER]
            self._normal_trigger_running = False
        else:
            self._start_event_queue.append(Event.AUTO_TRIGGER)

    def _on_normal_trigger_command(self):
        if self._auto_trigger_running:
            self._start_event_queue += [Event.STOP, Event.NORMAL_TRIGGER]
            self._auto_trigger_running = False
        else:
            self._start_event_queue.append(Event.NORMAL_TRIGGER) 

    def _on_single_trigger_command(self):
        if self._auto_trigger_running:
            self._start_event_queue += [Event.STOP, Event.SINGLE_TRIGGER]
            self._auto_trigger_running = False
        elif self._normal_trigger_running:
            self._start_event_queue += [Event.STOP, Event.SINGLE_TRIGGER]
            self._normal_trigger_running = False
        else:
            self._start_event_queue.append(Event.SINGLE_TRIGGER)

    def get_commands(self): 
        return {
            commands.EXIT_COMMAND: lambda: exit(),
            commands.CONNECT_COMMAND: lambda identifier: self._connect(identifier),
            commands.SCALE_COMMAND: self._set_adjust_scale_mode, 
            commands.TRIGGER_LEVEL_COMMAND: self._set_adjust_trigger_level_mode,  
            commands.TOGGLE_CURS: self.toggle_cursors, 
            commands.TOGGLE_HCURS: self.toggle_horizontal_cursors, 
            commands.TOGGLE_VCURS: self.toggle_vertical_cursors,
            commands.NEXT_CURS: self.next_cursor, 
            commands.ADJUST_CURS: self._set_adjust_cursor_mode, 
            commands.AUTO_TRIGGER_COMMAND: self._on_auto_trigger_command, 
            commands.NORMAL_TRIGGER_COMMAND: self._on_normal_trigger_command,
            commands.SINGLE_TRIGGER_COMMAND: self._on_single_trigger_command,
            commands.STOP: self._stop_trigger,
            commands.TRIGGER_RISING_EDGE_COMMAND: lambda: self._start_event_queue.append(Event.SET_RISING_EDGE_TRIGGER),
            commands.TRIGGER_FALLING_EDGE_COMMAND: lambda: self._start_event_queue.append(Event.SET_FALLING_EDGE_TRIGGER),
            commands.PROBE_1: lambda: self._set_probe(1),
            commands.PROBE_10: lambda: self._set_probe(10),
            commands.CAL: lambda: self._start_event_queue.append(Event.SET_CAL_OFFSETS),
            commands.PNG: lambda filename: self._run_png_export(filename),
            'record': lambda: self._start_event_queue.append(Event.RECORD_SAMPLE)
        }

    def _set_disconnected(self) -> None:
        self.scope_status = Scope_Status.DISCONNECTED
        self._update_scope_status()

    def start_connect(self) -> None:
        self.scope_status = Scope_Status.CONNECTING
        self._update_scope_status()
        self._scope_interface.set_scope_action(ScopeAction.CONNECT)
        self._scope_interface.run()
            
    def finish_connect(self) -> None:
        self.scope_status = Scope_Status.NEUTRAL
        self.scale.update_sample_rate(self._scope_interface.scope.SCOPE_SPECS['sample_rate'], self._scope_interface.scope.SCOPE_SPECS['memory_depth'])
        self._start_event_queue.append(Event.CHANGE_SCALE)
        self._start_event_queue.append(Event.SET_RISING_EDGE_TRIGGER)
        self._start_event_queue.append(Event.SET_TRIGGER_LEVEL)
        self._update_scope_status()

    def display_signal(self, xx: list[float], triggered: bool) -> None:
        if xx is not None and len(xx) > 0:
            self.readout.set_average(average(xx))
            self.readout.set_rms(rms(xx))
            self.scope_display.vector = xx
            self.scope_display.resample_vector(self.scale.hor, self.scale.vert, self.scale.fs, 
                                               self._scope_interface.scope.SCOPE_SPECS['memory_depth'], 
                                               self.scope_trigger.trigger_type, triggered,
                                               self._scope_interface.scope.FIR_LENGTH)
            self.scope_status = Scope_Status.TRIGGERED
            self._update_scope_status()

    def _start_auto_trigger_cycle(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.FORCE_TRIGGER)
        self._auto_trigger_running = True
        self._scope_interface.fs = self.scale.fs
        self._last_fs = self.scale.fs
        self._scope_interface.run()

    def _finish_auto_trigger_cycle(self) -> None:
        self._triggered = False
        self.display_signal(self._scope_interface.xx, self._triggered)
        if self._auto_trigger_running:
            self._start_event_queue.append(Event.AUTO_TRIGGER)

    def _start_normal_trigger_cycle(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.TRIGGER)
        self._normal_trigger_running = True
        self._scope_interface.fs = self.scale.fs
        self._last_fs = self.scale.fs
        self._scope_interface.run()

    def _finish_normal_trigger_cycle(self) -> None:
        if len(self._scope_interface.xx) > 0: 
            self._triggered = True
            self.display_signal(self._scope_interface.xx, self._triggered)
        if self._normal_trigger_running:
            self._start_event_queue.append(Event.NORMAL_TRIGGER)

    def _finish_single_trigger(self) -> None:
        if len(self._scope_interface.xx) > 0:
            self._triggered = True
            self.display_signal(self._scope_interface.xx, self._triggered)

    def _start_force_trigger(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.FORCE_TRIGGER)
        self._scope_interface.run()

    def _start_single_trigger(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.TRIGGER)
        self._scope_interface.run()

    def _start_record_sample(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.RECORD_SAMPLE)
        self._scope_interface.run()
        self._record_running = True

    def _finish_record_sample(self) -> None:
        self.scope_display.record = self._scope_interface._record
        self.scope_display.resample_record(self.scale.vert)
        if self._record_running:
            self._start_event_queue.append(Event.RECORD_SAMPLE)

    def _stop_trigger(self) -> None:
        if self._auto_trigger_running:
            self._auto_trigger_running = False
        elif self._normal_trigger_running:
            self._normal_trigger_running = False  
            self._scope_interface.stop_trigger()

    def _start_set_trigger_level(self) -> None:
        self._set_trigger_level = True
        self._scope_interface.set_value(self.scope_display.get_trigger_voltage(self.scale.vert))
        self._scope_interface.set_scope_action(ScopeAction.SET_TRIGGER_LEVEL)
        self._scope_interface.run()

    def _start_set_rising_edge_trigger(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.SET_RISING_EDGE_TRIGGER)
        self._scope_interface.run()

    def _finish_set_rising_edge_trigger(self) -> None:
        self.scope_trigger.trigger_type = TriggerType.RISING_EDGE
        self.readout.set_trigger_type(self.scope_trigger.trigger_type)

    def _start_set_falling_edge_trigger(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.SET_FALLING_EDGE_TRIGGER)
        self._scope_interface.run()

    def _finish_set_falling_edge_trigger(self) -> None:
        self.scope_trigger.trigger_type = TriggerType.FALLING_EDGE
        self.readout.set_trigger_type(self.scope_trigger.trigger_type)

    # TODO: Refactor the three methods below that are very similar.
    def toggle_cursors(self) -> None:
        self.cursors.toggle() 
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible or self.cursors.vert_visible: 
            self.readout.enable_cursor_readout(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))   
        else: 
            self.readout.disable_cursor_readout()

    def toggle_horizontal_cursors(self) -> None:
        self.cursors.toggle_hor()
        if self.cursors.hor_visible:
            self.readout.enable_cursor_readout(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))  
        elif not self.cursors.vert_visible: 
            self.readout.disable_cursor_readout()
        else:
            self.readout.disable_horizontal_cursor_readout()
            self.cursors.next_cursor()
        self.scope_display.set_cursors(self.cursors)

    def toggle_vertical_cursors(self) -> None:
        self.cursors.toggle_vert()
        if self.cursors.vert_visible:
            self.readout.enable_cursor_readout(self.cursors.get_cursor_dict(self.scale.hor, self.scale.vert))   
        elif not self.cursors.hor_visible: 
            self.readout.disable_cursor_readout()
        else:
            self.readout.disable_vertical_cursor_readout()
            self.cursors.next_cursor()
        self.scope_display.set_cursors(self.cursors)

    def next_cursor(self) -> None:
        self.cursors.next_cursor()
        self.scope_display.set_cursors(self.cursors)

    def __call__(self) -> None: self.root.mainloop()