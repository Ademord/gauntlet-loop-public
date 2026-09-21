"""Manually export selected sanitized metrics from a new, private SQLite backup."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

if __package__ in (None, ""):
    import observer
    import contact_metrics
else:
    from . import observer, contact_metrics

REPOSITORY = Path(__file__).resolve().parents[1]


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _session_summary(snapshot, session_id):
    observation = observer.session_report(snapshot, session_id)
    contact = contact_metrics.session_report(snapshot, session_id)
    collector = observation["collector_sha256"]
    if not isinstance(collector, str) or not re.fullmatch(r"[a-f0-9]{64}", collector):
        raise ValueError("Invalid collector fingerprint")
    latest = contact["resolution"]
    state = latest["state"] if latest and latest["state"] in contact_metrics.RESOLUTIONS else None
    return {
        "session_sha256": _hash(session_id.encode("utf-8")),
        "task_sha256": _hash(observation["task_id"].encode("utf-8")),
        "collector_sha256": collector,
        "collector_matches_current": observation["collector_matches_current"],
        "metric_scope": "partial", "coverage": "partial",
        "event_counts": {name: observation["events"]["by_event"].get(name, 0)
                         for name in sorted(observer.EVENTS)},
        "captured_events": observation["events"]["total"],
        "identityless_events": observation["events"]["identityless"],
        "captured_contacts": contact["observed_user_messages"],
        "classification_counts": {name: contact["label_counts"][name] for name in sorted(contact_metrics.LABELS)},
        "classification_complete": contact["classification_complete"],
        "known_correction_count": contact["known_correction_count"],
        "correction_total": contact["correction_total"],
        "work_contact_total": contact["work_contact_total"],
        "user_reported_resolution_state": state,
        "first_pass_resolution": contact["first_pass_resolution"],
        "tokens": None, "cost_usd": None, "human_minutes": contact["human_minutes"],
        "human_minutes_qualifier": "Reported active minutes for captured contacts only; unknown unless all captured contacts have reports.",
    }


def export_checkpoint(db, private_snapshot, output, sessions):
    """Keep the full backup private; export only explicitly selected session summaries."""
    db, private_snapshot, output = Path(db), Path(private_snapshot), Path(output)
    if not db.is_absolute() or not private_snapshot.is_absolute():
        raise ValueError("Database and private snapshot paths must be absolute")
    if any(path.exists() or path.is_symlink() for path in (private_snapshot, output)):
        raise ValueError("Checkpoint targets must be new")
    db, private_snapshot, output = db.resolve(), private_snapshot.resolve(), output.resolve()
    if len({db, private_snapshot, output}) != 3 or not db.is_file():
        raise ValueError("A source database and distinct new targets are required")
    repository = REPOSITORY.resolve()
    if private_snapshot.is_relative_to(repository) or not output.is_relative_to(repository):
        raise ValueError("Public output must be inside the repository; private snapshot must be outside")
    if not isinstance(sessions, (list, tuple)) or not sessions:
        raise ValueError("Select at least one namespaced session")
    for session in sessions:
        observer._text(session, True)
        namespace, _, raw_id = session.partition(":")
        if namespace not in {"codex", "claude"} or not raw_id.strip():
            raise ValueError("Select host-namespaced session IDs")
    if len(set(sessions)) != len(sessions):
        raise ValueError("Session selections must be unique")
    private_snapshot.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the destination exclusively before SQLite opens it. Never connect
    # to the live source in write mode, or initialize contact tables there.
    with private_snapshot.open("xb"):
        pass
    with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(private_snapshot)) as target:
            source.backup(target)
    contact_metrics.init_tables(private_snapshot)
    summaries = [_session_summary(private_snapshot, session) for session in sessions]
    manifest = {
        "schema_version": 1, "recorded_utc": observer._now(),
        "metric_scope": "partial", "coverage": "partial",
        "snapshot_sha256": _hash(private_snapshot.read_bytes()),
        "reporter_sha256": {
            "observer": _hash(Path(observer.__file__).read_bytes()),
            "contact_metrics": _hash(Path(contact_metrics.__file__).read_bytes()),
            "checkpoint": _hash(Path(__file__).read_bytes()),
        },
        "sessions": summaries, "performance_claim": None,
        "limitations": [
            "Selected captured records only; missing hooks and pre-enrollment activity remain unknown.",
            "Contact classifications and resolution are caller attestations, not independent acceptance.",
            "First-pass resolution concerns the captured classified original request, not measured agent superiority.",
            "No complete token, cost or human-effort measurement is established.",
            "Identifier hashes are pseudonymous references, not a guarantee of anonymity.",
        ],
    }
    encoded = json.dumps(manifest, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--private-snapshot", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--session", action="append", required=True)
    args = parser.parse_args(argv)
    try:
        manifest = export_checkpoint(args.db, args.private_snapshot, args.output, args.session)
        print(json.dumps({"status": "exported", "selected_sessions": len(manifest["sessions"]),
                          "snapshot_sha256": manifest["snapshot_sha256"]}))
        return 0
    except (ValueError, TypeError, OSError, sqlite3.Error):
        print("Checkpoint failed; check private destination, selection and new output targets.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
