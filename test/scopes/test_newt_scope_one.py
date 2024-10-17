import sys
import os
import time
import subprocess
import tempfile
import shutil
sys.path.append('..')

import unittest

from voltpeek.scopes.newt_scope_one import NewtScope_One

class TestNewtScope_One(unittest.TestCase):
    def setUp(self):
        self.newt_scope_one = NewtScope_One()

    def test_newt_scope_init(self):
        self.assertEqual(self.newt_scope_one.baudrate, 115200)
        self.assertEqual(self.newt_scope_one.port, None)
        self.assertEqual(self.newt_scope_one.error, False)

    def test_inverse_quantize(self):
        LSB = NewtScope_One.SCOPE_SPECS['voltage_ref']/NewtScope_One.SCOPE_SPECS['resolution']
        self.assertAlmostEqual(self.newt_scope_one.inverse_quantize(255, 
                                                              NewtScope_One.SCOPE_SPECS['resolution'], 
                                                              NewtScope_One.SCOPE_SPECS['voltage_ref']), 
                                                              NewtScope_One.SCOPE_SPECS['voltage_ref'] - LSB)

    def test_zero(self):
        self.assertEqual(self.newt_scope_one._zero(0.5), 0)    

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
