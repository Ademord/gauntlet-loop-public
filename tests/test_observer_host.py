"""Host adapter tests using synthetic sessions and a temporary SQLite database."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import observer_host as host


class ObserverHostTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="observer-host-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.db = self.root / "observer.sqlite3"
        self.cwd = str(self.root / "workspace")
        host.init_db(self.db)

    def arm(self, chosen="codex", **kwargs):
        return host.arm(self.db, chosen, self.cwd, "task-one", {"host": chosen}, **kwargs)

    def start(self, raw_id="one", chosen="codex", cwd=None, event="SessionStart", auto_enroll=False, **extra):
        return host.ingest_hook(self.db, chosen, {
            "session_id": raw_id, "hook_event_name": event,
            "cwd": self.cwd if cwd is None else cwd, **extra,
        }, auto_enroll=auto_enroll)

    def rows(self, table):
        self.assertIn(table, {"sessions", "events", "pending_enrollments", "measurements"})
        with closing(sqlite3.connect(self.db)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(f"SELECT * FROM {table}")]

    def test_manual_registration_namespaces_identical_host_session_ids(self):
        for chosen in ("codex", "claude"):
            host.register(self.db, chosen, "same-id", chosen + "-task", {"host": chosen})
            self.assertEqual(self.start("same-id", chosen, event="Stop")["status"], "recorded")
            self.assertEqual(host.report(self.db, chosen, "same-id")["task_id"], chosen + "-task")
        self.assertEqual({row["session_id"] for row in self.rows("sessions")},
                         {"codex:same-id", "claude:same-id"})

    def test_arm_rejects_invalid_configuration_cwd_ttl_and_host(self):
        for config in ({"host": "claude"}, {}, {"host": "codex", "prompt": "private"},
                       {"host": "codex", "request_sha256": "bad"}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                host.arm(self.db, "codex", self.cwd, "task", config)
        for ttl in (False, 0, -1, 3601, 1.5):
            with self.subTest(ttl=ttl), self.assertRaises(ValueError):
                self.arm(ttl_seconds=ttl)
        with self.assertRaises(ValueError):
            host.arm(self.db, "codex", "relative/path", "task", {"host": "codex"})
        with self.assertRaises(ValueError):
            host.register(self.db, "other", "session", "task", {"host": "other"})
        with self.assertRaises(ValueError):
            host.register(self.db, "codex", "session", "task", {"host": "claude"})
        self.assertEqual(self.rows("sessions"), [])
        self.assertEqual(self.rows("pending_enrollments"), [])

    def test_only_exact_host_cwd_and_session_start_can_consume(self):
        self.arm()
        attempts = [
            {"chosen": "claude"}, {"cwd": str(Path(self.cwd).parent)},
            {"cwd": str(Path(self.cwd) / "child")}, {"event": "PreToolUse"},
            {"event": "UnsupportedEvent"},
        ]
        for attempt in attempts:
            with self.subTest(attempt=attempt):
                self.assertEqual(self.start(**attempt)["status"], "ignored")
                self.assertEqual(self.rows("sessions"), [])
                self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])
        self.assertEqual(self.start()["status"], "recorded")
        report = host.report(self.db, "codex", "one")
        self.assertEqual(report["config"]["capture_scope"], "next-session-from-enrollment")
        self.assertEqual(report["collector_sha256"], hashlib.sha256(Path(host.observer.__file__).read_bytes()).hexdigest())
        self.assertEqual(len(self.rows("measurements")), len(host.observer.REASONS))

    def test_normalized_cwd_matches_without_prefix_enrollment(self):
        self.arm()
        equivalent = os.path.join(self.cwd, "child", "..", ".")
        if os.name == "nt":
            equivalent = equivalent.upper()
        self.assertEqual(self.start(cwd=equivalent)["status"], "recorded")

    def test_duplicate_pending_enrollment_is_rejected_per_host_cwd(self):
        self.arm()
        with self.assertRaises(ValueError):
            self.arm()
        self.arm("claude")
        self.assertEqual(len(self.rows("pending_enrollments")), 2)

    def test_expired_enrollment_cannot_register_and_can_be_rearmed(self):
        with patch.object(host.time, "time", return_value=100):
            self.arm(ttl_seconds=1)
        with patch.object(host.time, "time", return_value=101):
            self.assertEqual(self.start()["status"], "ignored")
            self.arm(ttl_seconds=1)
            self.assertEqual(self.start()["status"], "recorded")
        pending = self.rows("pending_enrollments")
        self.assertIsNone(pending[0]["consumed_session_id"])
        self.assertEqual(pending[1]["consumed_session_id"], "codex:one")

    def test_consumption_is_one_shot_and_repeated_start_preserves_new_arm(self):
        self.arm()
        self.start()
        self.assertEqual(self.start("two")["status"], "ignored")
        self.arm()
        self.assertEqual(self.start()["status"], "recorded")
        self.assertIsNone(self.rows("pending_enrollments")[1]["consumed_session_id"])
        self.assertEqual(self.start("two")["status"], "recorded")
        self.assertEqual(len(self.rows("sessions")), 2)

    def test_concurrent_starts_consume_at_most_one_enrollment(self):
        self.arm()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.start, ["one", "two"]))
        self.assertCountEqual([r["status"] for r in results], ["recorded", "ignored"])
        self.assertEqual(len(self.rows("sessions")), 1)
        self.assertEqual(len(self.rows("events")), 1)

    def test_registration_failure_rolls_back_pending_consumption(self):
        self.arm()
        original = host.observer._register
        def fail_after_insert(*args):
            original(*args)
            raise ValueError("synthetic registration failure")
        with patch.object(host.observer, "_register", side_effect=fail_after_insert):
            with self.assertRaises(ValueError):
                self.start()
        self.assertEqual(self.rows("sessions"), [])
        self.assertEqual(self.rows("measurements"), [])
        self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])
        self.assertEqual(self.start()["status"], "recorded")

    def test_all_core_lifecycle_events_route_without_storing_payload_contents(self):
        self.arm()
        self.start()
        for event in host.observer.EVENTS:
            with self.subTest(event=event):
                result = self.start(event=event, prompt="PRIVATE_PROMPT", tool_input={"x": "PRIVATE_TOOL"})
                self.assertEqual(result["status"], "recorded")
        with closing(sqlite3.connect(self.db)) as conn:
            contents = "\n".join(conn.iterdump())
        self.assertNotIn("PRIVATE_PROMPT", contents)
        self.assertNotIn("PRIVATE_TOOL", contents)

    def test_cli_hook_is_silent_and_fail_open_on_success_ignore_and_error(self):
        self.arm()
        payload = {"session_id": "one", "hook_event_name": "SessionStart", "cwd": self.cwd}
        cases = [json.dumps(payload).encode(), b'{"session_id":"other","hook_event_name":"Stop"}',
                 b'not-json PRIVATE_BAD_PAYLOAD', b'x' * (host.observer.MAX_PAYLOAD + 1)]
        for raw in cases:
            with self.subTest(size=len(raw)):
                result = subprocess.run([sys.executable, str(Path(host.__file__)), "--db", str(self.db),
                                         "--host", "codex", "hook"], input=raw, capture_output=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
        diagnostics = (self.root / "collector-errors.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("PRIVATE_BAD_PAYLOAD", diagnostics)
        self.assertEqual(len(self.rows("sessions")), 1)

    def test_auto_enrollment_is_opt_in_and_missing_database_is_not_created(self):
        for event in host.observer.EVENTS:
            self.assertEqual(self.start(event=event)["status"], "ignored")
        self.assertEqual(self.rows("sessions"), [])
        missing = self.root / "missing.sqlite3"
        self.assertEqual(host.ingest_hook(missing, "codex", {
            "session_id": "new", "hook_event_name": "Stop"}, auto_enroll=True)["status"], "ignored")
        self.assertFalse(missing.exists())
        for option in (1, "true", None):
            with self.subTest(option=option), self.assertRaises(ValueError):
                host.ingest_hook(self.db, "codex", {}, auto_enroll=option)

    def test_any_supported_event_can_be_first_for_both_hosts(self):
        for chosen in ("codex", "claude"):
            for event in sorted(host.observer.EVENTS):
                with self.subTest(host=chosen, event=event):
                    raw_id = "ongoing-" + event
                    self.assertEqual(self.start(raw_id, chosen, event=event, auto_enroll=True)["status"], "recorded")
                    report = host.report(self.db, chosen, raw_id)
                    self.assertEqual(report["events"]["by_event"], {event: 1})
                    self.assertEqual(report["config"], {
                        "host": chosen, "capture_scope": "all-local-from-first-observed-event"})
                    self.assertEqual(report["task_id"], "auto:" + hashlib.sha256(
                        (chosen + ":" + raw_id).encode("utf-8")).hexdigest())
                    for metric in host.observer.REASONS:
                        self.assertIsNone(report[metric])
                    self.assertEqual(report["outcomes"], [])
                    self.assertEqual(report["coverage"]["status"], "incomplete")
        self.assertEqual(len({r["task_id"] for r in self.rows("sessions")}), 2 * len(host.observer.EVENTS))

    def test_auto_captures_no_cwd_prompt_transcript_or_document_contents(self):
        secret_cwd = str(self.root / "PRIVATE_CWD")
        payload = {"session_id": "ongoing", "hook_event_name": "PreToolUse",
                   "cwd": secret_cwd, "tool_name": "Read", "tool_use_id": "call-1",
                   "prompt": "PRIVATE_PROMPT", "tool_input": {"path": "PRIVATE_DOCUMENT"},
                   "tool_response": "PRIVATE_RESPONSE", "transcript_path": "PRIVATE_TRANSCRIPT"}
        self.assertEqual(host.ingest_hook(self.db, "claude", payload, auto_enroll=True)["status"], "recorded")
        with closing(sqlite3.connect(self.db)) as conn:
            contents = "\n".join(conn.iterdump())
        for secret in ("PRIVATE_CWD", "PRIVATE_PROMPT", "PRIVATE_DOCUMENT", "PRIVATE_RESPONSE", "PRIVATE_TRANSCRIPT"):
            self.assertNotIn(secret, contents)
        self.assertEqual(self.rows("pending_enrollments"), [])
        self.assertEqual(host.ingest_hook(self.db, "codex", {
            "session_id": "without-cwd", "hook_event_name": "Stop"}, auto_enroll=True)["status"], "recorded")

    def test_auto_preserves_explicit_registration_and_does_not_consume_pending(self):
        config = {"host": "codex", "effort": "high", "workflow": "explicit-fixture"}
        host.register(self.db, "codex", "one", "explicit-task", config)
        self.arm()
        before = self.rows("sessions")
        measures = self.rows("measurements")
        for event in ("Stop", "SessionStart"):
            self.assertEqual(self.start(event=event, auto_enroll=True)["status"], "recorded")
        self.assertEqual(self.rows("sessions"), before)
        self.assertEqual(self.rows("measurements"), measures)
        self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])

    def test_exact_pending_start_wins_over_auto_enrollment(self):
        self.arm()
        self.assertEqual(self.start(auto_enroll=True)["status"], "recorded")
        report = host.report(self.db, "codex", "one")
        self.assertEqual(report["task_id"], "task-one")
        self.assertEqual(report["config"]["capture_scope"], "next-session-from-enrollment")
        self.assertEqual(self.rows("pending_enrollments")[0]["consumed_session_id"], "codex:one")

    def test_auto_mismatched_host_cwd_and_nonstart_leave_pending_intact(self):
        self.arm()
        for raw_id, kwargs in [("other-host", {"chosen":"claude"}),
                               ("other-cwd", {"cwd":str(Path(self.cwd)/"nested")}),
                               ("ongoing", {"event":"PreToolUse"})]:
            self.assertEqual(self.start(raw_id, auto_enroll=True, **kwargs)["status"], "recorded")
            self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])
        # A later start for the already auto-enrolled ongoing session must not
        # change its attribution or steal the pending task.
        before = host.report(self.db,"codex","ongoing")["task_id"]
        self.start("ongoing", auto_enroll=True)
        self.assertEqual(host.report(self.db,"codex","ongoing")["task_id"], before)
        self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])
        self.start("eligible", auto_enroll=True)
        self.assertEqual(host.report(self.db,"codex","eligible")["task_id"],"task-one")

    def test_expired_pending_allows_auto_without_consuming_old_arm(self):
        with patch.object(host.time,"time",return_value=100):
            self.arm(ttl_seconds=1)
        with patch.object(host.time,"time",return_value=101):
            self.start(auto_enroll=True)
        self.assertTrue(host.report(self.db,"codex","one")["task_id"].startswith("auto:"))
        self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])

    def test_malformed_first_event_never_registers_or_consumes_pending(self):
        self.arm()
        base = {"session_id":"bad", "hook_event_name":"SessionStart", "cwd":self.cwd}
        bad_fields = [{"tool_name": {"not":"metadata"}}, {"model":"bad\nmodel"},
                      {"turn_id":"x"*(host.observer.MAX_METADATA+1)}, {"session_id":True},
                      {"session_id":"bad\nID"}, {"cwd":42}, {"cwd":"relative/path"},
                      {"unretained":float("nan")}, {"prompt":"x"*host.observer.MAX_PAYLOAD}]
        for fields in bad_fields:
            with self.subTest(fields=list(fields)), self.assertRaises((ValueError,TypeError)):
                host.ingest_hook(self.db,"codex",dict(base,**fields),auto_enroll=True)
        for fields in ({"hook_event_name":"UnsupportedEvent"}, {"session_id":None}, {"session_id":""}):
            self.assertEqual(host.ingest_hook(self.db,"codex",dict(base,**fields),auto_enroll=True)["status"], "ignored")
        self.assertEqual(self.rows("sessions"), [])
        self.assertEqual(self.rows("events"), [])
        self.assertEqual(self.rows("measurements"), [])
        self.assertIsNone(self.rows("pending_enrollments")[0]["consumed_session_id"])

    def test_concurrent_auto_enrollment_is_single_and_tool_deduplication_survives(self):
        def arrival(_):
            return self.start("concurrent", event="PreToolUse", auto_enroll=True,
                              tool_use_id="same-call", turn_id="same-turn")
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(arrival, range(8)))
        self.assertCountEqual([r["status"] for r in results], ["recorded"] + ["duplicate"]*7)
        self.assertEqual(len(self.rows("sessions")),1)
        self.assertEqual(len(self.rows("measurements")),len(host.observer.REASONS))
        self.assertEqual(len(self.rows("events")),1)

    def test_concurrent_auto_starts_one_pending_task_and_one_opaque_task(self):
        self.arm()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda name:self.start(name,auto_enroll=True), ["one","two"]))
        self.assertEqual([r["status"] for r in results], ["recorded","recorded"])
        tasks = [row["task_id"] for row in self.rows("sessions")]
        self.assertEqual(tasks.count("task-one"),1)
        self.assertEqual(sum(task.startswith("auto:") for task in tasks),1)
        self.assertEqual(len(self.rows("events")),2)

    def test_auto_registration_failure_rolls_back_session_and_measurements(self):
        original = host.observer._register
        def fail_after_insert(*args):
            original(*args)
            raise ValueError("synthetic failure")
        with patch.object(host.observer,"_register",side_effect=fail_after_insert):
            with self.assertRaises(ValueError):
                self.start(event="Stop",auto_enroll=True)
        self.assertEqual(self.rows("sessions"),[])
        self.assertEqual(self.rows("measurements"),[])
        self.assertEqual(self.rows("events"),[])
        self.assertEqual(self.start(event="Stop",auto_enroll=True)["status"],"recorded")

    def test_cli_auto_opt_in_is_silent_and_keeps_unknown_metrics(self):
        payload = {"session_id":"ongoing-cli", "hook_event_name":"Stop", "prompt":"PRIVATE_CONTENT"}
        command = [sys.executable,"-B",str(Path(host.__file__)),"--db",str(self.db),
                   "--host","claude","hook","--auto-enroll"]
        for raw in (json.dumps(payload).encode(), b'not-json PRIVATE_BAD_PAYLOAD'):
            result = subprocess.run(command,input=raw,capture_output=True,timeout=15)
            self.assertEqual((result.returncode,result.stdout,result.stderr),(0,b"",b""))
        report = host.report(self.db,"claude","ongoing-cli")
        self.assertEqual(report["events"]["by_event"],{"Stop":1})
        self.assertIsNone(report["cost_usd"])
        self.assertEqual(report["outcomes"],[])
        self.assertNotIn("PRIVATE_BAD_PAYLOAD",(self.root/"collector-errors.jsonl").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
