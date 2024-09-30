#!/usr/bin/env python3

import sys
sys.path.append('..')

import unittest

from voltpeek.scale import Scale

class TestScale(unittest.TestCase):
    def setUp(self):
        self.scale = Scale()

    def test_scale_init(self):
        self.assertEqual(self.scale.fs, 62500000)
        self.assertEqual(self.scale.clock_div, 1)
        self.assertEqual(self.scale.high_range_flip, False)
        self.assertEqual(self.scale.low_range_flip, False)
        self.assertEqual(self.scale.vert, 5)

    def increment_to_max_hor_index(self):
        for _ in range(0, self.scale.MAX_HOR_INDEX-self.scale.DEFAULT_HORIZONTAL_INDEX):
            self.scale.increment_hor()

    def test_increment_hor(self):
        self.increment_to_max_hor_index() 
        self.assertEqual(self.scale.hor,1)
        self.assertEqual(self.scale._horizontal_index, self.scale.MAX_HOR_INDEX)

    def test_maximum_hor_increment(self):
        self.increment_to_max_hor_index()
        self.scale.increment_hor()
        self.assertEqual(self.scale.hor,1)

if __name__ == '__main__':
    unittest.main()