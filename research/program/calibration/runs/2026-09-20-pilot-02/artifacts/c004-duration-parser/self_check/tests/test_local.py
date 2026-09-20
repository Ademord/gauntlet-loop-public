import unittest
from solution import parse_duration


class LocalTests(unittest.TestCase):
    def test_iso_format(self):
        self.assertEqual(parse_duration("PT1H2M3.5S"), 3723.5)
        self.assertEqual(parse_duration("PT90M"), 5400)
        self.assertEqual(parse_duration("PT0S"), 0)
        self.assertEqual(parse_duration("  PT1H  "), 3600)

    def test_human_format(self):
        self.assertEqual(parse_duration("about 2 hours 15 min"), 8100)
        self.assertEqual(parse_duration("1hour30min"), 5400)
        self.assertEqual(parse_duration("1 second"), 1)
        self.assertEqual(parse_duration("1 seconds"), 1)
        self.assertEqual(parse_duration("about 90 seconds"), 90)
        self.assertEqual(parse_duration("1.5s"), 1.5)

    def test_rejects_bad_input(self):
        self.assertEqual(parse_duration("about1h"), "unknown")
        self.assertEqual(parse_duration("90 sec"), "unknown")
        self.assertEqual(parse_duration("1.5h"), "unknown")
        self.assertEqual(parse_duration("1.5 min"), "unknown")
        self.assertEqual(parse_duration("-1h"), "unknown")
        self.assertEqual(parse_duration("+1h"), "unknown")
        self.assertEqual(parse_duration("1m1h"), "unknown")
        self.assertEqual(parse_duration("1h1h"), "unknown")
        self.assertEqual(parse_duration("pt1h"), "unknown")
        self.assertEqual(parse_duration("PT"), "unknown")
        self.assertEqual(parse_duration(""), "unknown")
        self.assertEqual(parse_duration("   "), "unknown")
        self.assertEqual(parse_duration(123), "unknown")
        self.assertEqual(parse_duration("PT1H2M3S extra"), "unknown")
        self.assertEqual(parse_duration("bogus PT1H"), "unknown")
        self.assertEqual(parse_duration("PT1.5H"), "unknown")
        self.assertEqual(parse_duration("PT1M2H"), "unknown")
        self.assertEqual(parse_duration("PT2M1H"), "unknown")
        self.assertEqual(parse_duration("2 hours 3 hours"), "unknown")
        self.assertEqual(parse_duration("5m"), "unknown")
        self.assertEqual(parse_duration("1s1min"), "unknown")
        self.assertEqual(parse_duration("PT.5S"), "unknown")
        self.assertEqual(parse_duration(".5s"), "unknown")
        self.assertEqual(parse_duration("3.s"), "unknown")
        self.assertEqual(parse_duration("about   "), "unknown")
        self.assertEqual(parse_duration("aboutness 2h"), "unknown")
        self.assertEqual(parse_duration("PT1e10H"), "unknown")

    def test_combined_units_and_order(self):
        self.assertEqual(parse_duration("1min1s"), 61)
        self.assertEqual(parse_duration("about 5 minutes"), 300)
        self.assertEqual(parse_duration("PT1H2M3S"), 3723)

    def test_overflow_is_unknown(self):
        self.assertEqual(parse_duration("PT" + "9" * 400 + "H"), "unknown")
        self.assertEqual(parse_duration("PT" + "9" * 400 + "M"), "unknown")
        self.assertEqual(parse_duration("PT" + "9" * 400 + "S"), "unknown")
        self.assertEqual(
            parse_duration("about " + "9" * 400 + " hours"), "unknown"
        )


if __name__ == "__main__":
    unittest.main()
