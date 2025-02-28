import unittest
from unittest.mock import patch
from main import (table_create, rpn_check, make_operation, to_bin, process_expression)

class MyTestCase(unittest.TestCase):


    def test_process_expression_with_negation(self):
        vars, rpn = process_expression("!a | b")
        self.assertEqual(vars, ['!a', 'b'])
        self.assertEqual(rpn, ['!a', 'b', '|'])

    def test_process_expression_complex(self):
        vars, rpn = process_expression("(a & b) | c")
        self.assertEqual(vars, ['a', 'b', 'c'])
        self.assertEqual(rpn, ['a', 'b', '&', 'c', '|'])

    def test_make_operation_and(self):
        self.assertEqual(make_operation(1, 1, '&'), 1)
        self.assertEqual(make_operation(1, 0, '&'), 0)
        self.assertEqual(make_operation(0, 0, '&'), 0)

    def test_make_operation_or(self):
        self.assertEqual(make_operation(1, 1, '|'), 1)
        self.assertEqual(make_operation(1, 0, '|'), 1)
        self.assertEqual(make_operation(0, 0, '|'), 0)

    def test_make_operation_implication(self):
        self.assertEqual(make_operation(1, 1, '->'), 1)
        self.assertEqual(make_operation(1, 0, '->'), 0)
        self.assertEqual(make_operation(0, 0, '->'), 1)

    def test_make_operation_equivalence(self):
        self.assertEqual(make_operation(1, 1, '~'), 1)
        self.assertEqual(make_operation(1, 0, '~'), 0)

    def test_table_create(self):
        expr = "a & b"
        vars, rpn = process_expression(expr)
        table = table_create(expr, rpn, vars)

        self.assertEqual(table['index'], [0, 0, 0, 1])
        self.assertEqual(table['pdnf'], [3])
        self.assertEqual(table['pcnf'], [0, 1, 2])

if __name__ == '__main__':
    unittest.main()
# coverage run -m unittest discover
# coverage report -m