import copy
import unittest
from solution import route_record


class HiddenTests(unittest.TestCase):
    def test_failure_precedes_skip_and_flags(self):
        self.assertEqual(route_record({"status": "failed_provider", "processable": False, "flags": [{"severity": "ERROR", "code": "X"}]}), {"route": "failed", "reasons": ["failed_provider"]})

    def test_blank_precedes_flags(self):
        self.assertEqual(route_record({"processable": False, "flags": [{"severity": "ERROR", "code": "X"}]}), {"route": "skip", "reasons": []})

    def test_non_target_precedes_flags(self):
        self.assertEqual(route_record({"is_target_type": False, "flags": [{"severity": "ERROR", "code": "X"}]}), {"route": "skip", "reasons": []})

    def test_unknown_classification(self):
        self.assertEqual(route_record({}), {"route": "review", "reasons": ["UNCLASSIFIED"]})
        self.assertEqual(route_record({"is_target_type": None, "flags": [{"severity": "ERROR", "code": "X"}]}), {"route": "review", "reasons": ["UNCLASSIFIED"]})

    def test_warnings_do_not_gate(self):
        self.assertEqual(route_record({"is_target_type": True, "flags": [{"severity": "WARN", "code": "X"}]}), {"route": "auto", "reasons": []})

    def test_error_codes_unique_in_source_order(self):
        flags = [{"severity": "ERROR", "code": "Z"}, {"severity": "WARN", "code": "W"}, {"severity": "ERROR", "code": "Z"}, {"severity": "ERROR", "code": "A"}, {"severity": "ERROR"}]
        self.assertEqual(route_record({"is_target_type": True, "flags": flags}), {"route": "review", "reasons": ["Z", "A", "UNKNOWN_ERROR"]})

    def test_input_is_unchanged(self):
        record = {"is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}, {"severity": "ERROR", "code": "X"}]}
        before = copy.deepcopy(record)
        route_record(record)
        self.assertEqual(record, before)
