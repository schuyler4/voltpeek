from typing import Optional, Callable, Dict, Any
from enum import Enum
from threading import Thread, Lock
from functools import wraps

from serial.serialutil import PortNotOpenError

class ScopeAction(Enum):
    CONNECT = 0
    TRIGGER = 1
    FORCE_TRIGGER = 2
    SET_CLOCK_DIV = 3
    SET_TRIGGER_LEVEL = 4
    SET_RANGE = 5
    STOP = 6
    SET_CAL_OFFSETS = 7
    READ_CAL_OFFSETS = 8
    SET_RISING_EDGE_TRIGGER = 9
    SET_FALLING_EDGE_TRIGGER = 10
    SET_AMPLIFIER_GAIN = 11

def scope_action_handler(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs) 
        self._action_complete = True
        self._data_available.release()
        return result
    return wrapper

class ScopeInterface:
    def __init__(self, scope):
        self._scope_connected: bool = False
        self._xx: Optional[list[float]] = None
        self._calibration_ints: list[int] = None
        self._scope = scope() 
        self._data_available: Lock = Lock()
        self._action: ScopeAction = None
        self._action_complete: bool = True
        self._value: Optional[int] = None
        self._stop_flag = False
        self._full_scale = 10
        self._fs: Optional[float] = None
        self._disconnected_error: bool = False

        # Action handler mapping
        self._action_handlers: Dict[ScopeAction, Callable] = {
            ScopeAction.CONNECT: self._connect_scope,
            ScopeAction.FORCE_TRIGGER: self._force_trigger,
            ScopeAction.TRIGGER: self._trigger,
            ScopeAction.SET_CLOCK_DIV: self._set_clock_div,
            ScopeAction.SET_TRIGGER_LEVEL: self._set_trigger_level,
            ScopeAction.STOP: self.stop_trigger,
            ScopeAction.READ_CAL_OFFSETS: self._read_cal_offsets,
            ScopeAction.SET_CAL_OFFSETS: self._set_cal_offsets,
            ScopeAction.SET_RANGE: self._set_range,
            ScopeAction.SET_RISING_EDGE_TRIGGER: self._set_rising_edge_trigger,
            ScopeAction.SET_FALLING_EDGE_TRIGGER: self._set_falling_edge_trigger,
            ScopeAction.SET_AMPLIFIER_GAIN: self._set_amplifier_gain,
        }

    def _scope_available(self, scope_action: Callable):
        try:
            scope_action()
        except (Exception, OSError) as _:
            self._disconnected_error = True

    @scope_action_handler
    def _connect_scope(self):
        self._scope.connect()
        self._scope_connected = True

    @scope_action_handler
    def _force_trigger(self):
        self._xx = self._scope.get_scope_force_trigger_data(self._full_scale)
        if self._xx is None:
            self._disconnected_error = True

    @scope_action_handler
    def _trigger(self):
        self._xx = self._scope.get_scope_trigger_data(self._full_scale)
        if self._xx is None:
            self._disconnected_error = True

    @scope_action_handler
    def _set_clock_div(self):
        self._scope.set_clock_div(self._value)

    @scope_action_handler
    def _set_range(self):
        self._scope.set_range(self._full_scale)

    @scope_action_handler
    def _set_amplifier_gain(self):
        self._scope.set_amplifier_gain(self._full_scale)

    @scope_action_handler
    def _set_trigger_level(self):
        self._scope.set_trigger_voltage(self._value, self._full_scale)

    @scope_action_handler
    def _read_cal_offsets(self):
        self._calibration_ints = self._scope.read_calibration_offsets()
        if self._calibration_ints is None:
            self._disconnected_error = True

    @scope_action_handler
    def _set_cal_offsets(self): self._scope.set_calibration_offsets(self._full_scale)

    @scope_action_handler
    def _set_rising_edge_trigger(self): self._scope.set_rising_edge_trigger()

    @scope_action_handler
    def _set_falling_edge_trigger(self): self._scope.set_falling_edge_trigger()

    def run(self):
        if not self._action_complete and self._action in self._action_handlers:
            thread = Thread(target=lambda: self._scope_available(self._action_handlers[self._action]))
            thread.start()

    @property
    def data_available(self) -> bool: return not self._data_available.locked()

    @property
    def xx(self) -> Optional[list[float]]: return self._xx

    @property
    def value(self) -> Optional[int]: return self._value

    @property
    def calibration_ints(self) -> Optional[list[int]]: return self._calibration_ints

    @property
    def stopped(self) -> bool: return self._scope.stopped

    @property
    def stop_flag(self) -> bool: return self._stop_flag

    @property
    def scope(self): return self._scope 

    @property
    def full_scale(self) -> float: return self._full_scale

    @property
    def disconnected_error(self) -> bool: return self._disconnected_error

    def set_value(self, new_value: int) -> None:
        if self.data_available:
            self._value = new_value

    def set_full_scale(self, new_full_scale: float) -> None: self._full_scale = new_full_scale

    def set_scope_action(self, new_scope_action: ScopeAction):
        if self.data_available:
            self._action = new_scope_action
            self._action_complete = False
            self._data_available.acquire()
        
    def stop_trigger(self): 
        self._stop_flag = True
        self._scope.stop_trigger()

    def reset_stop_flag(self): self._stop_flag = False

    def clear_disconnected_error(self): self._disconnected_error = False

    @property
    def fs(self) -> Optional[float]: return self._fs

    @fs.setter
    def fs(self, new_fs: float): self._fs = new_fs