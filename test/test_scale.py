#!/usr/bin/env python3

import sys
sys.path.append('..')

from voltpeek.scale import Scale

import unittest

class TestScale(unittest.TestCase):
    def test_scale_init(self):
        scale = Scale() 
        self.assertEqual(scale.fs, 125000000)
        self.assertEqual(scale.clock_div, 1)
        self.assertEqual(scale.high_range_flip, False)
        self.assertEqual(scale.low_range_flip, False)
        self.assertEqual(scale.vert, 5)

if __name__ == '__main__':
    unittest.main()