import copy
import unittest

from solution import select_latest


class LocalTests(unittest.TestCase):
    def test_identity_is_project_and_run_id_pair(self):
        records = [
            {"project": "a", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "b", "run_id": "r", "updated_at": "2026-01-01T09:00:00Z"},
        ]
        result = select_latest(records)
        self.assertEqual(result, records)

    def test_skips_missing_or_invalid_identity(self):
        records = [
            {"run_id": "r", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "   ", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": 1, "run_id": "r", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "p", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "p", "run_id": "", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "p", "run_id": "  ", "updated_at": "2026-01-01T10:00:00Z"},
            {"project": "p", "run_id": 2, "updated_at": "2026-01-01T10:00:00Z"},
        ]
        self.assertEqual(select_latest(records), [])

    def test_does_not_strip_valid_identity_values(self):
        records = [{"project": " p ", "run_id": " r ", "updated_at": "2026-01-01T10:00:00Z"}]
        self.assertEqual(select_latest(records), records)

    def test_numeric_offsets_and_z_compared_by_instant(self):
        earlier = {
            "project": "p",
            "run_id": "r",
            "updated_at": "2026-01-01T09:00:00+00:00",
        }
        later = {
            "project": "p",
            "run_id": "r",
            "updated_at": "2026-01-01T10:30:00+05:30",
        }
        self.assertEqual(select_latest([earlier, later]), [earlier])

    def test_naive_timestamp_is_invalid(self):
        naive = {"project": "p", "run_id": "r", "updated_at": "2026-01-01T10:00:00", "state": "naive"}
        valid = {"project": "p", "run_id": "r", "updated_at": "2020-01-01T00:00:00Z", "state": "valid"}
        self.assertEqual(select_latest([naive, valid]), [valid])
        self.assertEqual(select_latest([valid, naive]), [valid])

    def test_missing_or_malformed_timestamp_is_invalid(self):
        malformed = {"project": "p", "run_id": "r", "updated_at": "not-a-date", "state": "bad"}
        missing = {"project": "p", "run_id": "r", "state": "missing"}
        non_string = {"project": "p", "run_id": "r", "updated_at": 12345, "state": "num"}
        valid = {"project": "p", "run_id": "r", "updated_at": "2020-01-01T00:00:00Z", "state": "valid"}
        self.assertEqual(select_latest([malformed, valid]), [valid])
        self.assertEqual(select_latest([missing, valid]), [valid])
        self.assertEqual(select_latest([non_string, valid]), [valid])

    def test_equal_instants_pick_later_occurrence(self):
        first = {"project": "p", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z", "state": "first"}
        second = {"project": "p", "run_id": "r", "updated_at": "2026-01-01T10:00:00+00:00", "state": "second"}
        self.assertEqual(select_latest([first, second]), [second])

    def test_all_invalid_timestamps_pick_later_occurrence(self):
        first = {"project": "p", "run_id": "r", "updated_at": "bad", "state": "first"}
        second = {"project": "p", "run_id": "r", "state": "second"}
        self.assertEqual(select_latest([first, second]), [second])

    def test_output_ordered_by_first_appearance(self):
        r1 = {"project": "p1", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z"}
        r2 = {"project": "p2", "run_id": "r", "updated_at": "2026-01-01T09:00:00Z"}
        r3 = {"project": "p1", "run_id": "r", "updated_at": "2026-01-01T11:00:00Z"}
        result = select_latest([r1, r2, r3])
        self.assertEqual(result, [r3, r2])

    def test_does_not_mutate_input(self):
        records = [
            {"project": "p", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z", "extra": 1},
            {"project": "p", "run_id": "r", "updated_at": "2026-01-01T11:00:00Z", "extra": 2},
        ]
        snapshot = copy.deepcopy(records)
        select_latest(records)
        self.assertEqual(records, snapshot)

    def test_preserves_extra_fields(self):
        record = {"project": "p", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z", "meta": {"a": 1}}
        result = select_latest([record])
        self.assertEqual(result, [record])
        self.assertIs(result[0], record)


if __name__ == "__main__":
    unittest.main()
