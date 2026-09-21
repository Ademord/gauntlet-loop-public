"""Opt-in, metadata-only SQLite observer. Never installs hooks or dispatches models."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

MAX_PAYLOAD = 1024 * 1024
MAX_METADATA = 512
MAX_DIAGNOSTICS = 65536
EVENTS = {'SessionStart', 'SessionEnd', 'PreToolUse', 'PostToolUse',
          'SubagentStart', 'SubagentStop', 'Stop', 'UserPromptSubmit', 'Interrupt'}
TOOL_EVENTS = {'PreToolUse', 'PostToolUse'}
FIELDS = ('turn_id', 'model', 'permission_mode', 'tool_name', 'tool_use_id',
          'agent_id', 'agent_type', 'source', 'reason')
CONFIG_FIELDS = {'host', 'client_version', 'model', 'model_id', 'effort', 'tools',
                 'permissions', 'permission_mode', 'memory', 'workflow', 'session_mode',
                 'request_sha256', 'source_snapshot_sha256', 'capture_scope'}
REASONS = {
    'tokens': 'Hook metadata does not establish complete token usage.',
    'cost_usd': 'Hook metadata does not establish metered or billed cost.',
    'human_minutes': 'Hook metadata does not measure human work time.',
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
 session_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, enrolled_utc TEXT NOT NULL,
 collection_mode TEXT NOT NULL, config_json TEXT NOT NULL, collector_sha256 TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id),
 event_name TEXT NOT NULL, received_utc TEXT NOT NULL, event_identity TEXT UNIQUE,
 dedupe_status TEXT NOT NULL, metadata_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS measurements (
 session_id TEXT NOT NULL REFERENCES sessions(session_id), name TEXT NOT NULL,
 value REAL, reason TEXT NOT NULL, PRIMARY KEY(session_id, name));
CREATE TABLE IF NOT EXISTS outcomes (
 id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id),
 recorded_utc TEXT NOT NULL, artifact_hash TEXT NOT NULL, check_hash TEXT NOT NULL,
 evaluator TEXT NOT NULL, evidence TEXT NOT NULL, outcome TEXT NOT NULL);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False)


def _text(value, required=False):
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError('Expected metadata string')
    if len(value) > MAX_METADATA or any(ord(c) < 32 for c in value):
        raise ValueError('Invalid metadata size or control character')
    return value


@contextmanager
def _db(path):
    conn = sqlite3.connect(str(path), timeout=1.0)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=1000')
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _db(path) as conn:
        conn.executescript(SCHEMA)
    return {'status': 'initialized'}


def register_session(path, session_id, task_id, config: dict):
    session_id, task_id = _text(session_id, True), _text(task_id, True)
    if not isinstance(config, dict) or set(config) - CONFIG_FIELDS:
        raise ValueError('Unsupported configuration metadata')
    _json(config)  # Reject nonfinite or non-JSON data, including otherwise unused fields.
    for key in ('request_sha256', 'source_snapshot_sha256'):
        value = config.get(key)
        if value is not None and (not isinstance(value, str) or
                                  not re.fullmatch(r'[0-9a-fA-F]{64}', value)):
            raise ValueError('Task packet identities require SHA-256 hashes')
    for value in config.values():
        if isinstance(value, list):
            if len(value) > 64:
                raise ValueError('Too many configuration values')
            for item in value:
                _text(item, True)
        elif value is not None and not isinstance(value, bool):
            _text(value, True)
    init_db(path)
    try:
        with _db(path) as conn:
            conn.execute('INSERT INTO sessions VALUES (?,?,?,?,?,?)',
                         (session_id, task_id, _now(), 'observational', _json(config),
                          hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
            conn.executemany('INSERT INTO measurements VALUES (?,?,NULL,?)',
                             [(session_id, name, reason) for name, reason in REASONS.items()])
    except sqlite3.IntegrityError as exc:
        raise ValueError('Session already enrolled; existing enrollment is unchanged') from exc
    return {'status': 'registered', 'session_id': session_id, 'collection_mode': 'observational'}


def ingest_hook(path, payload: dict):
    received_utc = _now()
    if not isinstance(payload, dict):
        raise ValueError('Hook payload must be an object')
    session_id = _text(payload.get('session_id'))
    if not session_id or not Path(path).is_file():
        return {'status': 'ignored', 'reason': 'session_not_enrolled'}
    with _db(path) as conn:
        enrollment = conn.execute('SELECT collector_sha256 FROM sessions WHERE session_id=?',
                                  (session_id,)).fetchone()
        if enrollment is None:
            return {'status': 'ignored', 'reason': 'session_not_enrolled'}
        if enrollment['collector_sha256'] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            raise ValueError('Collector identity changed since enrollment')
        event = _text(payload.get('hook_event_name'))
        if event not in EVENTS:
            return {'status': 'ignored', 'reason': 'unsupported_event'}
        raw = _json(payload).encode('utf-8')
        if len(raw) > MAX_PAYLOAD:
            raise ValueError('Hook payload exceeds limit')
        metadata = {key: _text(payload[key]) for key in FIELDS if key in payload}
        identity = None
        if event in TOOL_EVENTS and metadata.get('tool_use_id'):
            identity = _json([session_id, event, metadata['tool_use_id'], metadata.get('turn_id')])
        status = 'stable_tool_identity' if identity else 'unknown'
        try:
            cursor = conn.execute('INSERT INTO events (session_id,event_name,received_utc,'
                                  'event_identity,dedupe_status,metadata_json,payload_sha256) '
                                  'VALUES (?,?,?,?,?,?,?)',
                                  (session_id, event, received_utc, identity, status,
                                   _json(metadata), hashlib.sha256(raw).hexdigest()))
        except sqlite3.IntegrityError:
            if identity and conn.execute('SELECT 1 FROM events WHERE event_identity=?',
                                         (identity,)).fetchone():
                return {'status': 'duplicate', 'dedupe_status': status}
            raise
    return {'status': 'recorded', 'event_id': cursor.lastrowid, 'dedupe_status': status}


def record_outcome(path, session_id, *, artifact_hash, check_hash, evaluator, evidence, outcome):
    """Record an explicitly supplied independent assessment; never infer it from hooks."""
    session_id = _text(session_id, True)
    for value in (artifact_hash, check_hash):
        if not isinstance(value, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', value):
            raise ValueError('Outcome identities require SHA-256 hashes')
    evaluator, evidence = _text(evaluator, True), _text(evidence, True)
    if outcome not in {'passed', 'failed', 'blocked', 'not_assessed'}:
        raise ValueError('Unsupported assessment outcome')
    if not Path(path).is_file():
        raise ValueError('Session is not enrolled')
    with _db(path) as conn:
        if not conn.execute('SELECT 1 FROM sessions WHERE session_id=?', (session_id,)).fetchone():
            raise ValueError('Session is not enrolled')
        cursor = conn.execute('INSERT INTO outcomes (session_id,recorded_utc,artifact_hash,'
                              'check_hash,evaluator,evidence,outcome) VALUES (?,?,?,?,?,?,?)',
                              (session_id, _now(), artifact_hash.lower(), check_hash.lower(),
                               evaluator, evidence, outcome))
    return {'status': 'recorded', 'outcome_id': cursor.lastrowid}


def session_report(path, session_id):
    if not Path(path).is_file():
        raise ValueError('Session is not enrolled')
    with _db(path) as conn:
        row = conn.execute('SELECT * FROM sessions WHERE session_id=?', (session_id,)).fetchone()
        if row is None:
            raise ValueError('Session is not enrolled')
        counts = dict(conn.execute('SELECT event_name,COUNT(*) FROM events WHERE session_id=? '
                                   'GROUP BY event_name', (session_id,)).fetchall())
        unknown = conn.execute('SELECT COUNT(*) FROM events WHERE session_id=? '
                               'AND event_identity IS NULL', (session_id,)).fetchone()[0]
        outcomes = [dict(r) for r in conn.execute('SELECT * FROM outcomes WHERE session_id=? '
                                                'ORDER BY id', (session_id,))]
    diagnostics = Path(path).parent / 'collector-errors.jsonl'
    return {
        'session_id': session_id, 'task_id': row['task_id'],
        'collection_mode': row['collection_mode'], 'config': json.loads(row['config_json']),
        'collector_sha256': row['collector_sha256'], 'enrolled_utc': row['enrolled_utc'],
        'collector_matches_current': row['collector_sha256'] ==
                                    hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'events': {'total': sum(counts.values()), 'by_event': counts,
                   'tool_starts': counts.get('PreToolUse', 0),
                   'tool_ends': counts.get('PostToolUse', 0), 'identityless': unknown},
        'deduplication': {'status': 'partial' if unknown else 'stable_tool_identities_only',
                          'identityless_events': unknown},
        'coverage': {'status': 'incomplete', 'reason': 'Only received hooks for an enrolled '
                     'session are counted. Missing arrivals and pre-enrollment activity are unknown. '
                     'Receipt timestamps are not execution start/end times; tool events are not reviews.'},
        'tokens': None, 'cost_usd': None, 'human_minutes': None,
        'measurement_reasons': dict(REASONS), 'outcomes': outcomes,
        'outcome_limit': 'Supplied evaluator assessments only; independence is asserted by the '
                         'caller, not verified by the collector. Stop is never acceptance.',
        'diagnostics': {'present': diagnostics.is_file() and diagnostics.stat().st_size > 0,
                        'impact': 'Collector diagnostics are shared by this database directory '
                                  'and may indicate lost events; attribution is unknown.'},
    }


def _diagnostic(path):
    """Best-effort bounded diagnostics with no payload, exception text, or session identifiers."""
    try:
        target = Path(path).parent / 'collector-errors.jsonl'
        target.parent.mkdir(parents=True, exist_ok=True)
        line = (_json({'received_utc': _now(), 'error': 'collector_error'}) + '\n').encode()
        with target.open('a+b') as stream:
            stream.seek(0, 2)
            if stream.tell() + len(line) > MAX_DIAGNOSTICS:
                stream.seek(0)
                stream.truncate()
            stream.write(line)
    except Exception:
        pass  # Diagnostics must never interrupt the observed task.


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    register = commands.add_parser('register')
    register.add_argument('session_id')
    register.add_argument('task_id')
    register.add_argument('--config', required=True)
    commands.add_parser('hook')
    report = commands.add_parser('report')
    report.add_argument('session_id')
    args = parser.parse_args(argv)
    if args.command == 'hook':
        try:
            raw = sys.stdin.buffer.read(MAX_PAYLOAD + 1)
            if len(raw) > MAX_PAYLOAD:
                raise ValueError('Payload too large')
            if not Path(args.db).is_file():
                raise ValueError('Observer database is unavailable')
            ingest_hook(args.db, json.loads(raw))
        except Exception:
            _diagnostic(args.db)
        return 0
    try:
        if args.command == 'init':
            result = init_db(args.db)
        elif args.command == 'register':
            result = register_session(args.db, args.session_id, args.task_id,
                                      json.loads(Path(args.config).read_text(encoding='utf-8')))
        else:
            result = session_report(args.db, args.session_id)
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except Exception:
        print('Observer command failed; check database, enrollment and metadata.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
