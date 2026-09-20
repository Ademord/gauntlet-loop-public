import copy
import unittest
from solution import ready_tasks


class HiddenTests(unittest.TestCase):
    def test_running_consumes_capacity(self):
        tasks = [{"id": "running", "status": "running"}, {"id": "a"}, {"id": "b"}]
        self.assertEqual(ready_tasks(tasks, 2), ["a"])

    def test_running_holds_resource(self):
        tasks = [{"id": "running", "status": "running", "resources": ["browser"]}, {"id": "a", "priority": 9, "resources": ["browser"]}, {"id": "b", "resources": ["files"]}]
        self.assertEqual(ready_tasks(tasks, 3), ["b"])

    def test_selected_tasks_reserve_resources(self):
        tasks = [{"id": "a", "priority": 4, "resources": ["db"]}, {"id": "b", "priority": 3, "resources": ["db"]}, {"id": "c", "priority": 2, "resources": ["fs"]}]
        self.assertEqual(ready_tasks(tasks, 2), ["a", "c"])

    def test_stable_tie_and_no_input_mutation(self):
        tasks = [{"id": "z", "priority": 2}, {"id": "a", "priority": 2}, {"id": "b", "priority": 1}]
        before = copy.deepcopy(tasks)
        self.assertEqual(ready_tasks(tasks, 2), ["z", "a"])
        self.assertEqual(tasks, before)

    def test_failed_dependency_blocks_only_its_branch(self):
        tasks = [{"id": "bad", "status": "failed"}, {"id": "child", "depends_on": ["bad"]}, {"id": "other"}]
        self.assertEqual(ready_tasks(tasks, 2), ["other"])

    def test_unknown_dependency_rejected(self):
        with self.assertRaises(ValueError):
            ready_tasks([{"id": "a", "depends_on": ["missing"]}], 2)

    def test_cycle_rejected_even_if_all_done(self):
        tasks = [{"id": "a", "status": "done", "depends_on": ["b"]}, {"id": "b", "status": "done", "depends_on": ["a"]}]
        with self.assertRaises(ValueError):
            ready_tasks(tasks, 2)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            ready_tasks([{"id": "a"}, {"id": "a"}], 1)

    def test_capacity_validation_and_saturation(self):
        for value in [True, -1, 1.5, None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                ready_tasks([{"id": "a"}], value)
        self.assertEqual(ready_tasks([{"id": "a"}], 0), [])
        self.assertEqual(ready_tasks([{"id": "a", "status": "running"}, {"id": "b"}], 1), [])
