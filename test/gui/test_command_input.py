import unittest
from unittest.mock import MagicMock
import tkinter as tk

from voltpeek.gui.command_input import CommandInput
from voltpeek import constants

class TestCommandInput(unittest.TestCase):
    WIDTH = 800

    def setUp(self):
        self.master = tk.Tk()
        self.on_command_mock = MagicMock()
        self.command_input = CommandInput(self.master, self.on_command_mock, self.WIDTH)

    def tearDown(self):
        self.master.destroy()

    def test_initialization(self):
        self.assertIsInstance(self.command_input.input_text, tk.StringVar)
        self.assertEqual(self.command_input.command_stack, [])
        self.assertEqual(self.command_input.command_stack_pointer, 0)

    def test_on_command_enter_new_command(self):
        self.command_input.input_text.set('test_command')
        self.command_input.on_command_enter(None)
        self.on_command_mock.assert_called_once_with('test_command')
        self.assertEqual(self.command_input.command_stack[0], 'test_command')
        self.assertEqual(self.command_input.command_stack_pointer, 0)

    def test_on_command_enter_duplicate_command(self):
        self.command_input.input_text.set('test')
        self.command_input.on_command_enter(None)
        self.command_input.input_text.set('test')
        self.command_input.on_command_enter(None)
        self.assertEqual(len(self.command_input.command_stack), 1)

    def test_set_error(self):
        self.command_input.set_error('An error occurred')
        self.assertTrue(self.command_input.error)
        self.assertEqual(self.command_input.error_message, 'An error occurred')

    def test_display_error(self):
        self.command_input.set_error('error')
        self.command_input.display_error()
        self.assertEqual(self.command_input.input.cget('bg'), CommandInput.ERROR_BACKGROUND_COLOR)
        self.assertEqual(self.command_input.input_text.get(), 'error')

    def test_clear_input(self):
        self.command_input.input_text.set('Some text')
        self.command_input.clear_input()
        self.assertEqual(self.command_input.input_text.get(), '')

    def test_set_adjust_mode(self):
        self.command_input.set_adjust_mode()
        self.assertEqual(self.command_input.input.cget('state'), 'disabled')

    def test_set_command_mode(self):
        self.command_input.set_adjust_mode()
        self.command_input.set_command_mode()
        actual_state = self.command_input.input.cget('state')
        actual_bg_color = self.command_input.input.cget('bg')
        self.assertEqual(actual_state, 'normal')
        self.assertEqual(actual_bg_color, CommandInput.BACKGROUND_COLOR)
    
if __name__ == '__main__':
    unittest.main()
