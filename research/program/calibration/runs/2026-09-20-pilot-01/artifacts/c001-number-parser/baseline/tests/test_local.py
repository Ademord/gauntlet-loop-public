import math
import unittest

from solution import parse_number


class LocalTests(unittest.TestCase):
    def test_bool_rejected(self):
        self.assertIsNone(parse_number(True))
        self.assertIsNone(parse_number(False))

    def test_unsupported_types(self):
        self.assertIsNone(parse_number([1, 2]))
        self.assertIsNone(parse_number({"a": 1}))
        self.assertIsNone(parse_number(b"12.5"))

    def test_nonfinite_numeric_inputs(self):
        self.assertIsNone(parse_number(float("nan")))
        self.assertIsNone(parse_number(float("inf")))
        self.assertIsNone(parse_number(float("-inf")))

    def test_numeric_overflow(self):
        self.assertIsNone(parse_number(10 ** 400))
        self.assertIsNone(parse_number(-(10 ** 400)))

    def test_grouping_marks_stripped(self):
        self.assertEqual(parse_number("1'234'567.89"), 1234567.89)
        self.assertEqual(parse_number("1 234,56"), 1234.56)
        self.assertEqual(parse_number("1 234,56"), 1234.56)
        self.assertEqual(parse_number("  1 234  "), 1234.0)

    def test_single_kind_decimal(self):
        self.assertEqual(parse_number("1.000"), 1.0)
        self.assertEqual(parse_number("1,000"), 1.0)
        self.assertEqual(parse_number("+12,50"), 12.5)
        self.assertEqual(parse_number("-12.50"), -12.5)

    def test_single_kind_multiple_separators_invalid(self):
        self.assertIsNone(parse_number("1.2.3"))
        self.assertIsNone(parse_number("1,234,567"))

    def test_mixed_grouping_dot_thousand_comma_decimal(self):
        self.assertEqual(parse_number("1.234.567,89"), 1234567.89)
        self.assertEqual(parse_number("1.234,56"), 1234.56)

    def test_mixed_grouping_comma_thousand_dot_decimal(self):
        self.assertEqual(parse_number("1,234,567.89"), 1234567.89)
        self.assertEqual(parse_number("1,234.56"), 1234.56)
        self.assertEqual(parse_number("-1,234.56"), -1234.56)

    def test_mixed_grouping_invalid_group_sizes(self):
        self.assertIsNone(parse_number("12.34,56"))
        self.assertIsNone(parse_number("1,23.456"))
        self.assertIsNone(parse_number("1,2345.67"))

    def test_mixed_grouping_multiple_decimal_occurrences_invalid(self):
        self.assertIsNone(parse_number("1,234,567.89.10"))

    def test_partial_numbers_rejected(self):
        self.assertIsNone(parse_number(".5"))
        self.assertIsNone(parse_number("5."))
        self.assertIsNone(parse_number(","))
        self.assertIsNone(parse_number("."))

    def test_exponent_rejected(self):
        self.assertIsNone(parse_number("1e10"))
        self.assertIsNone(parse_number("1E-5"))

    def test_nan_infinity_spellings_rejected(self):
        self.assertIsNone(parse_number("NaN"))
        self.assertIsNone(parse_number("nan"))
        self.assertIsNone(parse_number("inf"))
        self.assertIsNone(parse_number("Infinity"))
        self.assertIsNone(parse_number("-inf"))

    def test_empty_and_whitespace(self):
        self.assertIsNone(parse_number(""))
        self.assertIsNone(parse_number("   "))

    def test_never_returns_nonfinite_float(self):
        result = parse_number("1" + "0" * 400)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
