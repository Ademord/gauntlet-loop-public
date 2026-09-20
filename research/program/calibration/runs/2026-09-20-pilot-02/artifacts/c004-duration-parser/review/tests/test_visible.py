import unittest
from solution import parse_duration


class VisibleTests(unittest.TestCase):
    def test_one_unit(self):
        self.assertEqual(parse_duration("2 h"), 7200)
        self.assertEqual(parse_duration("15 min"), 900)

    def test_missing(self):
        self.assertEqual(parse_duration(None), "unknown")
        self.assertEqual(parse_duration("no duration"), "unknown")
