#!/usr/bin/env python3

import sys
sys.path.append('..')

import unittest
from math import sin, pi, sqrt

from voltpeek.measurements import average, rms

tt = [i*1e-3 for i in range(0, 1000)]
vv = [sin(2*pi*100*t) for t in tt]

class TestMeasurements(unittest.TestCase):
    def test_average(self): 
        self.assertAlmostEqual(average(vv), 0.0)

    def test_rms(self):
        self.assertAlmostEqual(rms(vv), 1/sqrt(2), places=4)

if __name__ == '__main__':
    unittest.main()
