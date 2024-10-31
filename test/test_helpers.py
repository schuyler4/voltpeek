import sys
sys.path.append('..')

import unittest

from voltpeek.helpers import engineering_units

class TestHelpers(unittest.TestCase):
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
        self.assertEqual(engineering_units(0.1), '100m')
        self.assertEqual(engineering_units(0.01), '10m')
        self.assertEqual(engineering_units(0.001), '1m')
        self.assertEqual(engineering_units(0.9), '900m')
        self.assertEqual(engineering_units(0.09), '90m')
        self.assertEqual(engineering_units(0.009), '9m')

    def test_engineering_units_micro(self):
        self.assertEqual(engineering_units(0.0001), '100u')
        self.assertEqual(engineering_units(0.00001), '10u')
        self.assertEqual(engineering_units(0.000001), '1u')
        self.assertEqual(engineering_units(0.0009999), '999u')
        self.assertEqual(engineering_units(0.000099), '99u')
        self.assertEqual(engineering_units(0.000009), '9u')

    def test_engineering_units_nano(self):
        self.assertEqual(engineering_units(0.0000001), '100n')
        self.assertEqual(engineering_units(0.00000001), '10n')
        self.assertEqual(engineering_units(0.000000001), '1n')
        self.assertEqual(engineering_units(0.000000999), '999n')
        self.assertEqual(engineering_units(0.000000099), '99n')
        self.assertEqual(engineering_units(0.000000009), '9n')

    def test_engineering_units_out_of_range(self):
        self.assertEqual(engineering_units(0.999e-9), None)
        self.assertEqual(engineering_units(1e9), None)

    def test_engineering_units_normal_size_numbers(self):
        self.assertEqual(engineering_units(1.01), str(1.01))
        self.assertEqual(engineering_units(1.00), str(1.00))