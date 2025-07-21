import unittest

from voltpeek.interface import UserInterface, Mode

class TestUserInterface(unittest.TestCase):
    def setUp(self):
        self.interface = UserInterface(debug=True)

    def test_interface_init(self):
        self.assertEqual(self.interface.debug, True)
        self.assertEqual(self.interface._last_fs, 62500000)
        self.assertEqual(self.interface._connect_initiated, False)
        self.assertEqual(self.interface._record_running, False)
        self.assertEqual(self.interface._calibration, False)
        self.assertEqual(self.interface._triggered, False)
        self.assertEqual(self.interface._scope_interfaces, [])
        self.assertEqual(self.interface.mode, Mode.COMMAND)