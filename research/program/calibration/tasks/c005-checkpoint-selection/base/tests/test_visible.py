import unittest
from solution import select_latest


class VisibleTests(unittest.TestCase):
    def test_later_record(self):
        records = [{"project": "one", "run_id": "r", "updated_at": "2026-01-01T10:00:00Z", "state": "old"}, {"project": "one", "run_id": "r", "updated_at": "2026-01-01T11:00:00Z", "state": "new"}]
        self.assertEqual(select_latest(records), [records[1]])

    def test_empty(self):
        self.assertEqual(select_latest([]), [])
