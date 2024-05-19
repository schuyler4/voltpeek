#!/usr/bin/env python3

import sys
sys.path.append('..')

from voltpeek.trigger import Trigger, TriggerType

import unittest

class TestTrigger(unittest.TestCase):
    def test_trigger_init(self):
        trigger = Trigger()
        self.assertEqual(trigger.trigger_height, 0)
        self.assertEqual(trigger.trigger_type, TriggerType.RISING_EDGE)

    def test_set_trigger_type(self):
        trigger = Trigger()
        trigger._trigger_type = TriggerType.FALLING_EDGE
        self.assertEqual(trigger._trigger_type, TriggerType.FALLING_EDGE)

if __name__ == '__main__':
    unittest.main()