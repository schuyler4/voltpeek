from typing import Callable
from enum import Enum
from threading import Thread, Event

import tkinter as tk

from voltpeek import messages
from voltpeek import constants
from voltpeek.measurements import average
from voltpeek.serial_scope import Serial_Scope
from voltpeek.scope_display import Scope_Display
from voltpeek.command_input import Command_Input
from voltpeek.readout import Readout
from voltpeek.reconstruct import reconstruct
from voltpeek.pixel_vector import quantize_vertical, resample_horizontal, FIR_filter
from voltpeek.helpers import generate_trigger_vector
from voltpeek.trigger import get_trigger_voltage, trigger_code
from voltpeek.cursors import Cursors, Cursor_Data
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

# TODO: Make this more OO
class Scale:
    max_vertical_index = len(constants.Scale.VERTICALS) - 1
    max_hor_index = len(constants.Scale.HORIZONTALS) - 1
    range_flip_index = constants.Scale.LOW_RANGE_VERTICAL_INDEX

    def __init__(self) -> None:
        self.vertical_index = constants.Scale.DEFAULT_VERTICAL_INDEX 
        self.horizontal_index = constants.Scale.DEFAULT_HORIZONTAL_INDEX
        self.high_range_flip:bool = False
        self.low_range_flip:bool = False
        self._clock_div:int = 1
        self._fs:int = 125000000

    def increment_vert(self) -> None:
        if(self.vertical_index < self.max_vertical_index): 
            self.vertical_index += 1     
            self.high_range_flip = self.vertical_index == self.range_flip_index + 1 
            self.low_range_flip = False 

    def decrement_vert(self) -> None:
        if(self.vertical_index > 0): 
            self.vertical_index -= 1
            self.low_range_flip = self.vertical_index == self.range_flip_index
            self.high_range_flip = False

    def increment_hor(self) -> None:
        if(self.horizontal_index < self.max_hor_index): self.horizontal_index += 1

    def decrement_hor(self) -> None:
        if(self.horizontal_index > 0): self.horizontal_index -= 1

    @property
    def fs(self) -> int: return self._fs

    @property
    def clock_div(self) -> int: return self._clock_div

    def get_vert(self) -> float: return constants.Scale.VERTICALS[self.vertical_index]
    
    def get_hor(self) -> float: return constants.Scale.HORIZONTALS[self.horizontal_index]

    # TODO: possibly move these methods so they can be exposed to scripting API
    def get_max_sample_rate(self, memory_depth:int) -> float:
        return memory_depth/(self.get_hor()*constants.Display.GRID_LINE_COUNT)  

    def find_lowest_clock_division(self, sample_rate:float, base_clock:float) -> int:
        for div in range(1, 65540):
            if base_clock/div <= sample_rate:
                return div
        return None

    def update_sample_rate(self, base_clock:float, memory_depth:int) -> float:
        max_sample_rate:float = self.get_max_sample_rate(memory_depth)
        self._clock_div = self.find_lowest_clock_division(max_sample_rate, base_clock)
        self._fs = int(base_clock/self._clock_div)

class User_Interface:
    def _update_scope_status(self): self.readout.set_status(self.scope_status.name)
    
    def __init__(self) -> None:
        self.scale = Scale()
        self.build_tk_root() 
        self.scope_display:Scope_Display = Scope_Display(self.root)
        self.command_input:Command_Input = Command_Input(self.root, self.process_command)
        self.readout:Readout = Readout(self.root, self.scale.get_vert(), self.scale.get_hor())
        self.readout()
        self.scope_display()
        self.command_input()
        self.mode:Mode = Mode.COMMAND
        self.command_input.set_focus()
        self.vv = None
        self.serial_scope_connected:bool = False
        self.scope_status:Scope_Status = Scope_Status.DISCONNECTED
        self.cursors = Cursors()
        self._update_scope_status()
        self.auto_trigger_running:Event = Event()
        self.connect_thread:Thread = Thread()
        self.trigger_thread:Thread = Thread()
        self._update_fs()

    def build_tk_root(self) -> None:
        self.root:tk.Tk = tk.Tk()
        self.root.title(constants.Application.NAME)
        self.root.configure(bg=constants.Window.BACKGROUND_COLOR) 
        self.root.bind('<KeyPress>', self.on_key_press)

    def on_key_press(self, event) -> None:
        if(self.mode == Mode.ADJUST_SCALE 
           or self.mode == Mode.ADJUST_TRIGGER_LEVEL or self.mode == Mode.ADJUST_CURSORS):
            if(event.keycode in constants.Keys.EXIT_COMMAND_MODE): 
                if(self.mode == Mode.ADJUST_TRIGGER_LEVEL and self.serial_scope_connected): 
                    self.set_trigger()
                self._set_command_mode()
        if(self.mode == Mode.ADJUST_SCALE):
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
        # TODO: Fix bug when cursors are not visible
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

    def _update_fs(self):
        self.scale.update_sample_rate(scope_specs['sample_rate'], scope_specs['memory_depth'])
        self.readout.set_fs(self.scale.fs)
        if self.serial_scope_connected:
            self.serial_scope.set_clock_div(self.scale.clock_div)
        print(self.scale.fs)
        print(self.scale.clock_div)

    def _update_scale(self, arithmatic_fn: Callable[[None], None]) -> None:
        arithmatic_fn()
        self.readout.update_settings(self.scale.get_vert(), self.scale.get_hor())
        if self.scale.low_range_flip and self.serial_scope_connected:
            self.serial_scope.request_low_range()
        elif self.scale.high_range_flip and self.serial_scope_connected:
            self.serial_scope.request_high_range()
        if self.vv is not None:
            fs:int = 125000000 
            v_vertical:float = self.scale.get_vert()
            h_horizontal:float = self.scale.get_hor()
            vertical_encode:list[int] = quantize_vertical(self.vv, v_vertical)
            horizontal_encode:list[int] = resample_horizontal(vertical_encode, h_horizontal, fs) 
            self.scope_display.set_vector(horizontal_encode) 
        self._update_fs()

    def _update_cursor(self, arithmatic_fn: Callable[[None], None]) -> None:
        arithmatic_fn()
        self.readout.update_cursors(self.get_cursor_dict(self.cursors.hor_visible, 
                                                         self.cursors.vert_visible))
        self.scope_display.set_cursors(self.cursors)

    def exit(self) -> None:
        if self.auto_trigger_running.is_set(): 
            self.auto_trigger_running.clear()
        exit()

    def get_commands(self): return {
            messages.Commands.EXIT_COMMAND: self.exit,
            messages.Commands.CONNECT_COMMAND: self.connect_serial_scope,
            messages.Commands.SIMU_TRIGGER_COMMAND: self.simu_trigger,    
            messages.Commands.SCALE_COMMAND: self._set_adjust_scale_mode, 
            messages.Commands.TRIGGER_COMMAND: self.trigger, 
            messages.Commands.FAKE_TRIGGER_COMMAND: self.fake_trigger,
            messages.Commands.FORCE_TRIGGER_COMMAND: self.force_trigger,
            messages.Commands.TRIGGER_LEVEL_COMMAND: self._set_adjust_trigger_level_mode,  
            messages.Commands.TOGGLE_CURS: self.toggle_cursors, 
            messages.Commands.TOGGLE_HCURS: self.toggle_horizontal_cursors, 
            messages.Commands.TOGGLE_VCURS: self.toggle_vertical_cursors,
            messages.Commands.NEXT_CURS: self.cursors.next_cursor, 
            messages.Commands.ADJUST_CURS: self._set_adjust_cursor_mode, 
            messages.Commands.AUTO_TRIGGER_COMMAND: self.start_auto_trigger, 
            messages.Commands.STOP: self.stop_auto_trigger
        }
            
    #TODO: show an error to the user if the scope does not connect
    def connect_serial_scope(self) -> None:
        def connect_worker():
            self.serial_scope.init_serial()
            self.serial_scope_connected = True
            low_range_index = constants.Scale.LOW_RANGE_VERTICAL_INDEX
            if(self.scale.get_vert() <= constants.Scale.VERTICALS[low_range_index]):
                self.serial_scope.request_low_range()
            else:
                self.serial_scope.request_high_range()
            self.scope_status = Scope_Status.NEUTRAL
            self._update_scope_status()
            self._update_fs()
        self.serial_scope = Serial_Scope(115200, '/dev/ttyACM0')
        self.scope_status = Scope_Status.CONNECTING
        self._update_scope_status()
        self.connect_thread = Thread(target=connect_worker)
        self.connect_thread.start()

    #TODO: refactor these trigger methods that are basically the same
    def force_trigger(self) -> None:
        if(self.serial_scope_connected):
            print('triggered')
            self.scope_status:Scope_Status = Scope_Status.ARMED
            self._update_scope_status()
            xx:list[int] = self.serial_scope.get_scope_force_trigger_data()
            print(xx)
            if(len(xx) > 0):
                self.vv:list[float] = reconstruct(xx, scope_specs, self.scale.get_vert())
                self.readout.set_average(average(self.vv))
                vertical_encode:list[float] = quantize_vertical(self.vv, self.scale.get_vert())
                filtered_signal:list[float] = FIR_filter(vertical_encode)
                h:list[int] = resample_horizontal(vertical_encode, 
                                                  self.scale.get_hor(), self.scale.fs) 
                self.scope_display.set_vector(h)
                self.scope_status:Scope_Status = Scope_Status.TRIGGERED
                self._update_scope_status()
        else: 
            self.command_input.set_error(messages.Errors.SCOPE_DISCONNECTED_ERROR)

    def auto_trigger(self) -> None:
        count = 0
        if(self.serial_scope_connected):
            while(self.auto_trigger_running.is_set()): self.force_trigger() 

    def start_auto_trigger(self) -> None:
        self.auto_trigger_running.set()
        self.trigger_thread = Thread(target=self.auto_trigger)
        self.trigger_thread.start()
     
    def stop_auto_trigger(self) -> None: 
        self.auto_trigger_running.clear()
        self.scope_status:Scope_Status = Scope_Status.NEUTRAL
        self._update_scope_status()

    def trigger(self) -> None:
        if(self.serial_scope_connected):
            self.scope_status:Scope_Status = Scope_Status.ARMED
            self._update_scope_status()
            fs:int = 125000000 
            xx:list[int] = self.serial_scope.get_scope_trigger_data()
            print(xx)
            self.vv:list[float] = reconstruct(xx, scope_specs, self.scale.get_vert())
            self.readout.set_average(average(self.vv))
            vertical_encode:list[float] = quantize_vertical(self.vv, self.scale.get_vert())
            hh:list[int] = resample_horizontal(vertical_encode, self.scale.get_hor(), fs) 
            self.scope_display.set_vector(hh)
            self.scope_status:Scope_Status = Scope_Status.TRIGGERED
            self._update_scope_status()
        else: self.command_input.set_error(messages.Errors.SCOPE_DISCONNECTED_ERROR)

    def simu_trigger(self) -> None:
        if(self.serial_scope_connected):
            xx:list[int] = self.serial_scope.get_simulated_vector() 
            self.vv:list[float] = reconstruct(xx, scope_specs, self.scale.get_vert())
            self.readout.set_average(average(self.vv))
            v_vertical:float = self.scale.get_vert()
            self.scope_display.set_vector(quantize_vertical(self.vv, self.scale.get_vert()))
        else: self.command_input.set_error(messages.Errors.SCOPE_DISCONNECTED_ERROR) 

    def fake_trigger(self) -> None: 
        fs:int = 50000
        t_horizontal:float = self.scale.get_hor()
        v_vertical:float = self.scale.get_vert()
        self.vv:list[float] = generate_trigger_vector(t_horizontal)
        self.readout.set_average(average(self.vv))
        vertical_encoding:list[int] = quantize_vertical(self.vv, v_vertical)
        self.scope_display.set_vector(quantize_vertical(self.vv, v_vertical)) 
    
    def set_trigger(self) -> None: 
        trigger_height:int = self.scope_display.get_trigger_level()
        trigger_voltage = get_trigger_voltage(self.scale.get_vert(), trigger_height)
        print(trigger_voltage)
        attenuation:float = None
        offset:float = None
        if(self.scale.get_vert() <= 
            constants.Scale.VERTICALS[constants.Scale.LOW_RANGE_VERTICAL_INDEX]):
            attenuation = scope_specs['attenuation']['range_low']
            offset = scope_specs['offset']['range_low']
        else:
            attenuation = scope_specs['attenuation']['range_high']
            offset = scope_specs['offset']['range_high']
        code:int = trigger_code(trigger_voltage, scope_specs['voltage_ref'], attenuation, offset)
        print(code)
        self.serial_scope.set_trigger_code(code)

    def get_cursor_dict(self, horizontal:bool, vertical:bool) -> Cursor_Data:
        h1:str = self.cursors.get_hor1_voltage(self.scale.get_vert()) if horizontal else ''
        h2:str = self.cursors.get_hor2_voltage(self.scale.get_vert()) if horizontal else '' 
        hdelta:str = self.cursors.get_delta_voltage(self.scale.get_vert()) if horizontal else ''
        v1:str = self.cursors.get_vert1_time(self.scale.get_hor()) if vertical else ''
        v2:str = self.cursors.get_vert2_time(self.scale.get_hor()) if vertical else ''
        vdelta:str = self.cursors.get_delta_time(self.scale.get_hor()) if vertical else ''
        return { 'h1': h1, 'h2': h2, 'hdelta': hdelta, 'v1': v1, 'v2': v2, 'vdelta': vdelta }
    
    def toggle_cursors(self) -> None:
        self.cursors.toggle() 
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible or self.cursors.vert_visible: 
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible,
                                                                    self.cursors.vert_visible))     
        else: self.readout.disable_cursor_readout()

    def toggle_horizontal_cursors(self) -> None:
        self.cursors.toggle_hor()
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.hor_visible:
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible,
                                                                    self.cursors.vert_visible))     
        else: self.readout.disable_cursor_readout()

    def toggle_vertical_cursors(self) -> None:
        self.cursors.toggle_vert()
        self.scope_display.set_cursors(self.cursors)
        if self.cursors.vert_visible:
            self.readout.enable_cursor_readout(self.get_cursor_dict(self.cursors.hor_visible,
                                                                    self.cursors.vert_visible))     
        else: self.readout.disable_cursor_readout()

    def __call__(self) -> None: self.root.mainloop()
