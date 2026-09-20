import unittest
from solution import parse_number


class VisibleTests(unittest.TestCase):
    def test_plain_numbers(self):
        self.assertEqual(parse_number("12.50"), 12.5)
        self.assertEqual(parse_number(-3), -3.0)

    def test_comma_and_missing(self):
        self.assertEqual(parse_number(" 12,50 "), 12.5)
        self.assertIsNone(parse_number(None))
        self.assertIsNone(parse_number("not a number"))
