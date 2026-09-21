"""Local observer boundary tests; no real sessions, hooks, or model calls."""

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from tools import observer


REPOSITORY = Path(__file__).resolve().parents[1]
OBSERVER = REPOSITORY / "tools/observer.py"
SESSION = "fixture-session"
CONFIG = {"host": "codex", "client_version": "fixture-version"}


class ObserverTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / "observer.sqlite3"
        observer.init_db(self.database)
        observer.register_session(self.database, SESSION, "fixture-task", CONFIG)

    def events(self):
        with closing(sqlite3.connect(self.database)) as connection:
            connection.row_factory = sqlite3.Row
            return [dict(row) for row in connection.execute("SELECT * FROM events")]

    def database_contents(self):
        with closing(sqlite3.connect(self.database)) as connection:
            return "\n".join(connection.iterdump())

    def hook(self, event="PreToolUse", **fields):
        return {"session_id": SESSION, "hook_event_name": event,
                "tool_name": "Bash", **fields}

    def test_unregistered_session_is_ignored_without_saving_payload(self):
        payload = self.hook(session_id="unregistered", prompt="PRIVATE_UNREGISTERED_PROMPT",
                            tool_input={"command": "PRIVATE_UNREGISTERED_COMMAND"})
        result = observer.ingest_hook(self.database, payload)
        self.assertEqual(result["status"], "ignored")
        self.assertEqual(self.events(), [])
        contents = self.database_contents()
        self.assertNotIn("PRIVATE_UNREGISTERED_PROMPT", contents)
        self.assertNotIn("PRIVATE_UNREGISTERED_COMMAND", contents)
        self.assertNotIn("unregistered", contents)

    def test_only_metadata_is_stored_from_registered_hook_payload(self):
        secrets = ["PRIVATE_PROMPT_SENTINEL", "PRIVATE_COMMAND_SENTINEL",
                   "PRIVATE_RESPONSE_SENTINEL", "PRIVATE_PATH_SENTINEL",
                   "PRIVATE_TRANSCRIPT_SENTINEL"]
        payload = self.hook(tool_use_id="call-one", turn_id="turn-one",
                            prompt=secrets[0], tool_input={"command": secrets[1], "file_path": secrets[3]},
                            tool_response={"stdout": secrets[2]}, cwd=secrets[3],
                            transcript_path=secrets[4])
        self.assertEqual(observer.ingest_hook(self.database, payload)["status"], "recorded")
        self.assertEqual(len(self.events()), 1)
        contents = self.database_contents()
        for secret in secrets:
            with self.subTest(secret=secret):
                self.assertNotIn(secret, contents)
        self.assertIn("call-one", contents)
        self.assertIn("PreToolUse", contents)

    def test_stable_tool_ids_deduplicate_each_event_type_separately(self):
        for event in ("PreToolUse", "PostToolUse"):
            payload = self.hook(event, tool_use_id="same-call", turn_id="same-turn")
            self.assertEqual(observer.ingest_hook(self.database, payload)["status"], "recorded")
            self.assertEqual(observer.ingest_hook(self.database, payload)["status"], "duplicate")
        self.assertEqual(len(self.events()), 2)

    def test_identical_events_without_identity_are_both_retained(self):
        payload = self.hook()
        self.assertEqual(observer.ingest_hook(self.database, payload)["status"], "recorded")
        self.assertEqual(observer.ingest_hook(self.database, payload)["status"], "recorded")
        self.assertEqual(len(self.events()), 2)

    def test_claude_prompt_identity_and_failures_remain_metadata_only(self):
        for event in ('PreToolUse', 'PostToolUseFailure'):
            for prompt_id in ('prompt-one', 'prompt-two'):
                payload = self.hook(event, tool_use_id='repeated-tool-id', prompt_id=prompt_id,
                                    error='PRIVATE_FAILURE_CONTENT', is_interrupt=True)
                self.assertEqual(observer.ingest_hook(self.database, payload)['status'], 'recorded')
                self.assertEqual(observer.ingest_hook(self.database, payload)['status'], 'duplicate')
        observer.ingest_hook(self.database, self.hook('StopFailure', error='PRIVATE_STOP_ERROR'))
        report = observer.session_report(self.database, SESSION)
        self.assertEqual(report['events']['tool_failures'], 2)
        self.assertEqual(report['events']['tool_ends'], 0)
        self.assertEqual(report['outcomes'], [])
        self.assertNotIn('PRIVATE_FAILURE_CONTENT', self.database_contents())
        self.assertNotIn('PRIVATE_STOP_ERROR', self.database_contents())

    def test_duplicate_enrollment_cannot_replace_task_or_configuration(self):
        before = self.database_contents()
        with self.assertRaises((ValueError, sqlite3.IntegrityError)):
            observer.register_session(self.database, SESSION, "replacement-task",
                                      {"host": "different-host"})
        self.assertEqual(self.database_contents(), before)

    def test_stop_is_an_observation_not_independent_acceptance(self):
        observer.ingest_hook(self.database, self.hook("Stop", stop_hook_active=False,
                                                    last_assistant_message="All checks passed."))
        report = observer.session_report(self.database, SESSION)
        self.assertEqual(report["collection_mode"], "observational")
        self.assertEqual(report["events"]["total"], 1)
        self.assertEqual(report["outcomes"], [])
        self.assertNotIn("All checks passed.", self.database_contents())

    def test_prompt_and_interrupt_events_do_not_store_conversation_content(self):
        for event in ("UserPromptSubmit", "Interrupt"):
            payload = {"session_id": SESSION, "hook_event_name": event,
                       "prompt": "PRIVATE_USER_PROMPT", "last_assistant_message": "PRIVATE_ANSWER"}
            self.assertEqual(observer.ingest_hook(self.database, payload)["status"], "recorded")
        self.assertEqual(len(self.events()), 2)
        contents = self.database_contents()
        self.assertNotIn("PRIVATE_USER_PROMPT", contents)
        self.assertNotIn("PRIVATE_ANSWER", contents)
        self.assertEqual(observer.session_report(self.database, SESSION)["outcomes"], [])

    def test_changed_collector_identity_refuses_capture_and_is_reported(self):
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("UPDATE sessions SET collector_sha256 = ? WHERE session_id = ?",
                               ("0" * 64, SESSION))
            connection.commit()
        with self.assertRaises(ValueError):
            observer.ingest_hook(self.database, self.hook(tool_use_id="changed-collector-call"))
        self.assertEqual(self.events(), [])
        self.assertFalse(observer.session_report(self.database, SESSION)["collector_matches_current"])

    def test_prompt_uuid_deduplicates_delivery_without_merging_distinct_contacts(self):
        for prompt_id in ('first-prompt', 'second-prompt'):
            payload = self.hook('UserPromptSubmit', prompt_id=prompt_id, prompt='same message')
            self.assertEqual(observer.ingest_hook(self.database, payload)['status'], 'recorded')
            self.assertEqual(observer.ingest_hook(self.database, payload)['status'], 'duplicate')
        self.assertEqual(len(self.events()), 2)

    def test_missing_usage_and_human_effort_remain_unknown(self):
        observer.ingest_hook(self.database, self.hook("Stop"))
        report = observer.session_report(self.database, SESSION)
        for metric in ("tokens", "cost_usd", "human_minutes"):
            with self.subTest(metric=metric):
                self.assertIsNone(report[metric])
                self.assertTrue(report["measurement_reasons"][metric])
        self.assertEqual(report["coverage"]["status"], "incomplete")

    def test_identityless_capture_discloses_uncertain_deduplication(self):
        observer.ingest_hook(self.database, self.hook())
        observer.ingest_hook(self.database, self.hook())
        report = observer.session_report(self.database, SESSION)
        self.assertEqual(report["deduplication"]["identityless_events"], 2)
        self.assertEqual(report["events"]["identityless"], 2)

    def test_configuration_rejects_raw_content_and_nonfinite_metadata(self):
        for config in ({"prompt": "PRIVATE_CONFIGURATION_PROMPT"},
                       {"effort": float("nan")}, {"effort": float("inf")}):
            with self.subTest(config=config):
                before = self.database_contents()
                with self.assertRaises((ValueError, TypeError)):
                    observer.register_session(self.database, "invalid-config", "fixture-task", config)
                self.assertEqual(self.database_contents(), before)

    def test_outcome_requires_artifact_and_check_identity(self):
        values = {"artifact_hash": "a" * 64, "check_hash": "b" * 64,
                  "evaluator": "independent fixture evaluator",
                  "evidence": "fixture-check-log-sha256:" + "c" * 64, "outcome": "passed"}
        for field in ("artifact_hash", "check_hash"):
            with self.subTest(field=field):
                invalid = dict(values, **{field: ""})
                with self.assertRaises(ValueError):
                    observer.record_outcome(self.database, SESSION, **invalid)
                self.assertEqual(observer.session_report(self.database, SESSION)["outcomes"], [])
        observer.record_outcome(self.database, SESSION, **values)
        report = observer.session_report(self.database, SESSION)
        self.assertEqual(len(report["outcomes"]), 1)
        self.assertEqual(report["outcomes"][0]["outcome"], "passed")
        self.assertEqual(report["outcomes"][0]["artifact_hash"], values["artifact_hash"])
        self.assertEqual(report["outcomes"][0]["check_hash"], values["check_hash"])
        self.assertEqual(report["collection_mode"], "observational")


class SilentHookTest(unittest.TestCase):
    def test_registered_hook_records_metadata_without_output_or_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "observer.sqlite3"
            observer.init_db(database)
            observer.register_session(database, SESSION, "fixture-task", CONFIG)
            payload = json.dumps({"session_id": SESSION, "hook_event_name": "PreToolUse",
                                  "tool_name": "Bash", "tool_use_id": "cli-call",
                                  "tool_input": {"command": "PRIVATE_CLI_COMMAND"}})
            completed = subprocess.run(
                [sys.executable, "-B", str(OBSERVER), "--db", str(database), "hook"],
                input=payload, capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.stderr, "")
            self.assertFalse((root / "collector-errors.jsonl").exists())
            self.assertEqual(observer.session_report(database, SESSION)["events"]["total"], 1)
            with closing(sqlite3.connect(database)) as connection:
                self.assertNotIn("PRIVATE_CLI_COMMAND", "\n".join(connection.iterdump()))

    def test_invalid_json_and_missing_database_are_silent_with_private_diagnostics(self):
        for case in ("invalid-json", "missing-database", "corrupt-database"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                database = root / "observer.sqlite3"
                secret = "PRIVATE_FAILURE_DETAIL_SENTINEL"
                if case == "invalid-json":
                    observer.init_db(database)
                    payload = '{"prompt":"' + secret
                else:
                    payload = json.dumps({"session_id": SESSION, "hook_event_name": "Stop",
                                          "prompt": secret})
                    if case == "corrupt-database":
                        database.write_bytes(b"not a sqlite database")
                completed = subprocess.run(
                    [sys.executable, "-B", str(OBSERVER), "--db", str(database), "hook"],
                    input=payload, capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(completed.returncode, 0)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(completed.stderr, "")
                diagnostic = root / "collector-errors.jsonl"
                self.assertTrue(diagnostic.is_file())
                content = diagnostic.read_text(encoding="utf-8")
                self.assertTrue(content.strip())
                self.assertNotIn(secret, content)
                for line in content.splitlines():
                    self.assertIsInstance(json.loads(line), dict)
                if case == "missing-database":
                    self.assertFalse(database.exists())


if __name__ == "__main__":
    unittest.main()
