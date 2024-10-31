import sys
sys.path.append('..')

import unittest

from voltpeek.helpers import engineering_units

class TestHelpers(unittest.TestCase):
    def test_engineering_units(self):
        self.assertEqual(engineering_units(0.1), '100m')
        self.assertEqual(engineering_units(0.01), '10m')
        self.assertEqual(engineering_units(0.001), '1m')
        self.assertEqual(engineering_units(0.0001), '100u')
        self.assertEqual(engineering_units(0.00001), '10u')
        self.assertEqual(engineering_units(0.000001), '1u')
        self.assertEqual(engineering_units(0.0000001), '100n')
        self.assertEqual(engineering_units(0.00000001), '10n')
        self.assertEqual(engineering_units(0.000000001), '1n')
        self.assertEqual(engineering_units(0.9), '900m')
        self.assertEqual(engineering_units(0.09), '90m')
        self.assertEqual(engineering_units(0.009), '9m')
        self.assertEqual(engineering_units(0.0009), '900u')
        self.assertEqual(engineering_units(0.00009), '90u')
        self.assertEqual(engineering_units(0.000009), '9u')
        self.assertEqual(engineering_units(0.0000009), '900n')
        self.assertEqual(engineering_units(0.00000009), '90n')
        self.assertEqual(engineering_units(0.000000009), '9n')

    def test_engineering_units_out_of_range(self):
        self.assertEqual(engineering_units(9.99e-10), None)

    def test_engineering_units_one_and_larger(self):
        self.assertEqual(engineering_units(1.01), str(1.01))
        self.assertEqual(engineering_units(1.00), str(1.00))