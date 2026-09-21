"""External classifications of captured contacts; no worker instructions or model calls.

Counts concern received UserPromptSubmit records, in receipt order, not complete
conversation coverage. Labels and user-reported resolutions are append-only;
the latest label per event is current. Unknown/missing labels are not zero repairs.
Work contacts are initial requests, corrections, clarification responses, scope
changes and new requests; confirmations and approvals do not request more work.
Scope changes/new requests are separate work, never corrections to the original.
First-pass resolution means an explicitly resolved, unchanged original request
without additional work contacts through its linked resolution contact. It stays
unknown without complete captured classifications, an initial request, and that
cutoff. This is an observational user-report metric, not independent acceptance.
Optional active minutes are reported per contact, not inferred from elapsed time.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sqlite3
import sys

if __package__ in (None, ''):
    import observer
else:
    from . import observer


LABELS = {'initial_request', 'correction', 'clarification_response', 'approval',
          'scope_change', 'new_request', 'confirmation', 'unknown'}
WORK_LABELS = {'initial_request', 'correction', 'clarification_response',
               'scope_change', 'new_request'}
RESOLUTIONS = {'resolved', 'unresolved', 'reopened', 'abandoned'}
SCHEMA = """
CREATE TABLE IF NOT EXISTS contact_labels (
 id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id),
 event_id INTEGER NOT NULL REFERENCES events(id), revision INTEGER NOT NULL,
 label TEXT NOT NULL, actor TEXT NOT NULL, source TEXT NOT NULL,
 recorded_utc TEXT NOT NULL, human_minutes REAL, minutes_basis TEXT,
 UNIQUE(event_id, revision));
CREATE TABLE IF NOT EXISTS contact_resolutions (
 id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id),
 state TEXT NOT NULL, basis TEXT NOT NULL, actor TEXT NOT NULL, source TEXT NOT NULL,
 event_id INTEGER REFERENCES events(id), evidence TEXT, recorded_utc TEXT NOT NULL);
"""


def _session(conn, session_id):
    observer._text(session_id, True)
    if conn.execute('SELECT 1 FROM sessions WHERE session_id=?', (session_id,)).fetchone() is None:
        raise ValueError('Session is not enrolled')


def _contact(conn, session_id, event_id):
    if type(event_id) is not int or event_id < 1:
        raise ValueError('Contact requires a positive event ID')
    row = conn.execute('SELECT session_id,event_name FROM events WHERE id=?', (event_id,)).fetchone()
    if row is None or row['session_id'] != session_id or row['event_name'] != 'UserPromptSubmit':
        raise ValueError('Contact must reference this session\'s captured UserPromptSubmit event')


def _provenance(actor, source):
    if actor not in {'human', 'auditor'}:
        raise ValueError('Classification actor must be human or auditor')
    return observer._text(source, True)


def _finite_minutes(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def init_tables(path):
    """Add contact tables to an existing observer database; never enroll a session."""
    if not Path(path).is_file():
        raise ValueError('Observer database does not exist')
    with observer._db(path) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'sessions', 'events'}.issubset(names):
            raise ValueError('Expected an observer database')
        conn.executescript(SCHEMA)
    return {'status': 'initialized'}


def label_contact(path, session_id, event_id, label, *, actor, source,
                  human_minutes=None, minutes_basis=None):
    """Append a classification revision; no message content is required or stored."""
    if label not in LABELS:
        raise ValueError('Unsupported contact classification')
    source = _provenance(actor, source)
    if human_minutes is not None:
        if not _finite_minutes(human_minutes):
            raise ValueError('Active minutes must be finite and nonnegative')
        minutes_basis = observer._text(minutes_basis, True)
    elif minutes_basis is not None:
        raise ValueError('A minutes basis requires reported minutes')
    init_tables(path)
    with observer._db(path) as conn:
        conn.execute('BEGIN IMMEDIATE')
        _session(conn, session_id)
        _contact(conn, session_id, event_id)
        revision = conn.execute('SELECT COALESCE(MAX(revision),0)+1 FROM contact_labels WHERE event_id=?',
                                (event_id,)).fetchone()[0]
        cursor = conn.execute('INSERT INTO contact_labels (session_id,event_id,revision,label,actor,source,'
                              'recorded_utc,human_minutes,minutes_basis) VALUES (?,?,?,?,?,?,?,?,?)',
                              (session_id, event_id, revision, label, actor, source, observer._now(),
                               human_minutes, minutes_basis))
    return {'status': 'recorded', 'label_id': cursor.lastrowid, 'event_id': event_id, 'revision': revision}


def record_resolution(path, session_id, state, *, actor, source, event_id=None, evidence=None):
    """Append a caller-attested user report; auditors must name explicit user evidence."""
    if state not in RESOLUTIONS:
        raise ValueError('Unsupported user-reported resolution state')
    source = _provenance(actor, source)
    if evidence is not None:
        evidence = observer._text(evidence, True)
    if actor == 'auditor' and evidence is None:
        raise ValueError('Auditor resolution requires an explicit user-report evidence reference')
    if event_id is None and evidence is None:
        raise ValueError('Resolution requires a captured contact or an evidence reference')
    init_tables(path)
    with observer._db(path) as conn:
        _session(conn, session_id)
        if event_id is not None:
            _contact(conn, session_id, event_id)
        cursor = conn.execute('INSERT INTO contact_resolutions (session_id,state,basis,actor,source,'
                              'event_id,evidence,recorded_utc) VALUES (?,?,?,?,?,?,?,?)',
                              (session_id, state, 'user_reported', actor, source, event_id,
                               evidence, observer._now()))
    return {'status': 'recorded', 'resolution_id': cursor.lastrowid, 'basis': 'user_reported'}


def session_report(path, session_id):
    init_tables(path)
    with observer._db(path) as conn:
        _session(conn, session_id)
        contacts = [dict(row) for row in conn.execute('SELECT id,received_utc FROM events WHERE session_id=? '
                    'AND event_name=\'UserPromptSubmit\' ORDER BY id', (session_id,))]
        history = [dict(row) for row in conn.execute('SELECT * FROM contact_labels WHERE session_id=? ORDER BY id',
                                                    (session_id,))]
        resolutions = [dict(row) for row in conn.execute('SELECT * FROM contact_resolutions WHERE session_id=? '
                                                        'ORDER BY id', (session_id,))]
    current = {row['event_id']: row for row in history}
    labels = [current.get(contact['id'], {}).get('label', 'unknown') for contact in contacts]
    counts = {label: labels.count(label) for label in sorted(LABELS)}
    complete = bool(contacts) and counts['unknown'] == 0
    latest = resolutions[-1] if resolutions else None
    cutoff = latest['event_id'] if latest and latest['state'] == 'resolved' else None
    through = [contact for contact in contacts if cutoff is not None and contact['id'] <= cutoff]
    through_labels = [current.get(contact['id'], {}).get('label', 'unknown') for contact in through]
    anchored = bool(through_labels) and through_labels[0] == 'initial_request' and through_labels.count('initial_request') == 1
    unchanged = not any(label in {'scope_change', 'new_request'} for label in through_labels)
    first_pass = None
    if complete and anchored and unchanged:
        first_pass = sum(label in WORK_LABELS for label in through_labels) == 1 and not any(
            resolution['state'] == 'reopened' for resolution in resolutions)
    known_minutes = [row['human_minutes'] for row in current.values() if row['human_minutes'] is not None]
    minutes_complete = bool(contacts) and len(known_minutes) == len(contacts)
    reported_minutes = sum(known_minutes) if known_minutes else None
    if reported_minutes is not None and not _finite_minutes(reported_minutes):
        reported_minutes = None
    return {
        'session_id': session_id, 'collection_mode': 'observational',
        'metric_scope': 'captured_contact_records_only',
        'coverage': {'status': 'partial', 'scope': 'Received UserPromptSubmit records in receipt order only.',
                     'reason': 'Missing hooks, pre-enrollment messages and duplicate identity-less deliveries are unknown.'},
        'observed_user_messages': len(contacts), 'observed_followups_after_first_contact': max(0, len(contacts) - 1),
        'label_counts': counts, 'classification_complete': complete, 'unclassified_count': counts['unknown'],
        'known_correction_count': counts['correction'],
        'correction_total': counts['correction'] if complete else None,
        'known_work_contact_count': sum(counts[label] for label in WORK_LABELS),
        'work_contact_total': sum(counts[label] for label in WORK_LABELS) if complete else None,
        'known_separate_request_count': counts['scope_change'] + counts['new_request'],
        'contacts_to_resolution': len(through) if cutoff is not None else None,
        'work_contacts_to_resolution': sum(label in WORK_LABELS for label in through_labels)
                                       if cutoff is not None and complete else None,
        'first_pass_resolution': first_pass,
        'first_pass_scope': 'Captured, fully classified, unchanged original request with a linked user-reported resolution; '
                            'approvals/confirmations are not extra work. Otherwise unknown.',
        'resolution': latest, 'resolution_history': resolutions,
        'current_labels': list(current.values()), 'label_history': history,
        'known_reported_human_minutes': reported_minutes,
        'human_minutes': reported_minutes if minutes_complete else None,
        'human_minutes_status': 'overflow' if known_minutes and reported_minutes is None else
                                'reported_captured_contacts' if minutes_complete else 'incomplete_reports',
        'human_minutes_basis': 'Latest per-contact reported active minutes and explicit bases; never elapsed-time inference.',
        'limitations': ['Counts describe captured records, not exact whole-conversation totals.',
                       'Classification and user resolution are caller attestations, not automatic or independent acceptance.',
                       'Correction totals span the observed session; scope changes/new requests are separate work, not repairs.'],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    label = commands.add_parser('label')
    label.add_argument('session_id')
    label.add_argument('event_id', type=int)
    label.add_argument('label', choices=sorted(LABELS))
    label.add_argument('--human-minutes', type=float)
    label.add_argument('--minutes-basis')
    resolution = commands.add_parser('resolution')
    resolution.add_argument('session_id')
    resolution.add_argument('state', choices=sorted(RESOLUTIONS))
    resolution.add_argument('--event-id', type=int)
    resolution.add_argument('--evidence')
    for command in (label, resolution):
        command.add_argument('--actor', required=True, choices=('human', 'auditor'))
        command.add_argument('--source', required=True)
    report = commands.add_parser('report')
    report.add_argument('session_id')
    args = parser.parse_args(argv)
    try:
        if args.command == 'label':
            result = label_contact(args.db, args.session_id, args.event_id, args.label, actor=args.actor,
                                   source=args.source, human_minutes=args.human_minutes, minutes_basis=args.minutes_basis)
        elif args.command == 'resolution':
            result = record_resolution(args.db, args.session_id, args.state, actor=args.actor,
                                       source=args.source, event_id=args.event_id, evidence=args.evidence)
        else:
            result = session_report(args.db, args.session_id)
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except (ValueError, TypeError, sqlite3.Error, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
