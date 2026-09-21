"""Offline checks for conservative post-task triage and preserved pilot facts."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools import readiness


REPOSITORY = Path(__file__).resolve().parents[1]
SEED = readiness.DIRECTORY / "P001-triage.json"


class ReadinessTest(unittest.TestCase):
    def setUp(self):
        self.record = readiness.read_json(REPOSITORY / SEED)
        self.milestones = readiness.catalog(REPOSITORY)

    def errors(self, record=None):
        return readiness.record_errors(self.record if record is None else record, self.milestones)

    def test_seed_preserves_failed_attempts_and_unknown_full_cost(self):
        self.assertEqual([], self.errors())
        source = self.record["source_task"]
        self.assertEqual("failed", source["outcome"])
        self.assertEqual("not_installed", source["deployment"])
        self.assertEqual(["failed", "failed"], [a["acceptance"] for a in source["attempts"]])
        self.assertEqual([14, 15], [a["mechanical_checks"]["passed"] for a in source["attempts"]])
        self.assertEqual(4.7742095, source["worker_api_equivalent_usd"])
        self.assertIsNone(source["full_research_cost_usd"])
        self.assertIsNone(source["human_minutes"])
        self.assertEqual(1, source["controller_corrections"])
        repair = source["attempts"][1]
        self.assertEqual("budget_exhausted", repair["terminal_reason"])
        self.assertGreater(repair["worker_api_equivalent_usd"], repair["soft_usage_threshold_usd"])
        self.assertAlmostEqual(833.313, sum(a["worker_elapsed_seconds"] for a in source["attempts"]))

    def test_all_current_milestones_reviewed_without_status_promotion(self):
        self.assertEqual(50, len(self.milestones))
        self.assertEqual(set(self.milestones), set(self.record["milestone_review"]["reviewed_ids"]))
        self.assertEqual("Stronger development feedback", self.milestones["M-004"])
        self.assertEqual("Prefer native enforcement", self.milestones["M-033"])
        self.assertEqual([], self.record["milestone_status_changes"])
        self.assertTrue(all(gap["qualification"]["status"] == "not_run" for gap in self.record["gaps"]))

    def test_incomplete_review_and_new_catalog_milestone_require_review(self):
        self.record["milestone_review"]["reviewed_ids"].pop()
        self.assertTrue(any("cover every" in error for error in self.errors()))
        fresh = readiness.read_json(REPOSITORY / SEED)
        extended = dict(self.milestones, **{"M-051": "Future milestone"})
        self.assertTrue(any("cover every" in error for error in readiness.record_errors(fresh, extended)))

    def test_duplicate_review_and_unknown_gap_ids_are_rejected(self):
        self.record["milestone_review"]["reviewed_ids"].append("M-001")
        self.record["gaps"][0]["milestone_ids"] = ["M-999"]
        errors = self.errors()
        self.assertTrue(any("cover every" in error for error in errors))
        self.assertTrue(any("existing distinct" in error for error in errors))

    def test_causal_hypothesis_needs_alternatives_and_a_concrete_check(self):
        self.record["gaps"][0]["cause_status"] = "hypothesis"
        self.record["gaps"][0]["alternative_explanations"] = []
        self.record["gaps"][0]["qualification"]["failure_condition"] = "TBD"
        errors = self.errors()
        self.assertTrue(any("alternative explanations" in error for error in errors))
        self.assertTrue(any("failure_condition" in error for error in errors))

    def test_qualified_status_requires_result_evidence(self):
        check = self.record["gaps"][0]["qualification"]
        check["status"] = "passed"
        self.assertTrue(any("requires evidence" in error for error in self.errors()))
        check["evidence_references"] = ["public:qualified-native-fixture-record"]
        self.assertEqual([], self.errors())
        check["status"] = "not_run"
        self.assertTrue(any("cannot carry result evidence" in error for error in self.errors()))

    def test_readiness_cannot_authorize_paid_execution_or_promote_performance(self):
        self.record["paid_execution_authorized"] = True
        self.record["performance_evidence"] = "proven"
        self.record["milestone_status_changes"] = ["M-004"]
        self.record["gaps"][0]["qualification"]["method"] = "paid_worker"
        errors = self.errors()
        self.assertTrue(any("paid execution" in error for error in errors))
        self.assertTrue(any("performance evidence" in error for error in errors))
        self.assertTrue(any("milestone statuses" in error for error in errors))
        self.assertTrue(any("native_no_model" in error for error in errors))

    def test_cost_reconciliation_includes_failed_attempts(self):
        self.record["source_task"]["worker_api_equivalent_usd"] = 2.7197805
        self.assertTrue(any("include all" in error for error in self.errors()))

    def test_missing_attempt_usage_cannot_become_a_known_total(self):
        self.record["source_task"]["attempts"][1]["worker_api_equivalent_usd"] = None
        self.assertTrue(any("stay unknown" in error for error in self.errors()))
        self.record["source_task"]["worker_api_equivalent_usd"] = None
        self.assertEqual([], self.errors())

    def test_unknown_cause_is_valid_but_next_action_must_be_workable(self):
        self.record["gaps"][0]["cause_status"] = "unknown"
        self.assertEqual([], self.errors())
        self.record["next_gap_id"] = "P001-G05"  # Installation remains deferred.
        self.assertTrue(any("fix or investigation" in error for error in self.errors()))

    def fixture(self):
        temporary = tempfile.TemporaryDirectory(prefix="gauntlet-readiness-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for relative in (readiness.CATALOG, SEED):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPOSITORY / relative).read_bytes())
        return root

    def invoke(self, root, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            status = readiness.main(["--root", str(root), *args])
        return status, json.loads(output.getvalue())

    def test_commands_are_read_only_and_show_actual_catalog_titles(self):
        root = self.fixture()
        before = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in root.rglob("*") if p.is_file()}
        self.assertEqual(0, self.invoke(root, "validate")[0])
        self.assertEqual(0, self.invoke(root, "list")[0])
        status, result = self.invoke(root, "show", "P001")
        self.assertEqual(0, status)
        self.assertEqual("Ownership and isolation", result["milestone_titles"]["M-006"])
        self.assertEqual(1, self.invoke(root, "show", "MISSING")[0])
        after = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_duplicate_record_identity_is_rejected(self):
        root = self.fixture()
        (root / readiness.DIRECTORY / "duplicate-triage.json").write_bytes((root / SEED).read_bytes())
        status, result = self.invoke(root, "validate")
        self.assertEqual(1, status)
        self.assertTrue(any("duplicate triage ID" in error for error in result["errors"]))

    def test_invalid_json_shapes_are_reported_without_traceback(self):
        root = self.fixture()
        for content in ('[]', '{"id":"P001","id":"hidden"}', '{"value":NaN}'):
            with self.subTest(content=content):
                (root / SEED).write_text(content, encoding="utf-8")
                status, result = self.invoke(root, "validate")
                self.assertEqual(1, status)
                self.assertTrue(result["errors"])

    def test_gap_identity_and_mechanical_counts_are_checked(self):
        self.record["gaps"][1]["id"] = self.record["gaps"][0]["id"]
        self.record["source_task"]["attempts"][0]["mechanical_checks"]["passed"] = 18
        self.record["source_task"]["controller_corrections"] = True
        errors = self.errors()
        self.assertTrue(any("unique valid ID" in error for error in errors))
        self.assertTrue(any("mechanical check counts" in error for error in errors))
        self.assertTrue(any("controller_corrections" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
