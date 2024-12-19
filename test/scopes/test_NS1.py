import sys
sys.path.append('..')

from math import pi, sin

import unittest
from unittest.mock import patch

from voltpeek.scopes.NS1 import NS1

from test.scopes.serial_mock import SerialMock

class TestNewtScope_One(unittest.TestCase):
    def setUp(self): self.newt_scope_one = NS1()

    def test_init(self):
        self.assertEqual(self.newt_scope_one.baudrate, 115200)
        self.assertEqual(self.newt_scope_one.port, None)
        self.assertEqual(self.newt_scope_one.error, False)

    '''
    @patch('voltpeek.scopes.NS1.Serial', new=SerialMock)
    def test_connect(self):
        self.newt_scope_one.connect()
        self.assertTrue(self.newt_scope_one.serial_port.created, True)
        self.assertEqual(self.newt_scope_one.serial_port.baudrate, 115200)
        self.assertEqual(self.newt_scope_one.serial_port.timeout, 0)

    @patch('voltpeek.scopes.NS1.serial_port', new=SerialMock)
    def test_read_glob_data(self):
        self.newt_scope_one.connect()
        codes = self.newt_scope_one.read_glob_data()
        for code in codes:
            self.assertEqual(code, 300)
    '''

    def test_reconstruct(self):
        codes = [(NS1.SCOPE_SPECS['resolution']/2) for _ in range(0, NS1.SCOPE_SPECS['memory_depth'])]
        vv = self.newt_scope_one._reconstruct(codes, 10, offset_null=False)
        for v in vv:
            self.assertEqual(v, 0)
        codes = [(NS1.SCOPE_SPECS['resolution']/2) for _ in range(0, NS1.SCOPE_SPECS['memory_depth'])]
        vv = self.newt_scope_one._reconstruct(codes, 2, offset_null=False)
        for v in vv:
            self.assertEqual(v, 0)

    def test_FIR_filter_returns_empty_output_given_empty_input(self): self.assertEqual(self.newt_scope_one._FIR_filter([]), [])
    
    def test_FIR_filter_running_average(self):
        N = NS1.FIR_LENGTH
        test_list = [1, 2, 3, 4]
        result_list = [(1/N)+(2/N)+(3/N)+(4/N), (2/N)+(3/N)+(4/N), (3/N) + (4/N), (4/N)]  
        self.assertListEqual(list(self.newt_scope_one._FIR_filter(test_list)), result_list)