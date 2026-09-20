import unittest
from solution import ready_tasks


class VisibleTests(unittest.TestCase):
    def test_dependency(self):
        tasks = [{"id": "build", "status": "done"}, {"id": "review", "depends_on": ["build"]}]
        self.assertEqual(ready_tasks(tasks, 1), ["review"])

    def test_priority(self):
        self.assertEqual(ready_tasks([{"id": "low", "priority": 1}, {"id": "high", "priority": 2}], 1), ["high"])
