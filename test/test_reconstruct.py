import sys
sys.path.append('..')

import unittest

from voltpeek.reconstruct import quantize_vertical
from voltpeek.scopes.newt_scope_one import NewtScope_One
from voltpeek import constants

class TestReconstruct(unittest.TestCase):
    def test_quantize_vertical(self):
        vv = [0 for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]
        self.assertEqual(len(vv), 16384)
        pixel_list = quantize_vertical(vv, 2)
        for pixel_value in pixel_list:
            self.assertEqual(pixel_value, constants.Display.SIZE/2)
        vv = [2 for _ in range(0, NewtScope_One.SCOPE_SPECS['memory_depth'])]
        pixel_list = quantize_vertical(vv, 2)
        for pixel_value in pixel_list:
            self.assertEqual(pixel_value, (constants.Display.SIZE/2) + (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT))

        
