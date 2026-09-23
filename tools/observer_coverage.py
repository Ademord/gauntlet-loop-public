"""Read-only enrollment and accounting coverage audit; never installs or enrolls."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sqlite3
import sys

METRICS = ('tokens', 'cost_usd', 'human_minutes')
LABELS = {'initial_request', 'correction', 'clarification_response', 'approval',
          'scope_change', 'new_request', 'confirmation', 'unknown'}
EVENTS = {'SessionStart', 'SessionEnd', 'PreToolUse', 'PostToolUse',
          'PostToolUseFailure', 'StopFailure', 'SubagentStart', 'SubagentStop',
          'Stop', 'UserPromptSubmit', 'Interrupt'}


def _identity(value):
    if not isinstance(value, str) or len(value) > 512 or any(ord(c) < 32 for c in value):
        raise ValueError('Invalid selection')
    host, separator, identity = value.partition(':')
    if host not in ('codex', 'claude') or not separator or not identity.strip():
        raise ValueError('Invalid selection')
    return value


def _selection(selection):
    if not isinstance(selection, dict) or not isinstance(selection.get('sessions'), list):
        raise ValueError('Invalid selection')
    if not 1 <= len(selection['sessions']) <= 100:
        raise ValueError('Invalid selection size')
    identities = []
    for row in selection['sessions']:
        if not isinstance(row, dict):
            raise ValueError('Invalid selection row')
        identities.append(_identity(row.get('session_id')))
    controller = selection.get('controller_session_id')
    if controller is not None:
        controller = _identity(controller)
    all_ids = identities + ([controller] if controller else [])
    if len(set(all_ids)) != len(all_ids):
        raise ValueError('Duplicate selection')
    return identities, controller


def _number(value):
    if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
        raise ValueError('Invalid measurement')
    return value


def _contacts(conn, tables, session):
    if not {'contact_labels', 'contact_resolutions'}.issubset(tables):
        return None
    prompts = {row[0] for row in conn.execute(
        "SELECT id FROM events WHERE session_id=? AND event_name='UserPromptSubmit'", (session,))}
    latest = {}
    for row in conn.execute('SELECT event_id,label FROM contact_labels WHERE session_id=? ORDER BY id', (session,)):
        if row[0] in prompts:
            if row[1] not in LABELS:
                raise ValueError('Invalid classification')
            latest[row[0]] = row[1]
    labels = Counter(latest.get(event, 'unknown') for event in prompts)
    resolutions = [row[0] for row in conn.execute('SELECT state FROM contact_resolutions WHERE session_id=? ORDER BY id', (session,))]
    if any(state not in {'resolved', 'unresolved', 'reopened', 'abandoned'} for state in resolutions):
        raise ValueError('Invalid resolution')
    return {'captured_prompts': len(prompts), 'latest_label_counts': dict(sorted(labels.items())),
            'unclassified_prompts': labels.get('unknown', 0),
            'human_corrections': None, 'human_origin': 'not_established',
            'resolution_records': len(resolutions), 'latest_resolution_state': resolutions[-1] if resolutions else None,
            'first_pass_resolution': None,
            'reason': 'Labels classify captured records. Classifier identity does not establish prompt authorship; resolution rows are attestations, not verified task success.'}


def _session(conn, tables, identity, alias):
    enrolled = conn.execute('SELECT 1 FROM sessions WHERE session_id=?', (identity,)).fetchone() is not None
    counts = Counter()
    if enrolled:
        for name, count in conn.execute('SELECT event_name,COUNT(*) FROM events WHERE session_id=? GROUP BY event_name', (identity,)):
            counts[name if name in EVENTS else 'other'] += count
    measurements = {row[0]: _number(row[1]) for row in conn.execute(
        'SELECT name,value FROM measurements WHERE session_id=?', (identity,)) if row[0] in METRICS} if enrolled else {}
    return {'alias': alias,
            'status': 'not_enrolled' if not enrolled else ('observed_partial' if counts else 'enrolled_no_events'),
            'event_counts': dict(sorted(counts.items())),
            'reported_measurements': {metric: {'value': measurements.get(metric),
                'reason': 'Reported value only; scope and attribution unverified.' if measurements.get(metric) is not None else 'No attributable measurement in the selected observer record.'} for metric in METRICS},
            'contacts': _contacts(conn, tables, identity) if enrolled else None,
            'whole_task_cost_usd': None, 'capture_complete': False,
            'limitation': 'No recorded activity does not mean no work. Enrollment and received hooks cannot recover earlier or missing activity.'}


def audit(database, selection):
    """Return aliases and aggregate metadata only; no raw identifiers or text."""
    identities, controller = _selection(selection)
    database = Path(database).resolve()
    if not database.is_file():
        raise ValueError('Database unavailable')
    conn = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    try:
        conn.execute('PRAGMA query_only=ON')
        conn.execute('BEGIN')
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'sessions', 'events', 'measurements', 'outcomes'}.issubset(tables):
            raise ValueError('Observer schema missing')
        hosts = Counter()
        for row in conn.execute('SELECT session_id FROM sessions'):
            host = row[0].partition(':')[0]
            hosts[host if host in ('codex', 'claude') else 'other'] += 1
        values = [_number(row[0]) for row in conn.execute('SELECT value FROM measurements')]
        def count(table):
            return conn.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] if table in tables else None
        result = {'schema_version': 1, 'kind': 'observer_coverage_audit',
                  'selection_count': len(identities),
                  'selected': [_session(conn, tables, sid, f'task-{i:02d}') for i, sid in enumerate(identities, 1)],
                  'database_summary': {'sessions': count('sessions'), 'events': count('events'),
                      'by_host': dict(sorted(hosts.items())),
                      'measurement_rows': {'known': sum(v is not None for v in values), 'unknown': sum(v is None for v in values)},
                      'contact_labels': count('contact_labels'), 'resolution_records': count('contact_resolutions'), 'outcomes': count('outcomes')},
                  'whole_task_accounting_complete': False, 'whole_task_cost_usd': None,
                  'scope': 'Selected identities checked against one read transaction. No automatic enrollment, retrospective reconstruction, descendant roll-up or causal performance inference.'}
        if controller:
            result['controller'] = _session(conn, tables, controller, 'controller')
        return result
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output and (args.output.exists() or args.output.resolve() in (args.db.resolve(), args.selection.resolve())):
            raise ValueError('Output must be a new separate file')
        selected = json.loads(args.selection.read_text(encoding='utf-8'))
        result = audit(args.db, selected)
        text = json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False) + '\n'
        if args.output:
            with args.output.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(text)
        print(text, end='')
        return 0
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error):
        print('Coverage audit failed; check input schema and choose a new separate output file.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
