"""Explicit host enrollment for the metadata observer; never installs hooks."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import observer

HOSTS = {"codex", "claude"}
MAX_TTL_SECONDS = 3600
PENDING_SCHEMA = """
CREATE TABLE IF NOT EXISTS pending_enrollments (
 id INTEGER PRIMARY KEY, host TEXT NOT NULL, cwd TEXT NOT NULL,
 task_id TEXT NOT NULL, config_json TEXT NOT NULL,
 created_utc TEXT NOT NULL, expires_unix REAL NOT NULL,
 consumed_utc TEXT, consumed_session_id TEXT);
"""


def _host(host):
    if host not in HOSTS:
        raise ValueError("Choose host codex or claude")
    return host


def _session(host, raw_id):
    return observer._text(f"{_host(host)}:{observer._text(raw_id, True)}", True)


def _cwd(value):
    value = observer._text(value, True)
    if not os.path.isabs(value):
        raise ValueError("Enrollment requires an absolute cwd")
    normalized = os.path.normcase(os.path.normpath(value))
    return normalized.casefold() if os.name == "nt" else normalized


def _config(host, config):
    observer.validate_config(config)
    if config.get("host") != _host(host):
        raise ValueError("Configuration host must match the selected host")
    return dict(config)


def init_db(path):
    observer.init_db(path)
    with observer._db(path) as conn:
        conn.executescript(PENDING_SCHEMA)
    return {"status": "initialized"}


def register(path, host, session_id, task_id, config):
    config = _config(host, config)
    session_id = _session(host, session_id)
    observer._text(task_id, True)
    init_db(path)
    return observer.register_session(path, session_id, task_id, config)


def arm(path, host, cwd, task_id, config, ttl_seconds=300):
    """Enroll the next new SessionStart at this exact host and normalized cwd."""
    host, cwd = _host(host), _cwd(cwd)
    task_id, config = observer._text(task_id, True), _config(host, config)
    if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
        raise ValueError("Enrollment TTL must be an integer from 1 to 3600 seconds")
    config["capture_scope"] = "next-session-from-enrollment"
    init_db(path)
    with observer._db(path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        now = time.time()
        if conn.execute("SELECT 1 FROM pending_enrollments WHERE host=? AND cwd=? "
                        "AND consumed_session_id IS NULL AND expires_unix>?",
                        (host, cwd, now)).fetchone():
            raise ValueError("An unconsumed enrollment already exists for this host and cwd")
        cursor = conn.execute("INSERT INTO pending_enrollments "
                              "(host,cwd,task_id,config_json,created_utc,expires_unix) "
                              "VALUES (?,?,?,?,?,?)",
                              (host, cwd, task_id, observer._json(config), observer._now(),
                               now + ttl_seconds))
    return {"status": "armed", "enrollment_id": cursor.lastrowid, "host": host,
            "cwd": cwd, "expires_unix": now + ttl_seconds}


def _enroll_start(path, host, payload):
    """Consume and register atomically; repeated starts cannot consume another arm."""
    with observer._db(path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("SELECT 1 FROM sessions WHERE session_id=?",
                        (payload["session_id"],)).fetchone():
            return
        if not payload.get("cwd"):
            return
        cwd = _cwd(payload["cwd"])
        if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                            "AND name='pending_enrollments'").fetchone():
            return
        enrollment = conn.execute("SELECT * FROM pending_enrollments WHERE host=? AND cwd=? "
                                  "AND consumed_session_id IS NULL AND expires_unix>? "
                                  "ORDER BY id LIMIT 1", (host, cwd, time.time())).fetchone()
        if enrollment is None:
            return
        # Validate the metadata before consuming an enrollment. Payload contents
        # remain outside storage; the core retains only allowed metadata/hash.
        for key in observer.FIELDS:
            if key in payload:
                observer._text(payload[key])
        config = _config(host, json.loads(enrollment["config_json"]))
        observer._register(conn, payload["session_id"], enrollment["task_id"], config)
        conn.execute("UPDATE pending_enrollments SET consumed_utc=?,consumed_session_id=? "
                     "WHERE id=?", (observer._now(), payload["session_id"], enrollment["id"]))


def ingest_hook(path, host, payload):
    host = _host(host)
    if not isinstance(payload, dict):
        raise ValueError("Hook payload must be an object")
    if payload.get("hook_event_name") not in observer.EVENTS:
        return {"status": "ignored", "reason": "unsupported_event"}
    if not payload.get("session_id") or not Path(path).is_file():
        return {"status": "ignored", "reason": "session_not_enrolled"}
    payload = dict(payload, session_id=_session(host, payload["session_id"]))
    if len(observer._json(payload).encode("utf-8")) > observer.MAX_PAYLOAD:
        raise ValueError("Hook payload exceeds limit")
    if payload["hook_event_name"] == "SessionStart":
        _enroll_start(path, host, payload)
    return observer.ingest_hook(path, payload)


def report(path, host, session_id):
    result = observer.session_report(path, _session(host, session_id))
    _config(host, result["config"])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--host", help="codex or claude; required except for init")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    registration = commands.add_parser("register")
    registration.add_argument("session_id")
    registration.add_argument("task_id")
    registration.add_argument("--config", required=True)
    enrollment = commands.add_parser("arm")
    enrollment.add_argument("--cwd", required=True)
    enrollment.add_argument("--task", required=True)
    enrollment.add_argument("--config", required=True)
    enrollment.add_argument("--ttl-seconds", type=int, default=300)
    commands.add_parser("hook")
    reporting = commands.add_parser("report")
    reporting.add_argument("session_id")
    args = parser.parse_args(argv)
    if args.command == "hook":
        try:
            raw = sys.stdin.buffer.read(observer.MAX_PAYLOAD + 1)
            if len(raw) > observer.MAX_PAYLOAD or not Path(args.db).is_file():
                raise ValueError("Observer unavailable or payload too large")
            ingest_hook(args.db, args.host, json.loads(raw))
        except Exception:
            observer._diagnostic(args.db)
        return 0
    try:
        if args.command == "init":
            result = init_db(args.db)
        elif args.command == "report":
            result = report(args.db, args.host, args.session_id)
        else:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
            if args.command == "arm":
                result = arm(args.db, args.host, args.cwd, args.task, config, args.ttl_seconds)
            else:
                result = register(args.db, args.host, args.session_id, args.task_id, config)
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except Exception:
        print("Observer host command failed; check host, enrollment and metadata.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
