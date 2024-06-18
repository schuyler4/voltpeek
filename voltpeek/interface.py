from typing import Callable, Optional, Sequence
from enum import Enum
from threading import Thread, Event, Lock
from time import sleep

import tkinter as tk

from voltpeek import messages
from voltpeek import constants
from voltpeek import commands
from voltpeek.measurements import average, rms
from voltpeek.scope_interface import ScopeInterface, ScopeAction

from voltpeek.scope_display import Scope_Display
from voltpeek.command_input import Command_Input
from voltpeek.readout import Readout
from voltpeek.info_panel import InfoPanel

from voltpeek.reconstruct import reconstruct, quantize_vertical, resample_horizontal, FIR_filter

from voltpeek.trigger import Trigger, TriggerType, get_trigger_voltage, trigger_code
from voltpeek.cursors import Cursors, Cursor_Data
from voltpeek.scale import Scale

from voltpeek.scope_specs import scope_specs

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
    STOP = 4
    CHANGE_SCALE = 5
    RANGE_FLIP_LOW = 6
    RANGE_FLIP_HIGH = 7
    SET_TRIGGER_LEVEL = 8
    EXIT = 9

class UserInterface:
    def __init__(self) -> None:
        self._build_tk_root()

        self.scale: Scale = Scale()
        self.scope_trigger: Trigger = Trigger()
        self.cursors: Cursors = Cursors()

        self.scope_display: Scope_Display = Scope_Display(self.root)
        self.command_input: Command_Input = Command_Input(self.root, self.process_command)
        self.readout: Readout = Readout(self.root, self.scale.vert, self.scale.hor)
        self.info_panel: InfoPanel = InfoPanel(self.root)

        self.readout()
        self.scope_display()
        self.command_input()
        self.info_panel()

        self.mode: Mode = Mode.COMMAND
        self.command_input.set_focus()
        self.vv:Optional[list[float]] = None
        self.serial_scope_connected: bool = False
        self.scope_status = Scope_Status.DISCONNECTED
        self._update_scope_status()
        self._update_scope_probe()
        self._set_trigger_rising_edge()

        self._scope_interface: ScopeInterface = ScopeInterface()

        self._start_event_queue: list[Event] = []
        self._end_event_queue: list[Event] = []

        self._auto_trigger_running = False
        self._normal_trigger_running = False

    def _build_tk_root(self) -> None:
        self.root:tk.Tk = tk.Tk()
        self.root.title(constants.Application.NAME)
        self.root.configure(bg=constants.Window.BACKGROUND_COLOR) 
        self.root.tk.call('tk', 'scaling', 1)
        self.root.after(1, self.check_state)
        self.root.bind('<KeyPress>', self.on_key_press)

    def check_state(self):
        if self._scope_interface.data_available and len(self._start_event_queue) > 0:
            if self._start_event_queue[0] == Event.CONNECT:
                self.start_connect()
                self._end_event_queue.append(Event.CONNECT)
            if self._start_event_queue[0] == Event.SINGLE_TRIGGER:
                print('starting single trigger')
                self._start_single_trigger()
            if self._start_event_queue[0] == Event.AUTO_TRIGGER:
                self._start_auto_trigger_cycle()
                self._end_event_queue.append(Event.AUTO_TRIGGER)
            if self._start_event_queue[0] == Event.NORMAL_TRIGGER:
                self._start_normal_trigger_cycle()
                self._end_event_queue.append(Event.NORMAL_TRIGGER)
            if self._start_event_queue[0] == Event.STOP:
                pass
            if self._start_event_queue[0] == Event.CHANGE_SCALE:
                self._start_update_scale_hor()
                self._end_event_queue.append(Event.CHANGE_SCALE)
            if self._start_event_queue[0] == Event.RANGE_FLIP_LOW:
                self._start_range_flip_low()
            if self._start_event_queue[0] == Event.RANGE_FLIP_HIGH:
                self._start_range_flip_high()
            if self._start_event_queue[0] == Event.SET_TRIGGER_LEVEL:
                self._start_set_trigger_level()
            if self._start_event_queue[0] == Event.EXIT:
                exit()
            self._start_event_queue.pop(0)

        if self._scope_interface.data_available and len(self._end_event_queue) > 0:
            print(self._end_event_queue)
            if self._end_event_queue[0] == Event.CONNECT:
                self.finish_connect()
            if self._end_event_queue[0] == Event.AUTO_TRIGGER:
                self._finish_auto_trigger_cycle()
            if self._end_event_queue[0] == Event.NORMAL_TRIGGER:
                self._finish_normal_trigger_cycle()
            if self._end_event_queue[0] == Event.CHANGE_SCALE:
                self._render_update_scale()
            self._end_event_queue.pop(0)
        self.root.after(1, self.check_state)

    def on_key_press(self, event) -> None:
        if self.info_panel.visible and event.keycode != constants.KeyCodes.ENTER:
            self.info_panel.hide() 
        if self.mode == Mode.ADJUST_SCALE or self.mode == Mode.ADJUST_TRIGGER_LEVEL or self.mode == Mode.ADJUST_CURSORS:
            if event.keycode in constants.Keys.EXIT_COMMAND_MODE: 
                if self.mode == Mode.ADJUST_TRIGGER_LEVEL: 
                    self.set_trigger()
                    self._start_event_queue.append(Event.SET_TRIGGER_LEVEL)
                self._set_command_mode()
        if self.mode == Mode.ADJUST_SCALE:
            if event.char == constants.Keys.VERTICAL_UP:
                self._update_scale_vert(self.scale.increment_vert)
            elif event.char == constants.Keys.VERTICAL_DOWN:
                self._update_scale_vert(self.scale.decrement_vert)
            elif event.char == constants.Keys.HORIZONTAL_RIGHT:
                self._set_update_scale(self.scale.increment_hor)
            elif event.char == constants.Keys.HORIZONTAL_LEFT:
                self._set_update_scale(self.scale.decrement_hor)
        elif self.mode == Mode.ADJUST_TRIGGER_LEVEL:
            if event.char == constants.Keys.VERTICAL_UP:
                self.scope_display.increment_trigger_level()
            elif event.char == constants.Keys.VERTICAL_DOWN:
                self.scope_display.decrement_trigger_level()
        elif self.mode == Mode.ADJUST_CURSORS:
            if event.char == constants.Keys.VERTICAL_UP:
                self._update_cursor(self.cursors.decrement_hor)
            elif event.char == constants.Keys.VERTICAL_DOWN:
                self._update_cursor(self.cursors.increment_hor)
            elif event.char == constants.Keys.HORIZONTAL_RIGHT:
                self._update_cursor(self.cursors.increment_vert)
            elif event.char == constants.Keys.HORIZONTAL_LEFT:
                self._update_cursor(self.cursors.decrement_vert)
        elif self.mode == Mode.COMMAND:
            if event.keycode == constants.KeyCodes.UP_ARROW:
                self.command_input.set_command_stack()

    def process_command(self, command:str) -> None:
        for key in self.get_commands():
            if key == command: 
                self.get_commands()[key]()
                return
        self.command_input.set_error(messages.Errors.INVALID_COMMAND_ERROR)
    
    def _set_adjust_scale_mode(self) -> None:
        self.mode = Mode.ADJUST_SCALE
        self.command_input.set_adjust_mode()
        self.root.focus_set()

    def _set_adjust_cursor_mode(self) -> None:
        # TODO: Fix bug where cursors are not visible
        if self.cursors.hor_visible or self.cursors.vert_visible:
            self.mode = Mode.ADJUST_CURSORS  
            self.command_input.set_adjust_mode()
            self.root.focus_set()

    def _set_adjust_trigger_level_mode(self) -> None:
        self.mode = Mode.ADJUST_TRIGGER_LEVEL
        self.command_input.set_adjust_mode()
        self.root.focus_set()
        self.scope_display.set_trigger_level(constants.Display.SIZE/2)

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
        self.scale.update_sample_rate(scope_specs['sample_rate'], scope_specs['memory_depth'])
        self._start_event_queue.append(Event.CHANGE_SCALE)

    def _start_update_scale_hor(self) -> None:
        self._scope_interface.set_value(self.scale.clock_div)
        print(self.scale.clock_div)
        self._scope_interface.set_scope_action(ScopeAction.SET_CLOCK_DIV)
        self._change_scale = True
        self._scope_interface.run()

    def _update_scale_vert(self, update_fn: Callable[[], None]) -> None:
        update_fn()
        if self.scale.low_range_flip:
            self._start_event_queue.append(Event.RANGE_FLIP_LOW)
        elif self.scale.high_range_flip:
            self._start_event_queue.append(Event.RANGE_FLIP_HIGH)
        else:
            self._render_update_scale()

    def _start_range_flip_high(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.SET_HIGH_RANGE)
        self._scale_range_flip_high = True
        self._scope_interface.run()

    def _start_range_flip_low(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.SET_LOW_RANGE)
        self._scale_range_flip_low = True
        self._scope_interface.run()
    
    def _render_update_scale(self) -> None:
        self.readout.update_settings(self.scale.vert*self.scale.probe_div, self.scale.hor)
        self.readout.set_fs(self.scale.fs)
        if self.vv is not None:
            vertical_encode: list[int] = quantize_vertical(self.vv, self.scale.vert)
            horizontal_encode: list[int] = resample_horizontal(vertical_encode, self.scale.hor, scope_specs['sample_rate']) 
            self.scope_display.set_vector(horizontal_encode) 

    def _update_cursor(self, arithmatic_fn: Callable[[], None]) -> None:
        arithmatic_fn()
        self.readout.update_cursors(self.get_cursor_dict(self.cursors.hor_visible, self.cursors.vert_visible))
        self.scope_display.set_cursors(self.cursors)
    
    def exit(self) -> None:
        if not self._auto_trigger_running and not self._normal_trigger_running:
            exit()
        elif self._normal_trigger_running:
            self._stop_and_exit = True
            self._normal_trigger_running = False
            self._scope_interface.set_scope_action(ScopeAction.STOP)
        elif self._auto_trigger_running:
            self._auto_trigger_running = False
            self._stop_and_exit = True

    def _calibrate_offsets(self):
        average_offset: float = 0  

    def _connect(self):
        self._start_event_queue.append(Event.CONNECT)
        self._set_update_scale(None)
        self._start_event_queue.append(Event.CHANGE_SCALE)
        self._start_event_queue.append(Event.RANGE_FLIP_HIGH)

    def get_commands(self): 
        return {
            commands.EXIT_COMMAND: lambda: self._start_event_queue.append(Event.EXIT),
            commands.CONNECT_COMMAND: self._connect,
            commands.SCALE_COMMAND: self._set_adjust_scale_mode, 
            commands.TRIGGER_LEVEL_COMMAND: self._set_adjust_trigger_level_mode,  
            commands.TOGGLE_CURS: self.toggle_cursors, 
            commands.TOGGLE_HCURS: self.toggle_horizontal_cursors, 
            commands.TOGGLE_VCURS: self.toggle_vertical_cursors,
            commands.NEXT_CURS: self.cursors.next_cursor, 
            commands.ADJUST_CURS: self._set_adjust_cursor_mode, 
            commands.AUTO_TRIGGER_COMMAND: lambda: self._start_event_queue.append(Event.AUTO_TRIGGER), 
            commands.NORMAL_TRIGGER_COMMAND: lambda: self._start_event_queue.append(Event.NORMAL_TRIGGER),
            commands.SINGLE_TRIGGER_COMMAND: self._start_single_trigger,
            commands.STOP: self._stop_trigger,
            commands.TRIGGER_RISING_EDGE_COMMAND: self._set_trigger_rising_edge,
            commands.TRIGGER_FALLING_EDGE_COMMAND: self._set_trigger_falling_edge,
            commands.HELP: self.info_panel.show,
            commands.PROBE_1: lambda: self._set_probe(1),
            commands.PROBE_10: lambda: self._set_probe(10),
            commands.CAL: self._calibrate_offsets
        }

    def start_connect(self) -> None:
        self.scope_status = Scope_Status.CONNECTING
        self._update_scope_status()
        self._scope_interface.set_scope_action(ScopeAction.CONNECT)
        self._connect = True
        self._scope_interface.run()
            
    def finish_connect(self) -> None:
        self.scope_status = Scope_Status.NEUTRAL
        self._update_scope_status()

    def display_signal(self, xx: list[int]) -> None:
        if len(xx) > 0:
            filtered_signal: list[float] = FIR_filter(xx) 
            self.vv = reconstruct(filtered_signal, scope_specs, self.scale.vert, self.scale.probe_div)
            self.readout.set_average(average(self.vv))
            self.readout.set_rms(rms(self.vv))
            vertical_encode:list[float] = quantize_vertical(self.vv, self.scale.vert)
            h:list[int] = resample_horizontal(vertical_encode, self.scale.hor, self.scale.fs) 
            self.scope_display.set_vector(h)
            self.scope_status = Scope_Status.TRIGGERED
            self._update_scope_status()

    def _start_auto_trigger_cycle(self) -> None:
        print('starting auto trigger cycle')
        self._scope_interface.set_scope_action(ScopeAction.FORCE_TRIGGER)
        self._auto_trigger_running = True
        self._scope_interface.run()

    def _finish_auto_trigger_cycle(self) -> None:
        print('finishing auto trigger cycle')
        self.display_signal(self._scope_interface.xx)
        if self._auto_trigger_running:
            self._start_event_queue.append(Event.AUTO_TRIGGER)

    def _start_normal_trigger_cycle(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.TRIGGER)
        self._normal_trigger_running = True
        self._scope_interface.run()

    def _finish_normal_trigger_cycle(self) -> None:
        self.display_signal(self._scope_interface.xx)
        if self._normal_trigger_running:
            self._start_event_queue.append(Event.NORMAL_TRIGGER)

    def _start_single_trigger(self) -> None:
        self._scope_interface.set_scope_action(ScopeAction.TRIGGER)
        self._single_trigger = True
        self._scope_interface.run()

    def _stop_trigger(self) -> None:
        if self._auto_trigger_running:
            self._auto_trigger_running = False
        elif self._normal_trigger_running:
            self._normal_trigger_running = False  
            self._scope_interface.set_scope_action(ScopeAction.STOP)
            self.scope_status = Scope_Status.NEUTRAL
            self._update_scope_status()

    def set_trigger(self) -> None: 
        trigger_height:int = self.scope_display.get_trigger_level()
        trigger_voltage = get_trigger_voltage(self.scale.vert, trigger_height)
        attenuation: Optional[float] = None
        offset: Optional[float] = None
        if self.scale.vert <=  constants.Scale.VERTICALS[constants.Scale.LOW_RANGE_VERTICAL_INDEX]:
            attenuation = scope_specs['attenuation']['range_low']
            offset = scope_specs['offset']['range_low']
        else:
            attenuation = scope_specs['attenuation']['range_high']
            offset = scope_specs['offset']['range_high']
        self.trigger_code:int = trigger_code(trigger_voltage, scope_specs['voltage_ref'], attenuation, offset)

    def _start_set_trigger_level(self) -> None:
        self._set_trigger_level = True
        self._scope_interface.set_value(self.trigger_code)
        self._scope_interface.set_scope_action(ScopeAction.SET_TRIGGER_LEVEL)
        self._scope_interface.run()

    def get_cursor_dict(self, horizontal:bool, vertical:bool) -> Cursor_Data:
        h1:str = self.cursors.get_hor1_voltage(self.scale.vert) if horizontal else ''
        h2:str = self.cursors.get_hor2_voltage(self.scale.vert) if horizontal else '' 
        hdelta:str = self.cursors.get_delta_voltage(self.scale.vert) if horizontal else ''
        v1:str = self.cursors.get_vert1_time(self.scale.hor) if vertical else ''
        v2:str = self.cursors.get_vert2_time(self.scale.hor) if vertical else ''
        vdelta:str = self.cursors.get_delta_time(self.scale.hor) if vertical else ''
        return { 'h1': h1, 'h2': h2, 'hdelta': hdelta, 'v1': v1, 'v2': v2, 'vdelta': vdelta }
    
    def toggle_cursors(self) -> None:
        self.cursors.toggle() 
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible or self.cursors.vert_visible: 
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible, self.cursors.vert_visible))   
        else: 
            self.readout.disable_cursor_readout()

    def toggle_horizontal_cursors(self) -> None:
        self.cursors.toggle_hor()
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible:
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible, self.cursors.vert_visible))  
        else: 
            self.readout.disable_cursor_readout()

    def toggle_vertical_cursors(self) -> None:
        self.cursors.toggle_vert()
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.vert_visible:
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible, self.cursors.vert_visible))   
        else: 
            self.readout.disable_cursor_readout()

    def _set_trigger_rising_edge(self) -> None:
        self.scope_trigger.trigger_type = TriggerType.RISING_EDGE
        self.readout.set_trigger_type(self.scope_trigger.trigger_type)

    def _set_trigger_falling_edge(self) -> None:
        self.scope_trigger.trigger_type = TriggerType.FALLING_EDGE
        self.readout.set_trigger_type(self.scope_trigger.trigger_type)

    def __call__(self) -> None: self.root.mainloop()