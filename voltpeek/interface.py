#DEBUG
import matplotlib.pyplot as plt
#DEBUG
from typing import Callable, Optional, Sequence
from enum import Enum
from threading import Thread, Event, Lock

import tkinter as tk

from voltpeek import messages
from voltpeek import constants
from voltpeek import commands
from voltpeek.measurements import average, rms
from voltpeek.serial_scope import Serial_Scope

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

class ScopeAction(Enum):
    CONNECT = 0
    TRIGGER = 1
    AUTO_TRIGGER = 2

class ScopeInterface(Thread):
    def __init__(self):
        self._scope_connected: bool = False
        self._xx:Optional[list[float]] = None
        self._serial_scope = Serial_Scope(115200)
        self._data_available = Lock()
        self._action: ScopeAction = None
        self._stop = Event()

    def _trigger(self, forced=True):
        assert self._scope_connected
        if forced:
            xx: list[int] = self._serial_scope.get_scope_force_trigger_data()
        else:
            xx: list[int] = self._serial_scope.get_scope_trigger_data()
        self._xx = xx

    def run(self):
        self._data_available.acquire()
        if self._action == ScopeAction.CONNECT:
            self._serial_scope.init_serial()
        if self._action == ScopeAction.AUTO_TRIGGER:
            self._trigger(forced=True)
        if self._action == ScopeAction.TRIGGER:
            self._trigger(forced=False)
        self._data_available.release()

    @property 
    def data_available(self): return self._data_available

    @property
    def task_complete(self): return not self.is_alive()

    def set_scope_action(self, new_scope_action: ScopeAction):
        if self.task_complete and self.data_available:
            self._action = new_scope_action

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
        self.trigger_running: Event = Event()
        self.connect_thread: Thread = Thread()
        self.trigger_thread: Thread = Thread()
        self._update_fs()
        self._update_scope_probe()
        self._set_trigger_rising_edge()

        self._scope_interface = ScopeInterface()
        self._force_trigger = False
        self._single_trigger = False
        self._normal_trigger = False

    def _build_tk_root(self) -> None:
        self.root:tk.Tk = tk.Tk()
        self.root.title(constants.Application.NAME)
        self.root.configure(bg=constants.Window.BACKGROUND_COLOR) 
        self.root.tk.call('tk', 'scaling', 1)
        self.root.bind('<KeyPress>', self.on_key_press)

    def on_key_press(self, event) -> None:
        if self.info_panel.visible and event.keycode != constants.KeyCodes.ENTER:
            self.info_panel.hide() 
        if(self.mode == Mode.ADJUST_SCALE 
           or self.mode == Mode.ADJUST_TRIGGER_LEVEL or self.mode == Mode.ADJUST_CURSORS):
            if event.keycode in constants.Keys.EXIT_COMMAND_MODE: 
                if(self.mode == Mode.ADJUST_TRIGGER_LEVEL and self.serial_scope_connected): 
                    self.set_trigger()
                self._set_command_mode()
        if self.mode == Mode.ADJUST_SCALE:
            if(event.char == constants.Keys.VERTICAL_UP):
                self._update_scale(self.scale.increment_vert)
            elif(event.char == constants.Keys.VERTICAL_DOWN):
                self._update_scale(self.scale.decrement_vert)
            elif(event.char == constants.Keys.HORIZONTAL_RIGHT):
                self._update_scale(self.scale.increment_hor)
            elif(event.char == constants.Keys.HORIZONTAL_LEFT):
                self._update_scale(self.scale.decrement_hor)
        elif(self.mode == Mode.ADJUST_TRIGGER_LEVEL):
            if(event.char == constants.Keys.VERTICAL_UP):
                self.scope_display.increment_trigger_level()
            elif(event.char == constants.Keys.VERTICAL_DOWN):
                self.scope_display.decrement_trigger_level()
        elif(self.mode == Mode.ADJUST_CURSORS):
            if(event.char == constants.Keys.VERTICAL_UP):
                self._update_cursor(self.cursors.decrement_hor)
            elif(event.char == constants.Keys.VERTICAL_DOWN):
                self._update_cursor(self.cursors.increment_hor)
            elif(event.char == constants.Keys.HORIZONTAL_RIGHT):
                self._update_cursor(self.cursors.increment_vert)
            elif(event.char == constants.Keys.HORIZONTAL_LEFT):
                self._update_cursor(self.cursors.decrement_vert)
        elif(self.mode == Mode.COMMAND):
            if(event.keycode == constants.KeyCodes.UP_ARROW):
                self.command_input.set_command_stack()

    def process_command(self, command:str) -> None:
        for key in self.get_commands():
            if(key == command): 
                self.get_commands()[key]()
                return
        self.command_input.set_error(messages.Errors.INVALID_COMMAND_ERROR)
    
    def _set_adjust_scale_mode(self) -> None:
        self.mode = Mode.ADJUST_SCALE
        self.command_input.set_adjust_mode()
        self.root.focus_set()

    def _set_adjust_cursor_mode(self) -> None:
        # TODO: Fix bug where cursors are not visible
        if(self.cursors.hor_visible or self.cursors.vert_visible):
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
    
    def _update_scope_status(self) -> None: self.readout.set_status(self.scope_status.name)

    def _update_scope_probe(self) -> None: self.readout.set_probe(self.scale.probe_div)

    def _update_fs(self):
        self.scale.update_sample_rate(scope_specs['sample_rate'], scope_specs['memory_depth'])
        self.readout.set_fs(self.scale.fs)
        if self.serial_scope_connected:
            self.serial_scope.set_clock_div(self.scale.clock_div)
        print(self.scale.fs)
        print(self.scale.clock_div)

    def _update_scale(self, arithmatic_fn: Callable[[], None]) -> None:
        arithmatic_fn()
        self.readout.update_settings(self.scale.vert, self.scale.hor)
        if self.scale.low_range_flip and self.serial_scope_connected:
            self.serial_scope.request_low_range()
        elif self.scale.high_range_flip and self.serial_scope_connected:
            self.serial_scope.request_high_range()
        if self.vv is not None:
            fs: int = 625000000   
            v_vertical: float = self.scale.vert
            h_horizontal: float = self.scale.hor
            vertical_encode: list[int] = quantize_vertical(self.vv, v_vertical)
            horizontal_encode: list[int] = resample_horizontal(vertical_encode, h_horizontal, fs) 
            self.scope_display.set_vector(horizontal_encode) 
        self._update_fs()

    def _update_cursor(self, arithmatic_fn: Callable[[], None]) -> None:
        arithmatic_fn()
        self.readout.update_cursors(self.get_cursor_dict(self.cursors.hor_visible, 
                                                         self.cursors.vert_visible))
        self.scope_display.set_cursors(self.cursors)
    
    def exit(self) -> None:
        if self.trigger_running.is_set(): 
            self.trigger_running.clear()
        exit()

    def show_raw_data(self) -> None:
        plt.plot(self.nn, self.xx)
        plt.show()

    def get_commands(self): 
        return {
            commands.EXIT_COMMAND: self.exit,
            commands.CONNECT_COMMAND: self.connect_serial_scope,
            commands.SCALE_COMMAND: self._set_adjust_scale_mode, 
            commands.TRIGGER_LEVEL_COMMAND: self._set_adjust_trigger_level_mode,  
            commands.TOGGLE_CURS: self.toggle_cursors, 
            commands.TOGGLE_HCURS: self.toggle_horizontal_cursors, 
            commands.TOGGLE_VCURS: self.toggle_vertical_cursors,
            commands.NEXT_CURS: self.cursors.next_cursor, 
            commands.ADJUST_CURS: self._set_adjust_cursor_mode, 
            commands.AUTO_TRIGGER_COMMAND: self.start_auto_trigger, 
            commands.NORMAL_TRIGGER_COMMAND: self.start_normal_trigger,
            commands.SINGLE_TRIGGER_COMMAND: self.start_single_trigger,
            commands.STOP: self.stop_auto_trigger,
            commands.TRIGGER_RISING_EDGE_COMMAND: self._set_trigger_rising_edge,
            commands.TRIGGER_FALLING_EDGE_COMMAND: self._set_trigger_falling_edge,
            commands.HELP: self.info_panel.show,
            commands.PROBE_1: lambda: self._set_probe(1),
            commands.PROBE_10: lambda: self._set_probe(10),
            'rawdata':self.show_raw_data
        }
            
    def connect_serial_scope(self) -> None:

        def connect_worker():
            self.serial_scope.init_serial()
            self.serial_scope_connected = True
            low_range_index = constants.Scale.LOW_RANGE_VERTICAL_INDEX
            if(self.scale.vert <= constants.Scale.VERTICALS[low_range_index]):
                self.serial_scope.request_low_range()
            else:
                self.serial_scope.request_high_range()
            self.scope_status = Scope_Status.NEUTRAL
            self._update_scope_status()
            self._update_fs()

        self.serial_scope = Serial_Scope(115200)
        if self.serial_scope.pico_connected():
            self.scope_status = Scope_Status.CONNECTING
            self._update_scope_status()
            self.connect_thread = Thread(target=connect_worker)
            self.connect_thread.start()
        else:
            self.command_input.set_error('NewtScope is not connected.')

    def display_signal(self, xx: list[int]) -> None:
        if(len(xx) > 0):
            filtered_signal: list[float] = FIR_filter(xx) 
            self.vv = reconstruct(filtered_signal, scope_specs, self.scale.vert)
            self.readout.set_average(average(self.vv))
            self.readout.set_rms(rms(self.vv))
            vertical_encode:list[float] = quantize_vertical(self.vv, self.scale.vert)
            h:list[int] = resample_horizontal(vertical_encode, self.scale.hor, self.scale.fs) 
            self.scope_display.set_vector(h)
            self.scope_status = Scope_Status.TRIGGERED
            self._update_scope_status()

    def _trigger(self, force: bool = False) -> None:
        if self.serial_scope_connected:
            self.scope_status = Scope_Status.ARMED
            self._update_scope_status()
            if force:
                xx: list[int] = self.serial_scope.get_scope_force_trigger_data()
                print(xx)
            else:
                xx: list[int] = self.serial_scope.get_scope_trigger_data()
                print(xx)
            self.display_signal(xx)
            self.xx = xx
            self.nn = [n for n in range(0, len(xx))]
        else:
            self.command_input.set_error(messages.Errors.SCOPE_DISCONNECTED_ERROR)

    def auto_trigger(self) -> None:
        if self.serial_scope_connected:
            while self.trigger_running.is_set(): 
                self._trigger(force=True) 

    def single_trigger(self) -> None:
        if self.serial_scope_connected:
            self._trigger()
    
    def normal_trigger(self) -> None:
        if self.serial_scope_connected:
            while self.trigger_running.is_set():
                self._trigger()

    def start_auto_trigger(self) -> None:
        self.trigger_running.set()
        self.trigger_thread = Thread(target=self.auto_trigger)
        self.trigger_thread.start()

    def start_normal_trigger(self) -> None:
        self.trigger_running.set()
        self.trigger_thread = Thread(target=self.normal_trigger)
        self.trigger_thread.start()

    def start_single_trigger(self) -> None:
        self.trigger_running.set()
        self.trigger_thread = Thread(target=self.single_trigger)
        self.trigger_thread.start()

    def stop_auto_trigger(self) -> None: 
        self.trigger_running.clear()
        self.scope_status = Scope_Status.NEUTRAL
        self._update_scope_status()

    def set_trigger(self) -> None: 
        trigger_height:int = self.scope_display.get_trigger_level()
        trigger_voltage = get_trigger_voltage(self.scale.vert, trigger_height)
        attenuation: Optional[float] = None
        offset: Optional[float] = None
        if(self.scale.vert <= 
            constants.Scale.VERTICALS[constants.Scale.LOW_RANGE_VERTICAL_INDEX]):
            attenuation = scope_specs['attenuation']['range_low']
            offset = scope_specs['offset']['range_low']
        else:
            attenuation = scope_specs['attenuation']['range_high']
            offset = scope_specs['offset']['range_high']
        code:int = trigger_code(trigger_voltage, scope_specs['voltage_ref'], attenuation, offset)
        self.serial_scope.set_trigger_code(code)

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
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible,
                                                                    self.cursors.vert_visible))   
        else: 
            self.readout.disable_cursor_readout()

    def toggle_horizontal_cursors(self) -> None:
        self.cursors.toggle_hor()
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible:
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible,
                                                                    self.cursors.vert_visible))  
        else: 
            self.readout.disable_cursor_readout()

    def toggle_vertical_cursors(self) -> None:
        self.cursors.toggle_vert()
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.vert_visible:
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible,
                                                                    self.cursors.vert_visible))   
        else: 
            self.readout.disable_cursor_readout()

    def _set_trigger_rising_edge(self) -> None:
        self.scope_trigger.trigger_type = TriggerType.RISING_EDGE
        self.readout.set_trigger_type(self.scope_trigger.trigger_type)

    def _set_trigger_falling_edge(self) -> None:
        self.scope_trigger.trigger_type = TriggerType.FALLING_EDGE
        self.readout.set_trigger_type(self.scope_trigger.trigger_type)

    def __call__(self) -> None: self.root.mainloop()