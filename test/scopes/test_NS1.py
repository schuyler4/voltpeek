import sys
sys.path.append('..')

from math import pi, sin

import unittest
from unittest.mock import patch

from voltpeek.scopes.NS1 import NS1

from test.scopes.serial_mock import SerialMock

import numpy as np

class TestNS1(unittest.TestCase):
    def setUp(self): self.ns1 = NS1()

    def test_init(self):
        self.assertEqual(self.ns1.baudrate, 115200)
        self.assertEqual(self.ns1.port, None)
        self.assertEqual(self.ns1.error, False)

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
        vv = self.ns1._reconstruct(codes, 10, offset_null=False)
        for v in vv:
            self.assertEqual(v, 0)
        codes = [(NS1.SCOPE_SPECS['resolution']/2) for _ in range(0, NS1.SCOPE_SPECS['memory_depth'])]
        vv = self.ns1._reconstruct(codes, 2, offset_null=False)
        for v in vv:
            self.assertEqual(v, 0)

    def test_FIR_filter_returns_empty_output_given_empty_input(self): self.assertEqual(self.ns1._FIR_filter([]), [])
    
    def test_FIR_filter_running_average(self):
        N = NS1.FIR_LENGTH
        test_list = np.array([1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        result_list = [(1/N)+(2/N)+(3/N), (2/N)+(3/N)+(4/N), (3/N) + (4/N), (4/N)]  
        print(self.ns1._FIR_filter(test_list))
        print(self.ns1.FIR_LENGTH)
        #print(self.ns1._FIR_filter(test_list))
        self.assertListEqual(list(self.ns1._FIR_filter(test_list)), result_list)