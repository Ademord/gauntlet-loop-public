import copy
import unittest
from solution import match_items


class HiddenTests(unittest.TestCase):
    def test_cardinality_before_name_preference(self):
        pred = [{"name": "a", "amount": 5}, {"name": "b", "amount": 5}]
        gold = [{"name": "a", "amount": 5}, {"name": "a", "amount": 7}]
        self.assertEqual(match_items(pred, gold)["pairs"], [(1, 0), (0, 1)])

    def test_name_preference_at_equal_cardinality(self):
        pred = [{"name": "b", "amount": 5}, {"name": "a", "amount": 5}]
        gold = [{"name": "a", "amount": 5}, {"name": "b", "amount": 5}]
        self.assertEqual(match_items(pred, gold)["pairs"], [(1, 0), (0, 1)])

    def test_normalized_names(self):
        self.assertEqual(match_items([{"name": "  BOLT\t pack", "amount": None}], [{"name": "bolt pack", "amount": 9}])["pairs"], [(0, 0)])

    def test_null_does_not_match_null(self):
        self.assertEqual(match_items([{"name": "", "amount": None}], [{"name": " ", "amount": None}])["pairs"], [])

    def test_decimal_half_up(self):
        self.assertEqual(match_items([{"name": "x", "amount": "2.675"}], [{"name": "y", "amount": "2.68"}])["pairs"], [(0, 0)])

    def test_duplicate_rows_have_separate_identity(self):
        pred = [{"name": "a", "amount": 1}, {"name": "a", "amount": 1}, {"name": "other", "amount": 9}]
        gold = [{"name": "a", "amount": 1}, {"name": "a", "amount": 1}]
        self.assertEqual(match_items(pred, gold), {"pairs": [(0, 0), (1, 1)], "unmatched_predicted": [2], "unmatched_reference": []})

    def test_no_input_mutation(self):
        pred = [{"name": "a", "amount": 1}]
        gold = [{"name": "b", "amount": 1}, {"name": "c", "amount": 2}]
        before = copy.deepcopy((pred, gold))
        self.assertEqual(match_items(pred, gold)["unmatched_reference"], [1])
        self.assertEqual((pred, gold), before)

    def test_nonfinite_and_boolean_amounts_do_not_match(self):
        for value in [float("inf"), True, "NaN", "bad"]:
            with self.subTest(value=value):
                self.assertEqual(match_items([{"name": "x", "amount": value}], [{"name": "y", "amount": value}])["pairs"], [])
