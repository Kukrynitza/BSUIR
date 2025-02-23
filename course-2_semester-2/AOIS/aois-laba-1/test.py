import unittest
from unittest.mock import patch
from main import (menu,
    binary_to_decimal, addition_bin, to_bin,
    multiplication_bin, division_bin, float_to_ieee754, ieee754_to_float, addition_float
)

class MyTestCase(unittest.TestCase):
    def test_binary_to_decimal(self):
        self.assertEqual(binary_to_decimal([0, 1, 0, 1]), 5)
        self.assertEqual(binary_to_decimal([1, 1, 0, 1]), -5)

    def test_addition_bin(self):
        self.assertEqual(addition_bin([0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0]), [0, 0, 0, 0, 0, 1, 0, 1])

    def test_to_bin(self):
        self.assertEqual(to_bin(5, 'direct'), [0, 0, 0, 0, 0, 1, 0, 1])
        self.assertEqual(to_bin(-5, 'additionally'), [1, 1, 1, 1, 1, 0, 1, 1])

    def test_multiplication_bin(self):
        self.assertEqual(multiplication_bin([0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0]), [0, 0, 0, 0, 0, 1, 1, 0])

    def test_division_bin(self):
        self.assertEqual(division_bin([0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 1, 0]), '1.10000')

    def test_float_to_ieee754(self):
        ieee = float_to_ieee754(3.5)
        self.assertEqual(ieee[:9], [0, 1, 0, 0, 0, 0, 0, 0, 0])

    def test_ieee754_to_float(self):
        self.assertAlmostEqual(ieee754_to_float(float_to_ieee754(3.5)), 3.5, places=5)

    def test_addition_float(self):
        ieee_sum = addition_float(3.5, 2.5)
        self.assertAlmostEqual(ieee754_to_float(ieee_sum), 6.0, places=5)

    @patch('builtins.input', side_effect=['5', '3'])
    def test_menu_subtraction(self, mock_input):
        result = menu(2)
        self.assertEqual(result, 2)

    @patch('builtins.input', side_effect=['5', '3'])
    def test_menu_multiplication(self, mock_input):
        result = menu(3)
        self.assertEqual(result, 15)

    @patch('builtins.input', side_effect=['6', '3'])
    def test_menu_division(self, mock_input):
        result = menu(4)
        self.assertEqual(result, 2.0)

if __name__ == '__main__':
    unittest.main()
# coverage run --source=main -m unittest discover
# coverage report -m
