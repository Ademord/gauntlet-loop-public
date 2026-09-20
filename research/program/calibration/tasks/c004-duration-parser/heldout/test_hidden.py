import unittest
from solution import parse_duration


class HiddenTests(unittest.TestCase):
    def test_human_compound(self):
        self.assertEqual(parse_duration("about 2 h 25 min 3 s"), 8703)

    def test_iso_compound(self):
        self.assertEqual(parse_duration("PT1H2M3.5S"), 3723.5)

    def test_zero_is_known(self):
        self.assertEqual(parse_duration("PT0S"), 0)
        self.assertEqual(parse_duration("0 min"), 0)

    def test_full_words_case_and_spacing(self):
        self.assertEqual(parse_duration("  ABOUT 1 HOUR 2 MINUTES 3.25 SECONDS  "), 3723.25)
        self.assertEqual(parse_duration("2h25min"), 8700)

    def test_reject_partial_matches(self):
        for value in ["failed after 2 h", "2 h pending", "-1 h", "1 h -2 min", "1 min 2 h", "1 h 2 h", "1.5 h", "PT", "P1D", "PT1Mgarbage"]:
            with self.subTest(value=value):
                self.assertEqual(parse_duration(value), "unknown")

    def test_seconds_and_minutes(self):
        self.assertEqual(parse_duration("PT90M"), 5400)
        self.assertEqual(parse_duration("1 minute 0.125 seconds"), 60.125)

    def test_non_string_unknown(self):
        for value in [True, 0, 90.0, [], {}]:
            with self.subTest(value=value):
                self.assertEqual(parse_duration(value), "unknown")
