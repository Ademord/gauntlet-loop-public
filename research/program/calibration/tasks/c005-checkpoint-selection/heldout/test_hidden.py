import copy
import unittest
from solution import select_latest


def row(project="p", run="r", stamp="2026-01-01T00:00:00Z", **extra):
    return {"project": project, "run_id": run, "updated_at": stamp, **extra}


class HiddenTests(unittest.TestCase):
    def test_project_is_part_of_identity(self):
        records = [row("alpha"), row("beta")]
        self.assertEqual(select_latest(records), records)

    def test_compare_instants_not_local_clock_text(self):
        records = [row(stamp="2026-01-01T10:00:00+02:00"), row(stamp="2026-01-01T09:00:00Z")]
        self.assertEqual(select_latest(records), [records[1]])

    def test_valid_time_beats_invalid(self):
        records = [row(stamp="2026-01-01T00:00:00Z"), row(stamp="unknown")]
        self.assertEqual(select_latest(records), [records[0]])

    def test_invalid_ties_use_last_occurrence(self):
        records = [row(stamp="unknown", marker=1), row(stamp=None, marker=2)]
        self.assertEqual(select_latest(records), [records[1]])

    def test_equal_instants_use_last_occurrence(self):
        records = [row(stamp="2026-01-01T01:00:00+01:00", marker=1), row(stamp="2026-01-01T00:00:00Z", marker=2)]
        self.assertEqual(select_latest(records), [records[1]])

    def test_first_seen_key_order(self):
        records = [row(run="b"), row(run="a"), row(run="b", stamp="2026-01-02T00:00:00Z")]
        self.assertEqual(select_latest(records), [records[2], records[1]])

    def test_invalid_identity_is_skipped(self):
        good = row()
        records = [{"project": "p"}, {"project": "", "run_id": "r"}, {"project": "p", "run_id": None}, good]
        self.assertEqual(select_latest(records), [good])

    def test_naive_timestamp_is_invalid_and_input_unchanged(self):
        records = [row(stamp="2026-01-01T01:00:00Z"), row(stamp="2027-01-01T00:00:00")]
        before = copy.deepcopy(records)
        self.assertEqual(select_latest(records), [records[0]])
        self.assertEqual(records, before)
