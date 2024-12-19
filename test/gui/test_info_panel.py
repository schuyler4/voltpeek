import unittest
import tkinter as tk
from unittest.mock import Mock, patch
from voltpeek.commands import COMMAND_DOCS
from voltpeek.gui.info_panel import InfoPanel

class TestInfoPanel(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.info_panel = InfoPanel(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        self.assertIsInstance(self.info_panel.master, tk.Tk)
        self.assertIsInstance(self.info_panel.frame, tk.Frame)
        self.assertEqual(len(self.info_panel.info_strings), len(COMMAND_DOCS))
        self.assertFalse(self.info_panel.visible)

    def test_call(self):
        with patch('tkinter.Label') as mock_label:
            self.info_panel()
            self.assertEqual(mock_label.call_count, len(COMMAND_DOCS))

    def test_hide(self):
        self.info_panel.show()
        self.info_panel.hide()
        self.assertFalse(self.info_panel.visible)
        self.assertFalse(self.info_panel.frame.winfo_viewable())

    def test_visible_property(self):
        self.assertFalse(self.info_panel.visible)
        self.info_panel.show()
        self.assertTrue(self.info_panel.visible)
        self.info_panel.hide()
        self.assertFalse(self.info_panel.visible)

    def test_frame_attributes(self):
        self.assertEqual(self.info_panel.frame['bg'], InfoPanel.BACKGROUND_COLOR)
        self.assertEqual(self.info_panel.frame['highlightbackground'], InfoPanel.BORDER_COLOR)
        self.assertEqual(self.info_panel.frame['highlightthickness'], InfoPanel.BORDER_THICKNESS)

    def test_info_strings_content(self):
        for i, (key, value) in enumerate(COMMAND_DOCS.items()):
            expected = f"{key}: {value}"
            self.assertEqual(self.info_panel.info_strings[i].get(), expected)

if __name__ == '__main__':
    unittest.main()
