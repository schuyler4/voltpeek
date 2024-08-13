from typing import Optional
from enum import Enum
from threading import Thread, Event, Lock

from voltpeek.scopes.newt_scope_one import NewtScope_One

class ScopeAction(Enum):
    CONNECT = 0
    TRIGGER = 1
    FORCE_TRIGGER = 2
    SET_CLOCK_DIV = 3
    SET_HIGH_RANGE = 4
    SET_LOW_RANGE = 5
    SET_TRIGGER_LEVEL = 6
    STOP = 7
    SET_CAL_OFFSETS = 7
    READ_CAL_OFFSETS = 8
    SET_RANGE = 9

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

    def _connect_scope(self):
        self._scope.connect()
        self._scope_connected = True
        self._action_complete = True
        self._data_available.release()

    def _force_trigger(self):
        self._xx: list[int] = self._scope.get_scope_force_trigger_data(self._full_scale)
        self._action_complete = True
        self._data_available.release()

    def _trigger(self):
        self._xx: list[int] = self._scope.get_scope_trigger_data(self._full_scale)
        self._action_complete = True
        self._data_available.release()

    def _set_clock_div(self):
        self._scope.set_clock_div(self._value)
        self._action_complete = True
        self._data_available.release()

    def _set_range(self):
        self._scope.set_range(self._value)
        self._action_complete = True
        self._data_available.release()

    def _set_trigger_level(self):
        self._scope.set_trigger_voltage(self._value, self._full_scale)
        self._action_complete = True
        self._data_available.release()

    def _read_cal_offsets(self):
        self._calibration_ints = self._scope.read_calibration_offsets()
        self._action_complete = True
        self._data_available.release()
    
    def _set_cal_offsets(self):
        self._scope.set_calibration_offsets(self._value)
        self._action_complete = True
        self._data_available.release()

    def run(self):
        if self._action == ScopeAction.CONNECT and not self._action_complete:
            thread: Thread = Thread(target=self._connect_scope)   
        if self._action == ScopeAction.FORCE_TRIGGER and not self._action_complete:
            thread: Thread = Thread(target=self._force_trigger)
        if self._action == ScopeAction.TRIGGER and not self._action_complete:
            thread: Thread = Thread(target=self._trigger)
        if self._action == ScopeAction.SET_CLOCK_DIV and not self._action_complete:
            thread: Thread = Thread(target=self._set_clock_div)
        if self._action == ScopeAction.SET_TRIGGER_LEVEL and not self._action_complete:
            thread: Thread = Thread(target=self._set_trigger_level)
        if self._action == ScopeAction.STOP and not self._action_complete:
            thread: Thread = Thread(target=self.stop_trigger) 
        if self._action == ScopeAction.READ_CAL_OFFSETS and not self._action_complete:
            thread: Thread = Thread(target=self._read_cal_offsets)
        if self._action == ScopeAction.SET_CAL_OFFSETS and not self._action_complete:
            thread: Thread = Thread(target=self._set_cal_offsets)
        if self._action == ScopeAction.SET_RANGE and not self._action_complete:
            thread: Thread = Thread(target=self._set_range)
        thread.start()

    @property 
    def data_available(self): return not self._data_available.locked()

    @property
    def xx(self): return self._xx

    @property
    def value(self): return self._value

    @property
    def calibration_ints(self): return self._calibration_ints

    @property
    def stopped(self): return self._scope.stopped

    @property
    def stop_flag(self): return self._stop_flag

    @property
    def scope(self): return self._scope 

    @property
    def full_scale(self): return self._full_scale

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

    def reset_stop_flag(self):
        self._stop_flag = False