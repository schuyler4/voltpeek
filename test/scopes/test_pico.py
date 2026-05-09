import sys
import unittest
from unittest.mock import patch, MagicMock

from voltpeek.scopes.pico import Pico

class TestPico(unittest.TestCase):
    def setUp(self):
        self.pico = Pico()

    @patch('voltpeek.scopes.pico.list_ports.comports')
    def test_pico_connected_true(self, mock_comports):
        mock_port1 = MagicMock()
        mock_port1.vid = 0x1234

        mock_port2 = MagicMock()
        mock_port2.vid = Pico.PICO_VID

        mock_comports.return_value = [mock_port1, mock_port2]

        self.assertTrue(self.pico.pico_connected())

    @patch('voltpeek.scopes.pico.list_ports.comports')
    def test_pico_connected_false(self, mock_comports):
        mock_port1 = MagicMock()
        mock_port1.vid = 0x1234

        mock_port2 = MagicMock()
        mock_port2.vid = 0x5678

        mock_comports.return_value = [mock_port1, mock_port2]

        self.assertFalse(self.pico.pico_connected())

    @patch('voltpeek.scopes.pico.list_ports.comports')
    def test_find_pico_serial_port_found(self, mock_comports):
        mock_port = MagicMock()
        mock_port.vid = Pico.PICO_VID
        mock_port.device = '/dev/ttyACM0'

        mock_comports.return_value = [mock_port]

        self.assertEqual(self.pico.find_pico_serial_port(), '/dev/ttyACM0')

    @patch('voltpeek.scopes.pico.list_ports.comports')
    def test_find_pico_serial_port_not_found(self, mock_comports):
        mock_port = MagicMock()
        mock_port.vid = 0x1234
        mock_port.device = '/dev/ttyACM0'

        mock_comports.return_value = [mock_port]

        self.assertIsNone(self.pico.find_pico_serial_port())

    @patch('voltpeek.scopes.pico.list_ports.comports')
    def test_find_scope_ports(self, mock_comports):
        mock_port1 = MagicMock()
        mock_port1.vid = Pico.PICO_VID
        mock_port1.device = '/dev/ttyACM0'

        mock_port2 = MagicMock()
        mock_port2.vid = 0x1234
        mock_port2.device = '/dev/ttyACM1'

        mock_port3 = MagicMock()
        mock_port3.vid = Pico.PICO_VID
        mock_port3.device = '/dev/ttyACM2'

        mock_comports.return_value = [mock_port1, mock_port2, mock_port3]

        self.assertEqual(Pico.find_scope_ports(), ['/dev/ttyACM0', '/dev/ttyACM2'])

if __name__ == '__main__':
    unittest.main()
