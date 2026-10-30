"""Synthetic eligibility controls; no models, network, or real state changes."""

import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from evidence_use import MAX_BYTES, assess_use


class EvidenceUseTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {"id": "E1", "bindings": {
            "artifact": "build-1", "criteria": "rules-1", "scope": "local"},
            "lineage": {"root_observation_ids": ["O1"], "derived_from": []}}
        self.use = {"kind": "current_acceptance", "claim": "local-correction",
                    "material_conditions": {"artifact": "evidence", "criteria": "evidence",
                                            "review": "context", "lifecycle": "context"}}
        self.context = {"expected_conditions": {
            "artifact": "build-1", "criteria": "rules-1", "review": "verified", "lifecycle": "active"},
            "observed_conditions": {"review": "verified", "lifecycle": "active"},
            "historical_expectations": {"artifact": "build-1", "criteria": "rules-1"}}

    def assess(self):
        return assess_use(self.evidence, self.use, self.context)

    def cli(self, data):
        return subprocess.run(
            [sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "tools/evidence_use.py")],
            input=data, capture_output=True, check=False)

    def test_current_reviewed_identity_control_is_eligible(self):
        result = self.assess()
        self.assertEqual(result["status"], "eligible")
        self.assertEqual(result["material_unmet"], [])
        self.assertEqual(result["historical_validity"], "eligible")

    def test_same_artifact_changed_criteria_is_not_current_evidence(self):
        before = copy.deepcopy(self.evidence)
        self.context["expected_conditions"]["criteria"] = "rules-2"
        result = self.assess()
        self.assertEqual(result["status"], "ineligible")
        self.assertEqual(result["historical_validity"], "eligible")
        self.assertEqual(self.evidence, before)

    def test_historical_question_does_not_require_current_lifecycle(self):
        self.use = {"kind": "historical_report", "claim": "old-check-result",
                    "material_conditions": {"artifact": "evidence", "criteria": "evidence"}}
        self.context["observed_conditions"]["lifecycle"] = "cancelled"
        self.assertEqual(self.assess()["status"], "eligible")

    def test_cancelled_current_use_fails_even_with_current_hash(self):
        self.context["observed_conditions"]["lifecycle"] = "cancelled"
        result = self.assess()
        self.assertEqual(result["status"], "ineligible")
        self.assertIn({"condition": "lifecycle", "reason": "condition_mismatch"}, result["material_unmet"])

    def test_missing_selected_condition_is_unknown_and_does_not_accept(self):
        del self.context["observed_conditions"]["review"]
        result = self.assess()
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["next_observations"], ["Establish review for this use"])

    def test_unknown_expected_value_cannot_copy_evidence_as_expectation(self):
        del self.context["expected_conditions"]["criteria"]
        self.assertEqual(self.assess()["status"], "unknown")
        self.context["expected_conditions"]["criteria"] = None
        self.assertEqual(self.assess()["status"], "unknown")

    def test_evidence_self_assertion_does_not_replace_host_review(self):
        self.evidence["bindings"]["review"] = "verified"
        self.context["observed_conditions"].pop("review")
        self.assertEqual(self.assess()["status"], "unknown")
        self.context["observed_conditions"]["review"] = "unreviewed"
        self.assertEqual(self.assess()["status"], "ineligible")

    def test_irrelevant_fields_do_not_add_gates(self):
        self.evidence["bindings"]["unselected_remote"] = "unavailable"
        self.context["expected_conditions"]["unselected_remote"] = "healthy"
        self.context["observed_conditions"]["unselected_remote"] = None
        self.assertEqual(self.assess()["status"], "eligible")

    def test_authorized_read_only_investigation_survives_failed_acceptance(self):
        self.context.update(investigation_authorized=True, investigation_read_only=True)
        self.context["observed_conditions"]["review"] = None
        self.assertEqual(self.assess()["status"], "unknown")
        self.assertTrue(self.assess()["can_investigate"])
        investigation = {"kind": "investigation", "claim": "inspect-existing-log",
                         "material_conditions": {"authorized": "context", "read_only": "context"}}
        context = {"expected_conditions": {"authorized": True, "read_only": True},
                   "observed_conditions": {"authorized": True, "read_only": True}}
        self.assertEqual(assess_use(self.evidence, investigation, context)["status"], "eligible")
        context["observed_conditions"]["authorized"] = False
        self.assertEqual(assess_use(self.evidence, investigation, context)["status"], "ineligible")

    def test_consequential_action_uses_current_permission_and_destination(self):
        self.use["kind"] = "consequential_action"
        self.use["material_conditions"].update(authorized="context", destination="evidence")
        self.context["expected_conditions"].update(authorized=True, destination="D2")
        self.context["observed_conditions"]["authorized"] = True
        self.evidence["bindings"]["destination"] = "D1"
        self.assertEqual(self.assess()["status"], "ineligible")
        self.evidence["bindings"]["destination"] = "D2"
        self.assertEqual(self.assess()["status"], "eligible")
        self.context["observed_conditions"]["authorized"] = False
        self.assertEqual(self.assess()["status"], "ineligible")

    def test_known_failure_is_not_hidden_by_a_second_unknown(self):
        self.context["observed_conditions"]["review"] = None
        self.context["observed_conditions"]["lifecycle"] = "cancelled"
        self.assertEqual(self.assess()["status"], "ineligible")

    def test_copied_descendants_do_not_increase_independent_support(self):
        self.evidence["lineage"] = {"root_observation_ids": ["O1", "O1", "O1"],
                                    "derived_from": ["summary-1", "repost-1"]}
        self.context["verified_observation_ids"] = ["O1"]
        self.use["minimum_independent_observations"] = 2
        result = self.assess()
        self.assertEqual(result["status"], "ineligible")
        self.assertEqual(result["lineage"]["verified_root_observation_ids"], ["O1"])
        self.assertEqual(result["lineage"]["derived_from"], ["repost-1", "summary-1"])
        self.evidence["lineage"]["root_observation_ids"].append("O2")
        self.context["verified_observation_ids"].append("O2")
        self.assertEqual(self.assess()["status"], "eligible")

    def test_missing_independence_metadata_remains_unknown(self):
        self.use["minimum_independent_observations"] = 1
        self.assertEqual(self.assess()["status"], "unknown")
        self.context["verified_observation_ids"] = []
        self.assertEqual(self.assess()["status"], "ineligible")
        self.evidence.pop("lineage")
        self.assertEqual(self.assess()["status"], "unknown")

    def test_json_equality_is_structural_and_strictly_typed(self):
        self.use["material_conditions"] = {"setting": "evidence"}
        for actual, expected, status in [
            (True, 1, "ineligible"), (False, 0, "ineligible"),
            (1, 1.0, "ineligible"), ([1, 2], [2, 1], "ineligible"),
            ({"a": 1, "b": [True]}, {"b": [True], "a": 1}, "eligible"),
            (None, None, "unknown")]:
            with self.subTest(actual=actual, expected=expected):
                self.evidence["bindings"]["setting"] = actual
                self.context["expected_conditions"]["setting"] = expected
                self.assertEqual(self.assess()["status"], status)

    def test_exact_library_decimal_controls_and_bounds(self):
        self.use["material_conditions"] = {"setting": "evidence"}
        cases = [
            (Decimal("9007199254740992.0"), Decimal("9007199254740993.0"), "ineligible"),
            (Decimal("1e-400"), Decimal("2e-400"), "ineligible"),
            (Decimal("0.1"), Decimal("0.100"), "eligible"),
            (Decimal("1e-400"), Decimal("1e-400"), "eligible"),
            (Decimal("1.0"), 1, "ineligible"),
            (Decimal("1.0"), 1.0, "ineligible"),
            (Decimal("NaN"), Decimal("NaN"), "unknown"),
            (Decimal("1e-1025"), Decimal("1e-1025"), "unknown"),
            (Decimal("1" * 257 + ".0"), Decimal("1" * 257 + ".0"), "unknown"),
        ]
        for actual, expected, status in cases:
            with self.subTest(actual=actual, expected=expected):
                self.evidence["bindings"]["setting"] = actual
                self.context["expected_conditions"]["setting"] = expected
                self.assertEqual(self.assess()["status"], status)

    def test_cli_preserves_decimal_precision_and_range(self):
        # Keep the source tokens raw: json.dumps of Python floats would already
        # have lost the very information these independent counterexamples test.
        template = ('{"evidence":{"id":"numeric","bindings":{"threshold":%s}},'
                    '"proposed_use":{"kind":"consequential_action","claim":"numeric comparison",'
                    '"material_conditions":{"threshold":"evidence"}},'
                    '"current_context":{"expected_conditions":{"threshold":%s}}}')
        cases = [
            ("9007199254740992.0", "9007199254740993.0", "ineligible", 1),
            ("1e-400", "2e-400", "ineligible", 1),
            ("9007199254740993.0", "9007199254740993.0", "eligible", 0),
            ("1e-400", "1.0e-400", "eligible", 0),
            ("0.1", "0.100", "eligible", 0),
            ("1.0", "1", "ineligible", 1),
            ("1e-1025", "1e-1025", "unknown", 2),
            ("1e1025", "1e1025", "unknown", 2),
            ("1" * 257 + ".0", "1" * 257 + ".0", "unknown", 2),
        ]
        for actual, expected, status, code in cases:
            with self.subTest(actual=actual, expected=expected):
                result = self.cli((template % (actual, expected)).encode())
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], status)
                self.assertEqual(result.stderr, b"")

    def test_empty_selection_is_not_vacuous_acceptance(self):
        self.use["material_conditions"] = {}
        self.assertEqual(self.assess()["status"], "unknown")

    def test_inputs_are_unchanged_and_no_io_occurs(self):
        inputs = copy.deepcopy((self.evidence, self.use, self.context))
        with patch("builtins.open", side_effect=AssertionError("unexpected file access")):
            self.assertEqual(self.assess()["status"], "eligible")
        self.assertEqual((self.evidence, self.use, self.context), inputs)

    def test_malformed_or_unbounded_library_inputs_return_unknown(self):
        cases = [None, [], {"id": "E1", "extra": True}, {"id": ""},
                 {"id": "E1", "bindings": {"x": float("nan")}},
                 {"id": "E1", "bindings": {"x": "z" * 4097}},
                 {"id": "E1", "lineage": {"root_observation_ids": [True]}},
                 {"id": "E1", "bindings": {"x": 2**1025}}]
        cyclic = {"id": "E1", "bindings": {}}
        cyclic["bindings"]["x"] = cyclic
        cases.append(cyclic)
        for evidence in cases:
            with self.subTest(case=type(evidence).__name__):
                self.assertEqual(assess_use(evidence, self.use, self.context)["status"], "unknown")
        for key, value in [("kind", "execute-code"), ("kind", []),
                           ("minimum_independent_observations", True),
                           ("material_conditions", {"review": "auto"})]:
            changed = dict(self.use, **{key: value})
            self.assertEqual(assess_use(self.evidence, changed, self.context)["status"], "unknown")

    def test_cli_exit_codes_and_strict_json(self):
        request = {"evidence": self.evidence, "proposed_use": self.use, "current_context": self.context}
        result = self.cli(json.dumps(request).encode())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "eligible")
        self.context["observed_conditions"]["lifecycle"] = "cancelled"
        result = self.cli(json.dumps(request).encode())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "ineligible")
        invalid = [b"", b"{}", b"null", b"\xff", b'{"evidence":{},"evidence":{}}',
                   b'{"number":NaN}', b" " * (MAX_BYTES + 1), b"[" * 2000 + b"]" * 2000]
        for raw in invalid:
            with self.subTest(size=len(raw)):
                result = self.cli(raw)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], "unknown")
                self.assertEqual(result.stderr, b"")


if __name__ == "__main__":
    unittest.main()
