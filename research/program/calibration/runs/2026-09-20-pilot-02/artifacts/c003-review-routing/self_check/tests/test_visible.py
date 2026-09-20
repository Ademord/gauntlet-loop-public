import unittest
from solution import route_record


class VisibleTests(unittest.TestCase):
    def test_valid_record(self):
        self.assertEqual(route_record({"is_target_type": True}), {"route": "auto", "reasons": []})

    def test_error_needs_review(self):
        self.assertEqual(route_record({"is_target_type": True, "flags": [{"severity": "ERROR", "code": "SUM"}]}), {"route": "review", "reasons": ["SUM"]})
