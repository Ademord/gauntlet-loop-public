import math
import unittest

from solution import parse_number


class LocalContractTests(unittest.TestCase):
    def test_none_and_unsupported_types(self):
        self.assertIsNone(parse_number(None))
        self.assertIsNone(parse_number(True))
        self.assertIsNone(parse_number(False))
        self.assertIsNone(parse_number([1, 2]))
        self.assertIsNone(parse_number({"a": 1}))
        self.assertIsNone(parse_number(object()))

    def test_int_float_passthrough(self):
        self.assertEqual(parse_number(5), 5.0)
        self.assertEqual(parse_number(-3), -3.0)
        self.assertEqual(parse_number(2.5), 2.5)
        self.assertIsNone(parse_number(float("nan")))
        self.assertIsNone(parse_number(float("inf")))
        self.assertIsNone(parse_number(float("-inf")))
        self.assertIsNone(parse_number(10 ** 400))

    def test_grouping_marks_stripped(self):
        self.assertEqual(parse_number(" 1'234.56 "), 1234.56)
        self.assertEqual(parse_number("1 234,56"), 1234.56)
        self.assertEqual(parse_number("1 234,56"), 1234.56)
        self.assertEqual(parse_number("1 234,56"), 1234.56)

    def test_single_kind_is_decimal(self):
        self.assertEqual(parse_number("1.000"), 1.0)
        self.assertEqual(parse_number("1,000"), 1.0)
        self.assertEqual(parse_number("123"), 123.0)
        self.assertEqual(parse_number("-123"), -123.0)
        self.assertEqual(parse_number("+123.5"), 123.5)

    def test_single_kind_multiple_separators_invalid(self):
        self.assertIsNone(parse_number("1.000.000"))
        self.assertIsNone(parse_number("1,000,000"))

    def test_mixed_kind_grouping(self):
        self.assertEqual(parse_number("1,234.56"), 1234.56)
        self.assertEqual(parse_number("1.234,56"), 1234.56)
        self.assertEqual(parse_number("12,345,678.9"), 12345678.9)
        self.assertEqual(parse_number("12.345.678,9"), 12345678.9)

    def test_mixed_kind_bad_grouping_invalid(self):
        self.assertIsNone(parse_number("12,34.56"))
        self.assertIsNone(parse_number("1,2345.56"))
        self.assertIsNone(parse_number("1,234.56.78"))

    def test_partial_numbers_invalid(self):
        self.assertIsNone(parse_number(".5"))
        self.assertIsNone(parse_number("5."))
        self.assertIsNone(parse_number(","))
        self.assertIsNone(parse_number("-"))
        self.assertIsNone(parse_number(""))
        self.assertIsNone(parse_number("   "))

    def test_exponent_and_nan_spellings_invalid(self):
        self.assertIsNone(parse_number("1e10"))
        self.assertIsNone(parse_number("1E10"))
        self.assertIsNone(parse_number("nan"))
        self.assertIsNone(parse_number("NaN"))
        self.assertIsNone(parse_number("inf"))
        self.assertIsNone(parse_number("Infinity"))
        self.assertIsNone(parse_number("-infinity"))

    def test_garbage_invalid(self):
        self.assertIsNone(parse_number("not a number"))
        self.assertIsNone(parse_number("12a34"))

    def test_string_overflow(self):
        self.assertIsNone(parse_number("1" * 400))

    def test_never_nonfinite(self):
        result = parse_number("1" * 400)
        self.assertIsNone(result)
        result2 = parse_number(1e308 * 10)
        self.assertIsNone(result2)

    def test_mixed_kind_overflow(self):
        huge = "1" + ",234" * 130 + ".0"
        self.assertIsNone(parse_number(huge))

    def test_apostrophe_grouping(self):
        self.assertEqual(parse_number("1'234'567"), 1234567.0)
        self.assertEqual(parse_number("1'234'567,89"), 1234567.89)

    def test_leading_zero_in_group(self):
        self.assertEqual(parse_number("0,001.5"), 1.5)

    def test_non_ascii_digits_invalid(self):
        self.assertIsNone(parse_number("١٢٣"))
        self.assertIsNone(parse_number("１２３"))

    def test_sign_edge_cases(self):
        self.assertIsNone(parse_number("+"))
        self.assertIsNone(parse_number("--1"))
        self.assertIsNone(parse_number("++1"))
        self.assertIsNone(parse_number("1-"))
        self.assertIsNone(parse_number("1+"))

    def test_more_malformed_grouping(self):
        self.assertIsNone(parse_number("1,234,567,89.1"))
        self.assertIsNone(parse_number("1,23,456.78"))
        self.assertIsNone(parse_number("1,234,5.67"))
        self.assertIsNone(parse_number(",567.89"))
        self.assertIsNone(parse_number("1,234,.56"))

    def test_leading_zero_plain_integer(self):
        self.assertEqual(parse_number("007"), 7.0)

    def test_negative_zero(self):
        self.assertEqual(parse_number("-0"), -0.0)


if __name__ == "__main__":
    unittest.main()
