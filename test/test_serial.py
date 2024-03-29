#!/usr/bin/env python3

import sys
sys.path.append('..')

import unittest
from unittest.mock import Mock

from sigpeek.serial_scope import Serial_Scope

class Test_Serial_Scope(unittest.TestCase):
    def test_create_serial(self):
        serial_scope = Serial_Scope(9600, 'COM3')
        self.assertEqual(serial_scope.baudrate, 9600)
        self.assertEqual(serial_scope.port, 'COM3')
        self.assertFalse(serial_scope.error)

    def test_read_serial(self):
        serial_scope = Serial_Scope(9600, 'COM3') 
        port = Mock()

if __name__ == '__main__':
    unittest.main()
