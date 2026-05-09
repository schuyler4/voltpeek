import sys
sys.path.append('..')

import unittest

from voltpeek.helpers import engineering_units, three_sig_figs, negative_base10_encode, negative_base10_decode, pad_zero

class TestHelpers(unittest.TestCase):
    def test_three_sig_figs(self):
        self.assertEqual(three_sig_figs(0.1111), 0.111)
        self.assertEqual(three_sig_figs(1234), 1230)
        self.assertEqual(three_sig_figs(1283), 1280)
        self.assertEqual(three_sig_figs(0.9999), 1.000)
        self.assertEqual(three_sig_figs(-4.888), -4.89)

    def test_engineering_units_mega(self):
        self.assertEqual(engineering_units(9999999), '9.999999M')
        self.assertEqual(engineering_units(99999999), '99.999999M')
        self.assertEqual(engineering_units(999999999), '999.999999M')
        self.assertEqual(engineering_units(100000000), '100.0M')
        self.assertEqual(engineering_units(10000000), '10.0M')
        self.assertEqual(engineering_units(1000000), '1.0M')

    def test_engineering_units_kilo(self):
        self.assertEqual(engineering_units(9999), '9.999k')
        self.assertEqual(engineering_units(99999), '99.999k')
        self.assertEqual(engineering_units(999999), '999.999k')
        self.assertEqual(engineering_units(100000), '100.0k')
        self.assertEqual(engineering_units(10000), '10.0k')
        self.assertEqual(engineering_units(1000), '1.0k')

    def test_engineering_units_millie(self):
        self.assertEqual(engineering_units(0.1), '100.0m')
        self.assertEqual(engineering_units(0.01), '10.0m')
        self.assertEqual(engineering_units(0.001), '1.0m')
        self.assertEqual(engineering_units(0.9), '900.0m')
        self.assertEqual(engineering_units(0.09), '90.0m')
        self.assertEqual(engineering_units(0.009), '9.0m')
        self.assertEqual(engineering_units(0.0049), '4.9m')

    def test_engineering_units_micro(self):
        self.assertEqual(engineering_units(0.0001), '100.0u')
        self.assertEqual(engineering_units(0.00001), '10.0u')
        self.assertEqual(engineering_units(0.000001), '1.0u')
        self.assertEqual(engineering_units(0.000990), '990.0u')
        self.assertEqual(engineering_units(0.000099), '99.0u')
        self.assertEqual(engineering_units(0.000009), '9.0u')

    def test_engineering_units_nano(self):
        self.assertEqual(engineering_units(0.0000001), '100.0n')
        self.assertEqual(engineering_units(0.00000001), '10.0n')
        self.assertEqual(engineering_units(0.000000001), '1.0n')
        self.assertEqual(engineering_units(0.000000990), '990.0n')
        self.assertEqual(engineering_units(0.000000099), '99.0n')
        self.assertEqual(engineering_units(0.000000009), '9.0n')

    def test_engineering_units_out_of_range(self):
        self.assertEqual(engineering_units(0.999e-9), None)
        self.assertEqual(engineering_units(1e9), None)

    def test_engineering_units_normal_size_numbers(self):
        self.assertEqual(engineering_units(1.01), str(1.01))
        self.assertEqual(engineering_units(1.00), str(1.00))

    def test_pad_zero(self):
        self.assertEqual(pad_zero('123', 5), '00123')
        self.assertEqual(pad_zero('123', 3), '123')
        self.assertEqual(pad_zero('123', 2), '123')
        self.assertEqual(pad_zero('', 3), '000')
        self.assertEqual(pad_zero('1', 0), '1')
        self.assertEqual(pad_zero('1', -1), '1')

    def test_twos_complement_base10_encode_8bit(self):
        self.assertEqual(negative_base10_encode(126, 8), 126)
        self.assertEqual(negative_base10_encode(127, 8), 127)
        self.assertIsNone(negative_base10_encode(128, 8))

        self.assertEqual(negative_base10_encode(-1, 8), 255)
        self.assertEqual(negative_base10_decode(255, 8), -1)
        self.assertEqual(negative_base10_encode(-128, 8), 128)
        self.assertEqual(negative_base10_decode(128, 8), -128)
        self.assertIsNone(negative_base10_encode(-129, 8))
        self.assertEqual(negative_base10_encode(-50, 8), 206)
        self.assertEqual(negative_base10_decode(206, 8), -50)

        self.assertEqual(negative_base10_encode(0, 8), 0)
        self.assertEqual(negative_base10_decode(0, 8), 0)

    def test_twos_complement_base10_encode_16bit(self):
        self.assertEqual(negative_base10_encode(32766, 16), 32766)
        self.assertEqual(negative_base10_encode(32767, 16), 32767)

        self.assertEqual(negative_base10_encode(-800, 16), 64736)
        self.assertEqual(negative_base10_decode(64736, 16), -800)

        self.assertEqual(negative_base10_encode(-32768, 16), 65536 + (-32768))
        self.assertEqual(negative_base10_decode(65536+(-32768), 16), -32768)
        self.assertIsNone(negative_base10_encode(-32769, 16))