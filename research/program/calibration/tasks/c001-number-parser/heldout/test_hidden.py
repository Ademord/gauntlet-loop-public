import math
import unittest
from solution import parse_number


class HiddenTests(unittest.TestCase):
    def test_mixed_european(self):
        self.assertEqual(parse_number("-1.234.567,89"), -1234567.89)

    def test_mixed_american(self):
        self.assertEqual(parse_number("+1,234,567.89"), 1234567.89)

    def test_unicode_grouping(self):
        self.assertEqual(parse_number("6\u202f288,94"), 6288.94)
        self.assertEqual(parse_number("6\u00a0288.94"), 6288.94)

    def test_boolean_is_not_a_number(self):
        self.assertIsNone(parse_number(True))
        self.assertIsNone(parse_number(False))

    def test_nonfinite_rejected(self):
        for value in [math.inf, -math.inf, math.nan, "NaN", "inf", "-Infinity"]:
            with self.subTest(value=value):
                self.assertIsNone(parse_number(value))

    def test_single_mark_is_decimal(self):
        self.assertEqual(parse_number("1.000"), 1.0)
        self.assertEqual(parse_number("1,000"), 1.0)

    def test_invalid_grammar(self):
        for value in [[], {}, "1e3", "1,2,3", "1.2.3", "1.23,45", "1,23.45", ".5", "5."]:
            with self.subTest(value=value):
                self.assertIsNone(parse_number(value))

    def test_empty_and_signed_zero(self):
        self.assertIsNone(parse_number("\u00a0"))
        self.assertEqual(parse_number("-0,00"), 0.0)
