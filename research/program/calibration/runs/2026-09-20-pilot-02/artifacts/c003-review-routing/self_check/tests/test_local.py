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

    def test_does_not_mutate_input(self):
        record = {"is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}]}
        snapshot = {"is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}]}
        route_record(record)
        self.assertEqual(record, snapshot)

    def test_explicit_status_ok_behaves_like_missing(self):
        record = {"status": "ok", "is_target_type": True}
        self.assertEqual(route_record(record), {"route": "auto", "reasons": []})

    def test_explicit_none_status_is_failed(self):
        record = {"status": None, "is_target_type": True}
        self.assertEqual(route_record(record), {"route": "failed", "reasons": [None]})

    def test_explicit_none_processable_does_not_skip(self):
        record = {
            "processable": None,
            "is_target_type": True,
            "flags": [{"severity": "ERROR", "code": "X"}],
        }
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["X"]})

    def test_is_target_type_false_takes_priority_over_missing_processable(self):
        record = {"is_target_type": False}
        self.assertEqual(route_record(record), {"route": "skip", "reasons": []})

    def test_dedup_preserves_first_occurrence_across_unknown_normalization(self):
        record = {
            "is_target_type": True,
            "flags": [
                {"severity": "ERROR", "code": "A"},
                {"severity": "ERROR", "code": ""},
                {"severity": "ERROR", "code": "A"},
                {"severity": "ERROR", "code": None},
            ],
        }
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["A", "UNKNOWN_ERROR"]})

    def test_mixed_severities_only_error_codes_collected_in_order(self):
        record = {
            "is_target_type": True,
            "flags": [
                {"severity": "WARN", "code": "W1"},
                {"severity": "ERROR", "code": "E1"},
                {"code": "NOSEV"},
                {"severity": "ERROR", "code": "E2"},
            ],
        }
        self.assertEqual(route_record(record), {"route": "review", "reasons": ["E1", "E2"]})

    def test_result_has_exactly_route_and_reasons_keys(self):
        result = route_record({"is_target_type": True, "flags": [{"severity": "ERROR", "code": "X"}]})
        self.assertEqual(set(result.keys()), {"route", "reasons"})


if __name__ == "__main__":
    unittest.main()
