import unittest
import tkinter as tk
from voltpeek.cursors import Cursors
from voltpeek import constants
from voltpeek.trigger import TriggerType
import numpy as np

from voltpeek.gui.scope_display import Scope_Display

class TestScopeDisplay(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.cursors = Cursors()
        self.scope_display = Scope_Display(self.root, self.cursors)

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        self.assertIsInstance(self.scope_display.canvas, tk.Canvas)
        self.assertEqual(int(self.scope_display.canvas['height']), constants.Display.SIZE)
        self.assertEqual(int(self.scope_display.canvas['width']), constants.Display.SIZE)
        self.assertEqual(self.scope_display.canvas['bg'], '#000000')

    def test_hex_string_from_rgb(self):
        self.assertEqual(self.scope_display._hex_string_from_rgb((255, 0, 0)), '#ff0000')
        self.assertEqual(self.scope_display._hex_string_from_rgb((0, 255, 0)), '#00ff00')
        self.assertEqual(self.scope_display._hex_string_from_rgb((0, 0, 255)), '#0000ff')

    def test_set_vector(self):
        test_vector = [1, 2, 3, 4, 5]
        self.scope_display.set_vector(test_vector)
        self.assertEqual(self.scope_display.vector, test_vector)

    def test_set_trigger_level(self):
        self.scope_display.set_trigger_level(100)
        self.assertEqual(self.scope_display._trigger_level, 100)

    def test_get_trigger_voltage(self):
        self.scope_display.set_trigger_level(100)
        vertical_setting = 1.0
        expected_voltage = (constants.Display.SIZE - 100 - (constants.Display.SIZE/2)) * (vertical_setting / 
                           (constants.Display.SIZE/constants.Display.GRID_LINE_COUNT))
        self.assertAlmostEqual(self.scope_display.get_trigger_voltage(vertical_setting), expected_voltage)

    def test_increment_trigger_level(self):
        initial_level = 100
        self.scope_display.set_trigger_level(initial_level)
        self.scope_display.increment_trigger_level_fine()
        self.assertEqual(self.scope_display._trigger_level, initial_level - self.scope_display.FINE_STEP)

    def test_decrement_trigger_level(self):
        initial_level = 100
        self.scope_display.set_trigger_level(initial_level)
        self.scope_display.decrement_trigger_level_fine()
        self.assertEqual(self.scope_display._trigger_level, initial_level + self.scope_display.FINE_STEP)

    def test_image_map(self):
        self.scope_display.set_vector([constants.Display.SIZE//2] * constants.Display.SIZE)
        image_map = self.scope_display.image_map
        self.assertEqual(len(image_map), constants.Display.SIZE)
        self.assertEqual(len(image_map[0]), constants.Display.SIZE)
        self.assertIn(self.scope_display.SIGNAL_COLOR, [pixel for row in image_map for pixel in row])

if __name__ == '__main__':
    unittest.main()