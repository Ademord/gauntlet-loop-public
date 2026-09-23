"""Private backup and public checkpoint tests; no Git, network, or real sessions."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from tools import contact_metrics, observer, observer_checkpoint as checkpoint


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ObserverCheckpointTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="observer-checkpoint-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository = self.root / "public-repository"
        self.repository.mkdir()
        self.private = self.root / "PRIVATE_DIRECTORY"
        self.private.mkdir()
        self.db = self.private / "PRIVATE_LIVE.sqlite3"
        self.snapshot = self.private / "PRIVATE_BACKUP.sqlite3"
        self.output = self.repository / "evidence" / "checkpoint.json"
        self.selected = "codex:PRIVATE_SELECTED_SESSION"
        self.excluded = "claude:PRIVATE_EXCLUDED_SESSION"
        self.task = "PRIVATE_TASK_IDENTIFIER"
        self.root_patch = patch.object(checkpoint, "REPOSITORY", self.repository)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        observer.register_session(self.db, self.selected, self.task,
                                  {"host": "codex", "model": "PRIVATE_MODEL", "tools": [str(self.private)]})
        observer.register_session(self.db, self.excluded, "PRIVATE_EXCLUDED_TASK", {"host": "claude"})

    def export(self, sessions=None):
        return checkpoint.export_checkpoint(self.db, self.snapshot, self.output,
                                            [self.selected] if sessions is None else sessions)

    def contact(self, label, minutes=None):
        event = observer.ingest_hook(self.db, {
            "session_id": self.selected, "hook_event_name": "UserPromptSubmit",
            "prompt": "PRIVATE_RAW_MESSAGE", "cwd": str(self.private),
        })["event_id"]
        contact_metrics.label_contact(
            self.db, self.selected, event, label, actor="human", source="PRIVATE_SOURCE",
            human_minutes=minutes, minutes_basis="PRIVATE_MINUTES_BASIS" if minutes is not None else None,
        )
        return event

    def test_manifest_provenance_selection_and_private_field_exclusion(self):
        self.contact("initial_request", 1.5)
        last = self.contact("correction", 2.5)
        contact_metrics.record_resolution(self.db, self.selected, "resolved", actor="human",
                                          source="PRIVATE_RESOLUTION_SOURCE", event_id=last,
                                          evidence="PRIVATE_EVIDENCE")
        with closing(sqlite3.connect(self.db)) as conn:
            conn.execute("CREATE TABLE private_notes (body TEXT)")
            conn.execute("INSERT INTO private_notes VALUES ('PRIVATE_SAVED_PROMPT')")
            conn.commit()
        before = sha(self.db)
        manifest = self.export()
        self.assertEqual(sha(self.db), before)
        self.assertEqual(manifest["snapshot_sha256"], sha(self.snapshot))
        self.assertEqual(manifest["reporter_sha256"]["observer"], sha(Path(observer.__file__)))
        self.assertEqual(manifest["reporter_sha256"]["contact_metrics"], sha(Path(contact_metrics.__file__)))
        self.assertEqual(manifest["reporter_sha256"]["checkpoint"], sha(Path(checkpoint.__file__)))
        self.assertEqual(len(manifest["sessions"]), 1)
        session = manifest["sessions"][0]
        self.assertEqual(session["session_sha256"], hashlib.sha256(self.selected.encode()).hexdigest())
        self.assertEqual(session["task_sha256"], hashlib.sha256(self.task.encode()).hexdigest())
        self.assertEqual(session["collector_sha256"], sha(Path(observer.__file__)))
        self.assertEqual(session["captured_contacts"], 2)
        self.assertEqual(session["known_correction_count"], 1)
        self.assertEqual(session["correction_total"], 1)
        self.assertEqual(session["user_reported_resolution_state"], "resolved")
        self.assertIs(session["first_pass_resolution"], False)
        self.assertEqual(session["human_minutes"], 4.0)
        self.assertIn("captured contacts", session["human_minutes_qualifier"])
        self.assertEqual(session["coverage"], "partial")
        self.assertIsNone(session["tokens"])
        self.assertIsNone(session["cost_usd"])
        self.assertIsNone(manifest["performance_claim"])
        text = self.output.read_text(encoding="utf-8")
        self.assertNotIn("PRIVATE_", text)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn(hashlib.sha256(self.excluded.encode()).hexdigest(), text)
        self.assertEqual(json.loads(text), manifest)

    def test_contact_table_initialization_occurs_only_in_private_backup(self):
        before = sha(self.db)
        manifest = self.export()
        with closing(sqlite3.connect(self.db)) as source, closing(sqlite3.connect(self.snapshot)) as backup:
            self.assertIsNone(source.execute("SELECT name FROM sqlite_master WHERE name='contact_labels'").fetchone())
            self.assertIsNotNone(backup.execute("SELECT name FROM sqlite_master WHERE name='contact_labels'").fetchone())
        self.assertEqual(sha(self.db), before)
        self.assertEqual(manifest["snapshot_sha256"], sha(self.snapshot))
        self.assertIsNone(manifest["sessions"][0]["correction_total"])
        self.assertIsNone(manifest["sessions"][0]["human_minutes"])
        self.assertIsNone(manifest["sessions"][0]["user_reported_resolution_state"])

    def test_sqlite_backup_includes_committed_wal_state(self):
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
            conn.execute("UPDATE sessions SET task_id=? WHERE session_id=?", ("PRIVATE_WAL_TASK", self.selected))
            conn.commit()
            self.assertTrue(Path(str(self.db) + "-wal").is_file())
            before = sha(self.db)
            manifest = self.export()
            self.assertEqual(sha(self.db), before)
            self.assertEqual(manifest["sessions"][0]["task_sha256"],
                             hashlib.sha256(b"PRIVATE_WAL_TASK").hexdigest())
        self.assertEqual(manifest["snapshot_sha256"], sha(self.snapshot))

    def test_preexisting_targets_and_source_aliases_are_never_overwritten(self):
        for target in ("snapshot", "output", "source_snapshot", "source_output"):
            with self.subTest(target=target), tempfile.TemporaryDirectory(dir=self.root) as scratch:
                scratch = Path(scratch)
                snapshot = scratch / "backup.sqlite3"
                output = self.repository / (target + ".json")
                if target == "snapshot":
                    snapshot.write_bytes(b"existing-private-data")
                elif target == "output":
                    output.write_bytes(b"existing-public-data")
                elif target == "source_snapshot":
                    snapshot = self.db
                else:
                    output = self.db
                before = {path: path.read_bytes() for path in (self.db, snapshot, output) if path.is_file()}
                with self.assertRaises(ValueError):
                    checkpoint.export_checkpoint(self.db, snapshot, output, [self.selected])
                self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_private_snapshot_cannot_be_inside_repo_and_public_output_stays_inside(self):
        cases = [
            (self.repository / "private.sqlite3", self.output),
            (self.snapshot, self.private / "public.json"),
            (Path("relative-backup.sqlite3"), self.output),
            (self.output, self.output),
        ]
        before = sha(self.db)
        for snapshot, output in cases:
            with self.subTest(snapshot=snapshot, output=output), self.assertRaises(ValueError):
                checkpoint.export_checkpoint(self.db, snapshot, output, [self.selected])
        with self.assertRaises(ValueError):
            checkpoint.export_checkpoint(Path("relative-source.sqlite3"), self.snapshot, self.output, [self.selected])
        self.assertEqual(sha(self.db), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.snapshot.exists())

    def test_explicit_unique_namespaced_selection_is_required(self):
        for selection in ([], [self.selected, self.selected], ["unnamespaced"], ["other:session"]):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                self.export(selection)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.snapshot.exists())

    def test_unknown_session_cannot_produce_a_public_manifest(self):
        before = sha(self.db)
        with self.assertRaises(ValueError):
            self.export(["codex:unknown"])
        self.assertFalse(self.output.exists())
        self.assertEqual(sha(self.db), before)

    def test_unknown_and_partial_contact_minutes_stay_unknown(self):
        self.contact("initial_request", 1)
        self.contact("unknown")
        session = self.export()["sessions"][0]
        self.assertEqual(session["classification_counts"]["unknown"], 1)
        self.assertEqual(session["known_correction_count"], 0)
        self.assertIsNone(session["correction_total"])
        self.assertIsNone(session["human_minutes"])


if __name__ == "__main__":
    unittest.main()
