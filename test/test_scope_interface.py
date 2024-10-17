from enum import Enum
import time
import sys
sys.path.append('..')

import unittest

from voltpeek.scopes.newt_scope_one import NewtScope_One
from voltpeek.scope_interface import ScopeInterface, ScopeAction

class MockRange(Enum):
    LOW = 0
    HIGH = 1

class MockTrigger(Enum):
    RISING = 0
    FALLING = 1

class MockNewtScopeOne:
    def __init__(self):
        self.connected = False
        self.range = MockRange.LOW
        self.trigger = MockTrigger.RISING
        self.trigger_code = 0
        self.clock_div = 1
        self.calibration_offsets = [0 for _ in range(0, 4)]
        self.stop_flag = False

    def connect(self): self.connected = True

    def get_scope_trigger_data(self, full_scale: float) -> list[float]:
        for _ in range(0, 10):
            if self.stop_flag: 
                return None
            time.sleep(0.01)
        return [0 for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]
    
    def get_scope_force_trigger_data(self, full_scale: float) -> list[float]:
        return [0 for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]

    def set_range(self, full_scale: float) -> None:
        self.range = MockRange.HIGH if full_scale > NewtScope_One.LOW_RANGE_THRESHOLD else MockRange.LOW

    def set_trigger_voltage(self, trigger_voltage: float, full_scale: float) -> None:
        if full_scale <= NewtScope_One.LOW_RANGE_THRESHOLD:
            attenuation = NewtScope_One.SCOPE_SPECS['attenuation']['range_low']
        else: 
            attenuation = NewtScope_One.SCOPE_SPECS['attenuation']['range_high']
        # TODO: Add error handling for non-compliant trigger voltages
        max_input_voltage: float = (NewtScope_One.SCOPE_SPECS['voltage_ref']/attenuation)/2   
        self.trigger_code = int(((trigger_voltage + max_input_voltage)/(max_input_voltage*2))*(NewtScope_One.SCOPE_SPECS['trigger_resolution']-1))

    def set_clock_div(self, clock_div: int) -> None:
        self.clock_div = clock_div

    def set_calibration_offsets(self, calibration_offsets_str: str) -> None:
        self.calibration_offsets = [int(offset) for offset in calibration_offsets_str.split(',')]

    def set_rising_edge_trigger(self) -> None:
        self.trigger = MockTrigger.RISING

    def set_falling_edge_trigger(self) -> None:
        self.trigger = MockTrigger.FALLING

    def stop(self) -> None:
        self.stop_flag = True
    
    def read_calibration_offsets(self) -> list[int]:
        return [0 for _ in range(0, 4)]
    
    def disconnect(self) -> None: self.connected = False
    
class TestScopeInterface(unittest.TestCase):
    def setUp(self):
        self.scope = MockNewtScopeOne
        self.scope_interface = ScopeInterface(self.scope)

    def test_scope_class(self):
        self.assertEqual(self.scope, MockNewtScopeOne)
        self.assertTrue(isinstance(self.scope, type))
        self.assertEqual(self.scope.__name__, 'MockNewtScopeOne')

    def test_scope_interface_init(self):
        self.assertEqual(self.scope_interface._scope_connected, False)
        self.assertEqual(self.scope_interface._xx, None)
        self.assertEqual(self.scope_interface._calibration_ints, None)
        self.assertEqual(self.scope_interface._action, None)
        self.assertEqual(self.scope_interface._action_complete, True)
        self.assertEqual(self.scope_interface._value, None)
        self.assertEqual(self.scope_interface._stop_flag, False)
        self.assertEqual(self.scope_interface._full_scale, 10)

    def test_scope_interface_connect(self):
        self.scope_interface.set_scope_action(ScopeAction.CONNECT)
        self.scope_interface.run()
        self.assertTrue(self.scope_interface._scope.connected)
        self.assertTrue(self.scope_interface._scope_connected)
        self.assertTrue(self.scope_interface._action_complete)
        self.assertFalse(self.scope_interface._data_available.locked())

    def test_scope_interface_trigger(self):
        self.scope_interface.set_scope_action(ScopeAction.TRIGGER)
        self.scope_interface.run()
        ticks = 0
        while not self.scope_interface._action_complete:
            time.sleep(0.01) 
            ticks += 1
        self.assertTrue(ticks > 0)
        self.assertLess(ticks, 12)
        self.assertEqual(len(self.scope_interface._xx), NewtScope_One.SCOPE_SPECS['memory_depth'])
        self.assertEqual(self.scope_interface._xx, [0 for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])])
        self.assertTrue(self.scope_interface._action_complete)
        self.assertFalse(self.scope_interface._data_available.locked())

    def test_scope_interface_force_trigger(self):
        self.scope_interface.set_scope_action(ScopeAction.FORCE_TRIGGER)
        self.scope_interface.run()
        self.assertEqual(len(self.scope_interface._xx), NewtScope_One.SCOPE_SPECS['memory_depth'])
        self.assertEqual(self.scope_interface._xx, [0 for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])])
        self.assertTrue(self.scope_interface._action_complete)
        self.assertFalse(self.scope_interface._data_available.locked())

    def test_scope_interface_set_clock_div(self):
        self.scope_interface.set_value(2)
        self.scope_interface.set_scope_action(ScopeAction.SET_CLOCK_DIV)
        self.scope_interface.run()
        self.assertTrue(self.scope_interface._action_complete)
        self.assertFalse(self.scope_interface._data_available.locked())
        self.assertEqual(self.scope_interface._scope.clock_div, 2)

    def test_scope_interface_set_high_range(self):
        self.scope_interface.set_value(NewtScope_One.LOW_RANGE_THRESHOLD + 1)
        self.scope_interface.set_scope_action(ScopeAction.SET_RANGE)
        self.scope_interface.run()
        self.assertTrue(self.scope_interface._action_complete)
        self.assertFalse(self.scope_interface._data_available.locked())
        self.assertEqual(self.scope_interface._scope.range, MockRange.HIGH)

    def test_scope_interface_set_low_range(self):
        self.scope_interface.set_value(NewtScope_One.LOW_RANGE_THRESHOLD - 1)
        self.scope_interface.set_scope_action(ScopeAction.SET_RANGE)
        self.scope_interface.run()
        self.assertTrue(self.scope_interface._action_complete)
        self.assertFalse(self.scope_interface._data_available.locked())
        self.assertEqual(self.scope_interface._scope.range, MockRange.LOW)