import sys
sys.path.append('..')

from math import pi, sin

import unittest
from unittest.mock import patch

from voltpeek.scopes.NS1 import NewtScope_One

from scopes.serial_mock import SerialMock

class TestNewtScope_One(unittest.TestCase):
    def setUp(self): self.newt_scope_one = NewtScope_One()

    def test_init(self):
        self.assertEqual(self.newt_scope_one.baudrate, 115200)
        self.assertEqual(self.newt_scope_one.port, None)
        self.assertEqual(self.newt_scope_one.error, False)

    @patch('voltpeek.scopes.newt_scope_one.Serial', new=SerialMock)
    def test_connect(self):
        self.newt_scope_one.connect()
        self.assertTrue(self.newt_scope_one.serial_port.created, True)
        self.assertEqual(self.newt_scope_one.serial_port.baudrate, 115200)
        self.assertEqual(self.newt_scope_one.serial_port.timeout, 0)

    @patch('voltpeek.scopes.newt_scope_one.Serial', new=SerialMock)
    def test_read_glob_data(self):
        self.newt_scope_one.connect()
        codes = self.newt_scope_one.read_glob_data()
        for code in codes:
            self.assertEqual(code, 300)

    def test_inverse_quantize(self):
        LSB = NewtScope_One.SCOPE_SPECS['voltage_ref']/NewtScope_One.SCOPE_SPECS['resolution']
        self.assertAlmostEqual(self.newt_scope_one.inverse_quantize(255, 
                                                              NewtScope_One.SCOPE_SPECS['resolution'], 
                                                              NewtScope_One.SCOPE_SPECS['voltage_ref']), 
                                                              NewtScope_One.SCOPE_SPECS['voltage_ref'] - LSB)

    def test_zero(self): self.assertEqual(self.newt_scope_one._zero(0.5), 0)    

    def test_reamplify(self):
        gain = NewtScope_One.SCOPE_SPECS['attenuation']['range_high']
        self.assertEqual(self.newt_scope_one._reamplify(1, gain), (1/gain))
        gain = NewtScope_One.SCOPE_SPECS['attenuation']['range_low']
        self.assertEqual(self.newt_scope_one._reamplify(1, gain), (1/gain))

    def test_reconstruct(self):
        codes = [(NewtScope_One.SCOPE_SPECS['resolution']/2) for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]
        vv = self.newt_scope_one._reconstruct(codes, 10, offset_null=False)
        for v in vv:
            self.assertEqual(v, 0)
        codes = [(NewtScope_One.SCOPE_SPECS['resolution']/2) for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]
        vv = self.newt_scope_one._reconstruct(codes, 2, offset_null=False)
        for v in vv:
            self.assertEqual(v, 0)

    def test_FIR_filter_returns_empty_output_given_empty_input(self): self.assertEqual(self.newt_scope_one._FIR_filter([]), [])
    
    def test_FIR_filter_running_average(self):
        N = NewtScope_One.FIR_LENGTH
        test_list = [1, 2, 3, 4]
        result_list = [(1/N)+(2/N)+(3/N)+(4/N), (2/N)+(3/N)+(4/N), (3/N) + (4/N), (4/N)]  
        self.assertListEqual(list(self.newt_scope_one._FIR_filter(test_list)), result_list)