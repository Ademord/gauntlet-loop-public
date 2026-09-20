import unittest
from solution import match_items


class LocalTests(unittest.TestCase):
    def test_count_outranks_name_match(self):
        # A single name-match pair would give weight=1 but only 1 pair.
        # Two amount-only matches give 2 pairs but weight=0. Count wins.
        predicted = [
            {"name": "Bolt", "amount": 1},
            {"name": "Other", "amount": 2},
        ]
        reference = [
            {"name": "Bolt", "amount": 99},
            {"name": "Different", "amount": 2},
        ]
        result = match_items(predicted, reference)
        self.assertEqual(len(result["pairs"]), 2)
        self.assertEqual(sorted(result["pairs"]), [(0, 0), (1, 1)])

    def test_name_weight_breaks_tie_among_equal_count(self):
        # Two possible matchings of size 2; one has a name match, one doesn't.
        predicted = [
            {"name": "Widget", "amount": 5},
            {"name": "Widget", "amount": 7},
        ]
        reference = [
            {"name": "Widget", "amount": 7},
            {"name": "Gadget", "amount": 5},
        ]
        # predicted[0] can match reference[1] via amount (5==5)
        # predicted[1] can match reference[0] via name+amount (Widget, 7==7)
        # OR predicted[0]->ref0 (amount mismatch, name mismatch) not eligible
        # So best matching should prefer the one with a name match if count ties.
        result = match_items(predicted, reference)
        self.assertEqual(len(result["pairs"]), 2)

    def test_duplicate_rows_preserve_identity(self):
        predicted = [{"name": "Bolt", "amount": 1}, {"name": "Bolt", "amount": 1}]
        reference = [{"name": "Bolt", "amount": 1}, {"name": "Bolt", "amount": 1}]
        result = match_items(predicted, reference)
        self.assertEqual(sorted(result["pairs"]), [(0, 0), (1, 1)])
        self.assertEqual(result["unmatched_predicted"], [])
        self.assertEqual(result["unmatched_reference"], [])

    def test_lexicographic_tiebreak(self):
        # predicted[0] and predicted[1] both eligible for reference[0];
        # only predicted[1] eligible for reference[1].
        # To maximize pairs (2), reference[0] must take predicted[0],
        # leaving predicted[1] for reference[1].
        predicted = [
            {"name": "A", "amount": None},
            {"name": "A", "amount": None},
        ]
        reference = [
            {"name": "A", "amount": None},
            {"name": "A", "amount": None},
        ]
        result = match_items(predicted, reference)
        # Multiple optimal matchings exist: (0,0)+(1,1) vs (1,0)+(0,1).
        # Lexicographically smallest by (ref_index, pred_index) is (0,0),(0,1)... wait ref index first
        # sequence: for ref=0 choose smallest predicted index -> pred 0; for ref=1 -> pred 1
        self.assertEqual(result["pairs"], [(0, 0), (1, 1)])

    def test_name_normalization_whitespace_case(self):
        predicted = [{"name": "  Bolt   Inc  ", "amount": None}]
        reference = [{"name": "bolt inc", "amount": None}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [(0, 0)])

    def test_empty_name_never_matches(self):
        predicted = [{"name": "   ", "amount": None}]
        reference = [{"name": "", "amount": None}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [])
        self.assertEqual(result["unmatched_predicted"], [0])
        self.assertEqual(result["unmatched_reference"], [0])

    def test_amount_rounding_half_up(self):
        predicted = [{"name": None, "amount": "3.005"}]
        reference = [{"name": None, "amount": "3.01"}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [(0, 0)])

    def test_amount_numeric_string_and_number_equal(self):
        predicted = [{"name": None, "amount": "5.00"}]
        reference = [{"name": None, "amount": 5}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [(0, 0)])

    def test_bool_amount_never_matches(self):
        predicted = [{"name": None, "amount": True}]
        reference = [{"name": None, "amount": 1}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [])

    def test_nonfinite_amount_never_matches(self):
        predicted = [{"name": None, "amount": float("inf")}]
        reference = [{"name": None, "amount": float("inf")}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [])

    def test_invalid_string_amount_never_matches(self):
        predicted = [{"name": None, "amount": "not-a-number"}]
        reference = [{"name": None, "amount": "not-a-number"}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [])

    def test_none_amount_never_matches(self):
        predicted = [{"name": None, "amount": None}]
        reference = [{"name": None, "amount": None}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [])

    def test_inputs_unchanged(self):
        predicted = [{"name": "Bolt", "amount": 1}]
        reference = [{"name": "Bolt", "amount": 1}]
        predicted_copy = [dict(row) for row in predicted]
        reference_copy = [dict(row) for row in reference]
        match_items(predicted, reference)
        self.assertEqual(predicted, predicted_copy)
        self.assertEqual(reference, reference_copy)

    def test_unmatched_ordering(self):
        predicted = [{"name": "X", "amount": None}, {"name": "Y", "amount": None}, {"name": "Bolt", "amount": None}]
        reference = [{"name": "Bolt", "amount": None}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [(2, 0)])
        self.assertEqual(result["unmatched_predicted"], [0, 1])
        self.assertEqual(result["unmatched_reference"], [])

    def test_missing_keys_default_none(self):
        predicted = [{}]
        reference = [{}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [])
        self.assertEqual(result["unmatched_predicted"], [0])
        self.assertEqual(result["unmatched_reference"], [0])

    def test_large_amount_still_matches(self):
        # Regression guard: quantize() must not silently fail for values whose
        # digit count exceeds the default Decimal context precision (28).
        big = "1" + "0" * 30
        predicted = [{"name": None, "amount": big}]
        reference = [{"name": None, "amount": int(big)}]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [(0, 0)])

    def test_duplicate_oversubscription(self):
        predicted = [{"name": "Bolt", "amount": 1}] * 3
        reference = [{"name": "Bolt", "amount": 1}] * 2
        result = match_items(predicted, reference)
        self.assertEqual(len(result["pairs"]), 2)
        self.assertEqual(result["unmatched_predicted"], [2])
        self.assertEqual(result["unmatched_reference"], [])

    def test_full_8x8_complete_graph_lexicographic(self):
        predicted = [{"name": None, "amount": 5} for _ in range(8)]
        reference = [{"name": None, "amount": 5} for _ in range(8)]
        result = match_items(predicted, reference)
        self.assertEqual(result["pairs"], [(i, i) for i in range(8)])


if __name__ == "__main__":
    unittest.main()
