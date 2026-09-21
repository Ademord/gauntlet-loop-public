"""Offline failure tests for research evidence, freezes, and bounded execution."""

import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import program


REPOSITORY = Path(__file__).resolve().parents[1]
CATALOG = Path("research/program/MILESTONES-50.json")
EVIDENCE = Path("research/program/evidence.json")
EXPERIMENT = "EXP-001"
PLAN = Path(f"research/program/experiments/{EXPERIMENT}/plan.json")
MATERIAL = Path("research/program/materials/fixture.json")
SOURCE = Path("skill/fixture.md")
SUPPORT = Path("research/program/fixtures/support.txt")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ResearchProgramTest(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory(prefix="gauntlet-program-test-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "repo"
        root.mkdir()
        catalog = copy.deepcopy(read_json(REPOSITORY / CATALOG))
        for source in catalog["sources"].values():
            source.update(checked_date=date.today().isoformat(), review_status="active", review_after_days=30)
        for index, milestone in enumerate(catalog["milestones"], 1):
            milestone["claim_id"] = f"M-{index:03d}"
            milestone["workflow"] = {
                "state": "deferred", "queue": "deferred", "priority": index,
                "depends_on": [], "scope": "Synthetic fixture; no performance claim.",
            }
            milestone["evidence_ids"] = []
            milestone["experiment_ids"] = []
        first = catalog["milestones"][0]
        first["workflow"].update(state="open", queue="ready")
        first["evidence_ids"] = ["EV-001"]
        first["experiment_ids"] = [EXPERIMENT]
        write_json(root / CATALOG, catalog)
        (root / SOURCE).parent.mkdir(parents=True, exist_ok=True)
        (root / SOURCE).write_text("Preserve task ownership.\n", encoding="utf-8")
        (root / SUPPORT).parent.mkdir(parents=True, exist_ok=True)
        (root / SUPPORT).write_text("Independent prerequisite evidence.\n", encoding="utf-8")
        material = {
            "format_version": 1,
            "checked_date": date.today().isoformat(),
            "kind": "offline_documentary_overlap_inventory",
            "scope": "One synthetic inventory entry, not an efficacy experiment.",
            "source_files": {SOURCE.as_posix(): sha(root / SOURCE)},
            "entries": [{
                "id": "OVL-001", "title": "Task ownership",
                "skill": {
                    "path": SOURCE.as_posix(), "line_start": 1, "line_end": 1,
                    "excerpt": "Preserve task ownership.",
                    "excerpt_sha256": hashlib.sha256(b"Preserve task ownership.").hexdigest(),
                    "lines_sha256": hashlib.sha256(b"Preserve task ownership.").hexdigest(),
                },
                "source_ids": ["C1"], "overlap_classification": "mixed",
                "recommended_action": "needs_probe", "probe_status": "not_run",
                "native_support": "Synthetic documented primitive.",
                "native_limit": "No observed runtime benefit.",
                "risk": "The fixture cannot establish real host behavior.",
                "discriminating_probe": {
                    "setup": "Use a scratch workspace.",
                    "variants": ["Native host", "Host with ownership policy"],
                    "faults": ["Conflicting ownership"],
                    "pass_condition": "Conflicting ownership is detected.",
                    "metrics": ["Unresolved conflicts"],
                },
            }],
        }
        write_json(root / MATERIAL, material)
        evidence = {
            "schema_version": 1,
            "evidence": [{
                "id": "EV-001", "kind": "engineering",
                "observed_on": date.today().isoformat(),
                "scope": "A frozen synthetic source artifact exists.",
                "establishes": ["documentary-inventory"],
                "limitations": ["No empirical performance evidence."],
                "claim_ids": ["M-001"],
                "artifacts": [{"path": SUPPORT.as_posix(), "sha256": sha(root / SUPPORT)}],
                "source_ids": [],
            }],
        }
        write_json(root / EVIDENCE, evidence)
        plan = {
            "schema_version": 1, "id": EXPERIMENT, "claim_ids": ["M-001"],
            "questions": {
                "claim": "The source clauses can be inventoried without model calls.",
                "comparator": "The recorded source artifact and classifications.",
                "stop_rule": "Stop if a source identity does not match.",
                "losses_to_check": "Missing entries, stale sources and overstated evidence.",
                "cost": "Zero model calls; human time is not measured.",
                "next_decision": "Review the inventory without promoting a milestone.",
            },
            "metrics": ["Source identities checked", "Entries inventoried"],
            "prerequisites": [{
                "id": "PRE-001", "satisfied": True, "evidence_ids": ["EV-001"],
                "required_scope": "documentary-inventory",
                "reason": "The frozen synthetic source is available.",
            }],
            "inputs": [SOURCE.as_posix(), MATERIAL.as_posix()],
            "execution": {"kind": "inventory_audit", "material": MATERIAL.as_posix()},
            "budget": {
                "model_execution_usd": 0, "preparation_minutes": None,
                "evaluation_minutes": None, "human_minutes": None,
            },
            "status": "draft",
        }
        write_json(root / PLAN, plan)
        self.assertEqual(program.validate(root)["errors"], [], "Fixture must begin valid")
        return root

    def test_duplicate_claim_and_evidence_ids_are_rejected(self):
        for target in ("claim", "evidence"):
            with self.subTest(target=target):
                root = self.fixture()
                if target == "claim":
                    data = read_json(root / CATALOG)
                    data["milestones"][1]["claim_id"] = "M-001"
                    data["milestones"][1]["id"] = 1
                    write_json(root / CATALOG, data)
                else:
                    data = read_json(root / EVIDENCE)
                    data["evidence"].append(copy.deepcopy(data["evidence"][0]))
                    write_json(root / EVIDENCE, data)
                self.assertTrue(any("Duplicate" in error for error in program.validate(root)["errors"]))

    def test_missing_evidence_reference_blocks_validation_and_freeze(self):
        root = self.fixture()
        data = read_json(root / CATALOG)
        data["milestones"][0]["evidence_ids"] = ["EV-999"]
        write_json(root / CATALOG, data)
        self.assertTrue(program.validate(root)["errors"])
        with self.assertRaises(ValueError):
            program.freeze(root, EXPERIMENT)

    def test_dependency_cycle_is_rejected(self):
        root = self.fixture()
        data = read_json(root / CATALOG)
        data["milestones"][0]["workflow"]["depends_on"] = ["M-002"]
        data["milestones"][1]["workflow"]["depends_on"] = ["M-001"]
        write_json(root / CATALOG, data)
        self.assertTrue(program.validate(root)["errors"])

    def test_repository_escape_is_rejected_for_evidence_and_plan_inputs(self):
        for target in ("evidence", "input"):
            with self.subTest(target=target):
                root = self.fixture()
                # The escaped file exists and has the expected bytes: rejection
                # must come from containment, not missing-file or hash checks.
                (root.parent / "outside.txt").write_bytes((root / SUPPORT).read_bytes())
                if target == "evidence":
                    data = read_json(root / EVIDENCE)
                    data["evidence"][0]["artifacts"][0]["path"] = "../outside.txt"
                    write_json(root / EVIDENCE, data)
                else:
                    data = read_json(root / PLAN)
                    data["inputs"] = ["../outside.txt"]
                    write_json(root / PLAN, data)
                self.assertTrue(program.validate(root)["errors"])
                with self.assertRaises(ValueError):
                    program.freeze(root, EXPERIMENT)

    def test_artifact_hash_drift_invalidates_existing_evidence(self):
        root = self.fixture()
        # This artifact is separate from the inventory's source clauses, so the
        # prerequisite evidence guard must stop the otherwise valid inventory.
        (root / SUPPORT).write_text("Changed after observation.\n", encoding="utf-8")
        report = program.validate(root)
        self.assertEqual(report["errors"], [])
        self.assertTrue(any("hash changed" in warning for warning in report["warnings"]))
        self.assertTrue(program.readiness(root, EXPERIMENT))
        with self.assertRaises(ValueError):
            program.freeze(root, EXPERIMENT)

    def test_stale_or_contested_source_preserves_history_but_blocks_reuse(self):
        for condition in ("stale", "contested"):
            with self.subTest(condition=condition):
                root = self.fixture()
                self.assertEqual([item["claim_id"] for item in program.next_items(root)], ["M-001"])
                catalog = read_json(root / CATALOG)
                if condition == "stale":
                    catalog["sources"]["C1"]["checked_date"] = "2000-01-01"
                else:
                    catalog["sources"]["C1"]["review_status"] = "contested"
                write_json(root / CATALOG, catalog)
                evidence = read_json(root / EVIDENCE)
                evidence["evidence"][0]["source_ids"] = ["C1"]
                write_json(root / EVIDENCE, evidence)
                report = program.validate(root)
                self.assertEqual(report["errors"], [])
                self.assertTrue(any("C1" in warning for warning in report["warnings"]))
                if condition == "stale":
                    as_of = program.validate(root, today=date(2000, 1, 2))
                    self.assertFalse(any("C1:" in warning for warning in as_of["warnings"]))
                self.assertEqual(program.next_items(root), [])
                self.assertTrue(program.readiness(root, EXPERIMENT))
                with self.assertRaises(ValueError):
                    program.freeze(root, EXPERIMENT)

    def test_placeholder_plan_can_be_drafted_but_cannot_be_frozen(self):
        for field in ("questions", "metrics", "inputs", "prerequisite"):
            with self.subTest(field=field):
                root = self.fixture()
                plan = read_json(root / PLAN)
                if field == "questions":
                    plan["questions"]["claim"] = ""
                elif field == "prerequisite":
                    plan["prerequisites"][0]["satisfied"] = False
                else:
                    plan[field] = []
                write_json(root / PLAN, plan)
                self.assertEqual(program.validate(root)["errors"], [])
                self.assertTrue(program.readiness(root, EXPERIMENT))
                with self.assertRaises(ValueError):
                    program.freeze(root, EXPERIMENT)

    def test_run_requires_a_freeze(self):
        root = self.fixture()
        with self.assertRaises(ValueError):
            program.run_inventory(root, EXPERIMENT)

    def test_native_availability_evidence_cannot_qualify_runtime_control(self):
        root = self.fixture()
        self.assertEqual(program.readiness(root, EXPERIMENT), [])
        plan = read_json(root / PLAN)
        plan["prerequisites"][0]["required_scope"] = "runtime-control"
        write_json(root / PLAN, plan)
        evidence = read_json(root / EVIDENCE)
        evidence["evidence"][0].update(
            kind="documentation", scope="Native availability is documented.",
            establishes=["native-availability"],
        )
        write_json(root / EVIDENCE, evidence)
        self.assertEqual(program.validate(root)["errors"], [])
        self.assertTrue(plan["prerequisites"][0]["satisfied"])
        blockers = program.readiness(root, EXPERIMENT)
        self.assertTrue(any("does not establish required scope runtime-control" in item for item in blockers))
        with self.assertRaises(ValueError):
            program.freeze(root, EXPERIMENT)

    def test_truthy_but_incomplete_discriminating_probe_cannot_freeze(self):
        for flaw in ("placeholder", "not_record", "one_variant", "no_faults", "no_metrics"):
            with self.subTest(flaw=flaw):
                root = self.fixture()
                self.assertEqual(program.readiness(root, EXPERIMENT), [])
                material = read_json(root / MATERIAL)
                entry = material["entries"][0]
                if flaw == "placeholder":
                    entry["discriminating_probe"] = {"setup": "TODO"}
                elif flaw == "not_record":
                    entry["discriminating_probe"] = "A plausible-sounding probe exists."
                elif flaw == "one_variant":
                    entry["discriminating_probe"]["variants"] = ["Native host"]
                elif flaw == "no_faults":
                    entry["discriminating_probe"]["faults"] = []
                else:
                    entry["discriminating_probe"]["metrics"] = []
                self.assertTrue(entry["discriminating_probe"])
                write_json(root / MATERIAL, material)
                self.assertEqual(program.validate(root)["errors"], [])
                self.assertTrue(program.readiness(root, EXPERIMENT))
                with self.assertRaises(ValueError):
                    program.freeze(root, EXPERIMENT)

    def test_contested_dependency_evidence_hides_downstream_ready_work(self):
        for depth in (1, 2):
            with self.subTest(depth=depth):
                root = self.fixture()
                catalog = read_json(root / CATALOG)
                evidence = read_json(root / EVIDENCE)
                for index in range(1, depth + 1):
                    cid = f"M-{index + 1:03d}"
                    eid = f"EV-{index + 1:03d}"
                    catalog["milestones"][index - 1]["workflow"]["depends_on"] = [cid]
                    dependency = catalog["milestones"][index]
                    dependency["workflow"].update(state="verified_scope", queue="closed")
                    dependency["evidence_ids"] = [eid]
                    item = copy.deepcopy(evidence["evidence"][0])
                    item.update(id=eid, claim_ids=[cid], source_ids=["C1"] if index == depth else [])
                    evidence["evidence"].append(item)
                write_json(root / CATALOG, catalog)
                write_json(root / EVIDENCE, evidence)
                self.assertEqual(program.validate(root)["errors"], [])
                self.assertEqual([item["claim_id"] for item in program.next_items(root)], ["M-001"])
                catalog["sources"]["C1"]["review_status"] = "contested"
                write_json(root / CATALOG, catalog)
                self.assertEqual(program.validate(root)["errors"], [])
                self.assertEqual(program.next_items(root), [])

    def test_forged_inventory_result_cannot_claim_execution_or_wrong_scope(self):
        root = self.fixture()
        frozen = read_json(program.freeze(root, EXPERIMENT))
        actual = program.run_inventory(root, EXPERIMENT)
        self.assertEqual(program.result_errors(actual, frozen), [])
        outcomes = ("entries_checked", "pointer_errors", "native_behavior_probes_executed", "model_calls", "audit_seconds")
        for missing in outcomes:
            with self.subTest(missing=missing):
                forged = copy.deepcopy(actual)
                del forged["outcomes"][missing]
                self.assertTrue(program.result_errors(forged, frozen))
        mutations = [
            ("native_behavior_probes_executed", 1),
            ("model_calls", 1),
            ("entries_checked", actual["outcomes"]["entries_checked"] + 1),
            ("model_calls", False),
            ("entries_checked", "1"),
            ("audit_seconds", float("nan")),
            ("audit_seconds", float("inf")),
            ("audit_seconds", -1),
        ]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                forged = copy.deepcopy(actual)
                forged["outcomes"][key] = value
                self.assertTrue(program.result_errors(forged, frozen))
        forged = copy.deepcopy(actual)
        forged["costs"]["model_execution_usd"] = 0.01
        self.assertTrue(program.result_errors(forged, frozen))
        forged = copy.deepcopy(actual)
        forged["outcomes"]["pointer_errors"] = 1
        forged["decision"]["outcome"] = "reject"
        self.assertTrue(any("match disclosed losses" in error for error in program.result_errors(forged, frozen)))
        forged = copy.deepcopy(actual)
        forged["decision"]["scope"] = "Native runtime performance is improved."
        self.assertTrue(any("inventory-only decision scope" in error for error in program.result_errors(forged, frozen)))

    def test_changed_frozen_plan_and_material_cannot_execute(self):
        for changed in (PLAN, MATERIAL):
            with self.subTest(changed=changed):
                root = self.fixture()
                self.assertEqual(program.readiness(root, EXPERIMENT), [])
                program.freeze(root, EXPERIMENT)
                data = read_json(root / changed)
                if changed == PLAN:
                    data["questions"]["claim"] += " Altered after freeze."
                else:
                    data["entries"][0]["recommended_action"] = "keep"
                write_json(root / changed, data)
                with self.assertRaises(ValueError):
                    program.run_inventory(root, EXPERIMENT)

    def test_external_execution_cannot_be_frozen_or_run(self):
        root = self.fixture()
        plan = read_json(root / PLAN)
        plan["execution"]["kind"] = "external"
        write_json(root / PLAN, plan)
        self.assertEqual(program.validate(root)["errors"], [])
        self.assertTrue(program.readiness(root, EXPERIMENT))
        with self.assertRaises(ValueError):
            program.freeze(root, EXPERIMENT)
        with self.assertRaises(ValueError):
            program.run_inventory(root, EXPERIMENT)

    def test_false_nonfinite_and_negative_costs_are_invalid(self):
        for cost in (False, float("nan"), float("inf"), -1):
            with self.subTest(cost=cost):
                root = self.fixture()
                plan = read_json(root / PLAN)
                plan["budget"]["model_execution_usd"] = cost
                write_json(root / PLAN, plan)
                self.assertTrue(program.validate(root)["errors"])
                with self.assertRaises(ValueError):
                    program.freeze(root, EXPERIMENT)

    def test_offline_audit_never_promotes_milestones_or_overwrites_results(self):
        root = self.fixture()
        catalog_before = (root / CATALOG).read_bytes()
        evidence_before = (root / EVIDENCE).read_bytes()
        frozen = program.freeze(root, EXPERIMENT)
        self.assertTrue(frozen.is_file())
        frozen_before = frozen.read_bytes()
        with self.assertRaises(ValueError):
            program.freeze(root, EXPERIMENT)
        result = program.run_inventory(root, EXPERIMENT)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["evidence_kind"], "deterministic_audit")
        self.assertEqual(result["outcomes"]["entries_checked"], 1)
        self.assertEqual(result["outcomes"]["native_behavior_probes_executed"], 0)
        self.assertEqual(result["outcomes"]["model_calls"], 0)
        self.assertEqual(result["costs"]["model_execution_usd"], 0)
        self.assertIsNone(result["costs"]["human_minutes"])
        self.assertEqual((root / CATALOG).read_bytes(), catalog_before)
        self.assertEqual((root / EVIDENCE).read_bytes(), evidence_before)
        self.assertEqual(frozen.read_bytes(), frozen_before)
        experiment_dir = (root / PLAN).parent
        files_before = {
            path.relative_to(experiment_dir): path.read_bytes()
            for path in experiment_dir.rglob("*") if path.is_file()
        }
        with self.assertRaises(ValueError):
            program.run_inventory(root, EXPERIMENT)
        self.assertEqual({
            path.relative_to(experiment_dir): path.read_bytes()
            for path in experiment_dir.rglob("*") if path.is_file()
        }, files_before)
        self.assertEqual(read_json(root / CATALOG)["milestones"][0]["workflow"]["state"], "open")
        self.assertEqual([item["claim_id"] for item in program.next_items(root)], ["M-001"])


if __name__ == "__main__":
    unittest.main()
