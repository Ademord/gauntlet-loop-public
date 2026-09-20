import unittest
from solution import ready_tasks


class LocalTests(unittest.TestCase):
    def test_capacity_must_be_int(self):
        with self.assertRaises(ValueError):
            ready_tasks([], True)
        with self.assertRaises(ValueError):
            ready_tasks([], 1.5)
        with self.assertRaises(ValueError):
            ready_tasks([], "1")
        with self.assertRaises(ValueError):
            ready_tasks([], -1)

    def test_capacity_zero_allowed(self):
        self.assertEqual(ready_tasks([{"id": "a"}], 0), [])

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            ready_tasks([{"id": "a"}, {"id": "a"}], 5)

    def test_unknown_dependency_rejected(self):
        with self.assertRaises(ValueError):
            ready_tasks([{"id": "a", "depends_on": ["missing"]}], 5)

    def test_cycle_rejected_even_if_done(self):
        tasks = [
            {"id": "a", "depends_on": ["b"], "status": "done"},
            {"id": "b", "depends_on": ["a"], "status": "done"},
        ]
        with self.assertRaises(ValueError):
            ready_tasks(tasks, 0)

    def test_cycle_rejected_with_zero_capacity(self):
        tasks = [
            {"id": "a", "depends_on": ["b"]},
            {"id": "b", "depends_on": ["a"]},
        ]
        with self.assertRaises(ValueError):
            ready_tasks(tasks, 0)

    def test_running_consumes_capacity(self):
        tasks = [
            {"id": "r1", "status": "running"},
            {"id": "p1", "status": "pending"},
            {"id": "p2", "status": "pending"},
        ]
        self.assertEqual(len(ready_tasks(tasks, 2)), 1)

    def test_never_exceed_available_slots(self):
        tasks = [
            {"id": "r1", "status": "running"},
            {"id": "r2", "status": "running"},
            {"id": "p1", "status": "pending"},
        ]
        self.assertEqual(ready_tasks(tasks, 1), [])

    def test_failed_or_running_prereq_blocks(self):
        tasks = [
            {"id": "dep_failed", "status": "failed"},
            {"id": "dep_running", "status": "running"},
            {"id": "t1", "depends_on": ["dep_failed"]},
            {"id": "t2", "depends_on": ["dep_running"]},
            {"id": "t3"},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["t3"])

    def test_resources_held_by_running_excluded(self):
        tasks = [
            {"id": "r1", "status": "running", "resources": ["gpu"]},
            {"id": "p1", "resources": ["gpu"]},
            {"id": "p2", "resources": ["cpu"]},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["p2"])

    def test_selected_tasks_do_not_conflict_with_each_other(self):
        tasks = [
            {"id": "p1", "resources": ["gpu"], "priority": 2},
            {"id": "p2", "resources": ["gpu"], "priority": 1},
            {"id": "p3", "resources": ["cpu"], "priority": 0},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["p1", "p3"])

    def test_priority_ties_preserve_input_order(self):
        tasks = [
            {"id": "a", "priority": 1},
            {"id": "b", "priority": 1},
            {"id": "c", "priority": 1},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["a", "b", "c"])

    def test_greedy_skip_continues_past_conflicts(self):
        tasks = [
            {"id": "a", "resources": ["x"], "priority": 3},
            {"id": "b", "resources": ["x"], "priority": 2},
            {"id": "c", "resources": ["y"], "priority": 1},
        ]
        self.assertEqual(ready_tasks(tasks, 2), ["a", "c"])

    def test_inputs_not_mutated(self):
        tasks = [{"id": "a", "priority": 1}, {"id": "b", "priority": 2}]
        original = [dict(t) for t in tasks]
        ready_tasks(tasks, 5)
        self.assertEqual(tasks, original)

    def test_done_and_failed_hold_no_resources(self):
        tasks = [
            {"id": "d1", "status": "done", "resources": ["gpu"]},
            {"id": "f1", "status": "failed", "resources": ["cpu"]},
            {"id": "p1", "resources": ["gpu"]},
            {"id": "p2", "resources": ["cpu"]},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["p1", "p2"])

    def test_unrelated_branches_remain_eligible(self):
        tasks = [
            {"id": "dep", "status": "running"},
            {"id": "blocked", "depends_on": ["dep"]},
            {"id": "free"},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["free"])

    def test_self_dependency_cycle_rejected(self):
        with self.assertRaises(ValueError):
            ready_tasks([{"id": "a", "depends_on": ["a"]}], 5)

    def test_three_node_cycle_rejected(self):
        tasks = [
            {"id": "a", "depends_on": ["b"]},
            {"id": "b", "depends_on": ["c"]},
            {"id": "c", "depends_on": ["a"]},
        ]
        with self.assertRaises(ValueError):
            ready_tasks(tasks, 5)

    def test_cycle_among_unrelated_valid_tasks_still_rejected(self):
        tasks = [
            {"id": "ok"},
            {"id": "a", "depends_on": ["b"]},
            {"id": "b", "depends_on": ["a"]},
        ]
        with self.assertRaises(ValueError):
            ready_tasks(tasks, 5)

    def test_diamond_dependency_not_treated_as_cycle(self):
        tasks = [
            {"id": "d", "status": "done"},
            {"id": "b", "depends_on": ["d"], "status": "done"},
            {"id": "c", "depends_on": ["d"], "status": "done"},
            {"id": "a", "depends_on": ["b", "c"]},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["a"])

    def test_running_surplus_over_capacity_yields_zero_slots(self):
        tasks = [
            {"id": "r1", "status": "running"},
            {"id": "r2", "status": "running"},
            {"id": "r3", "status": "running"},
            {"id": "p1"},
        ]
        self.assertEqual(ready_tasks(tasks, 1), [])

    def test_dependency_selected_this_round_not_yet_done(self):
        # "a" is pending and would be selected, but "b" depends on "a"
        # which is still only pending (not done) at call time, so "b"
        # must not be considered eligible in the same dispatch.
        tasks = [
            {"id": "a"},
            {"id": "b", "depends_on": ["a"]},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["a"])

    def test_deep_dependency_chain_no_recursion_error(self):
        n = 3000
        tasks = [{"id": "t0", "status": "done"}]
        for i in range(1, n):
            status = "done" if i < n - 1 else "pending"
            tasks.append({"id": f"t{i}", "depends_on": [f"t{i - 1}"], "status": status})
        self.assertEqual(ready_tasks(tasks, 1), [f"t{n - 1}"])

    def test_multiple_resources_all_must_be_free(self):
        tasks = [
            {"id": "r1", "status": "running", "resources": ["gpu"]},
            {"id": "p1", "resources": ["gpu", "cpu"], "priority": 1},
            {"id": "p2", "resources": ["cpu"], "priority": 0},
        ]
        self.assertEqual(ready_tasks(tasks, 5), ["p2"])


if __name__ == "__main__":
    unittest.main()
