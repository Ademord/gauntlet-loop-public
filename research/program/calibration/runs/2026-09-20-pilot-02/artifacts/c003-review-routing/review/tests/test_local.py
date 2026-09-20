import unittest
from solution import route_record


class LocalTests(unittest.TestCase):
    def test_status_failed_overrides_everything(self):
        record = {
            "status": "error",
            "processable": False,
            "is_target_type": None,
            "flags": [{"severity": "ERROR", "code": "X"}],
        }
        self.assertEqual(route_record(record), {"route": "failed", "reasons": ["error"]})

    def test_missing_status_defaults_ok(self):
        self.assertEqual(route_record({"is_target_type": True}), {"route": "auto", "reasons": []})

    def test_not_processable_skips_and_ignores_flags(self):
        record = {"processable": False, "is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}]}
        self.assertEqual(route_record(record), {"route": "skip", "reasons": []})

    def test_not_target_type_skips_and_ignores_flags(self):
        record = {"is_target_type": False, "flags": [{"severity": "ERROR", "code": "X"}]}
        self.assertEqual(route_record(record), {"route": "skip", "reasons": []})

    def test_missing_is_target_type_is_review(self):
        record = {"flags": [{"severity": "ERROR", "code": "X"}]}
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["UNCLASSIFIED"]})

    def test_none_is_target_type_is_review(self):
        record = {"is_target_type": None}
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["UNCLASSIFIED"]})

    def test_warn_severity_does_not_gate_review(self):
        record = {"is_target_type": True, "flags": [{"severity": "WARN", "code": "X"}]}
        self.assertEqual(route_record(record), {"route": "auto", "reasons": []})

    def test_missing_severity_does_not_gate_review(self):
        record = {"is_target_type": True, "flags": [{"code": "X"}]}
        self.assertEqual(route_record(record), {"route": "auto", "reasons": []})

    def test_error_codes_deduped_in_first_occurrence_order(self):
        record = {
            "is_target_type": True,
            "flags": [
                {"severity": "ERROR", "code": "A"},
                {"severity": "ERROR", "code": "B"},
                {"severity": "ERROR", "code": "A"},
            ],
        }
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["A", "B"]})

    def test_missing_or_empty_error_code_becomes_unknown(self):
        record = {
            "is_target_type": True,
            "flags": [
                {"severity": "ERROR"},
                {"severity": "ERROR", "code": None},
                {"severity": "ERROR", "code": ""},
            ],
        }
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["UNKNOWN_ERROR"]})

    def test_missing_flags_means_auto(self):
        self.assertEqual(route_record({"is_target_type": True}), {"route": "auto", "reasons": []})

    def test_none_flags_means_auto(self):
        self.assertEqual(route_record({"is_target_type": True, "flags": None}), {"route": "auto", "reasons": []})

    def test_explicit_none_status_is_treated_as_not_ok(self):
        self.assertEqual(route_record({"status": None, "is_target_type": True}), {"route": "failed", "reasons": [None]})

    def test_explicit_none_processable_does_not_skip(self):
        self.assertEqual(route_record({"processable": None, "is_target_type": True}), {"route": "auto", "reasons": []})

    def test_processable_false_precedes_is_target_type_none(self):
        record = {"processable": False, "is_target_type": None}
        self.assertEqual(route_record(record), {"route": "skip", "reasons": []})

    def test_lowercase_error_severity_does_not_gate_review(self):
        record = {"is_target_type": True, "flags": [{"severity": "error", "code": "X"}]}
        self.assertEqual(route_record(record), {"route": "auto", "reasons": []})

    def test_does_not_mutate_input(self):
        record = {"is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}]}
        snapshot = {"is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}]}
        route_record(record)
        self.assertEqual(record, snapshot)


if __name__ == "__main__":
    unittest.main()
