import unittest
from solution import match_items


class VisibleTests(unittest.TestCase):
    def test_exact_name(self):
        self.assertEqual(match_items([{"name": "Bolt", "amount": 2}], [{"name": "Bolt", "amount": 3}])["pairs"], [(0, 0)])

    def test_empty(self):
        self.assertEqual(match_items([], []), {"pairs": [], "unmatched_predicted": [], "unmatched_reference": []})
