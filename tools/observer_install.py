"""Prepare/review/apply an additive local hook installation; never approve host trust."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

EVENTS = {
    'codex': ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse',
              'SubagentStart', 'SubagentStop', 'Stop', 'Interrupt', 'SessionEnd'],
    'claude': ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse',
               'PostToolUseFailure', 'SubagentStart', 'SubagentStop', 'Stop',
               'StopFailure', 'SessionEnd'],
}
MODULES = ('observer.py', 'observer_host.py', 'contact_metrics.py')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def merge_hooks(settings, host, command, args=None):
    merged = json.loads(json.dumps(settings))
    hooks = merged.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('Existing hooks must be an object')
    for event in EVENTS[host]:
        entries = hooks.setdefault(event, [])
        if not isinstance(entries, list):
            raise ValueError('Existing event hooks must be a list')
        if any(h.get('command') == command and h.get('args') == args for entry in entries
               for h in entry.get('hooks', [])):
            continue
        entry = {'hooks': [{'type': 'command', 'command': command, 'timeout': 3}]}
        if args is not None:
            entry['hooks'][0]['args'] = args
        if event in {'PreToolUse', 'PostToolUse', 'PostToolUseFailure'}:
            entry['matcher'] = '.*'
        entries.append(entry)
    return merged


def prepare(private_root, database, targets, python=sys.executable):
    private_root, database = Path(private_root).resolve(), Path(database).resolve()
    private_root.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent
    contents = {name: (source / name).read_bytes() for name in MODULES}
    version = digest(b''.join(name.encode() + contents[name] for name in MODULES))
    runtime = private_root / 'runtime' / version
    runtime.mkdir(parents=True, exist_ok=True)
    for name, data in contents.items():
        target = runtime / name
        if target.exists() and target.read_bytes() != data:
            raise ValueError('Frozen runtime was modified')
        if not target.exists():
            target.write_bytes(data)
    plan = {'schema_version': 1, 'runtime_sha256': version, 'runtime': str(runtime),
            'database': str(database), 'python': str(Path(python).resolve()),
            'created_utc': datetime.now(timezone.utc).isoformat(), 'changes': []}
    for host, target in targets.items():
        if host not in EVENTS:
            raise ValueError('Unsupported host')
        target = Path(target).resolve()
        before = target.read_bytes() if target.exists() else None
        settings = json.loads(before.decode('utf-8-sig')) if before is not None else {}
        if not isinstance(settings, dict):
            raise ValueError('Settings must be an object')
        # Windows command-line quoting. Native host execution must be separately tested.
        argv = [Path(python).resolve().as_posix(), '-B',
                    (runtime / 'observer_host.py').as_posix(), '--db', database.as_posix(),
                    '--host', host, 'hook']
        command = argv[0] if host == 'claude' else subprocess.list2cmdline(argv)
        args = argv[1:] if host == 'claude' else None
        after = (json.dumps(merge_hooks(settings, host, command, args), indent=2) + '\n').encode()
        plan['changes'].append({'host': host, 'target': str(target),
                               'before_sha256': digest(before) if before is not None else None,
                               'after_sha256': digest(after), 'after_utf8': after.decode(),
                               'command': command})
    return plan


def apply(plan, backup_root):
    """All preconditions checked first. Back up exact bytes; never overwrite concurrent edits."""
    backup_root = Path(backup_root).resolve()
    runtime = Path(plan['runtime'])
    runtime_hash = digest(b''.join(name.encode() + (runtime / name).read_bytes() for name in MODULES))
    if runtime_hash != plan['runtime_sha256']:
        raise ValueError('Frozen runtime identity changed since preparation')
    for change in plan['changes']:
        target = Path(change['target'])
        before = target.read_bytes() if target.exists() else None
        if (digest(before) if before is not None else None) != change['before_sha256']:
            raise ValueError('Settings changed since preparation; prepare again')
        if digest(change['after_utf8'].encode()) != change['after_sha256']:
            raise ValueError('Prepared content identity mismatch')
        backup = backup_root / (change['host'] + '-' + (change['before_sha256'] or 'absent') + '.json')
        if change['before_sha256'] is not None and backup.exists() and digest(backup.read_bytes()) != change['before_sha256']:
            raise ValueError('Existing backup identity mismatch')
    backup_root.mkdir(parents=True, exist_ok=True)
    results = []
    for change in plan['changes']:
        target = Path(change['target'])
        if change['before_sha256'] == change['after_sha256']:
            results.append({'host': change['host'], 'status': 'unchanged'})
            continue
        backup = backup_root / (change['host'] + '-' + (change['before_sha256'] or 'absent') + '.json')
        if target.exists():
            if backup.exists() and digest(backup.read_bytes()) != change['before_sha256']:
                raise ValueError('Existing backup identity mismatch')
            if not backup.exists():
                shutil.copyfile(target, backup)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.observer-prepared')
        with temporary.open('xb') as stream:
            stream.write(change['after_utf8'].encode())
        # Recheck immediately before replace, after preparation and backup.
        before = target.read_bytes() if target.exists() else None
        if (digest(before) if before is not None else None) != change['before_sha256']:
            temporary.unlink()
            raise ValueError('Concurrent settings edit; original left unchanged')
        os.replace(temporary, target)
        results.append({'host': change['host'], 'status': 'installed',
                        'before_sha256': change['before_sha256'],
                        'after_sha256': digest(target.read_bytes())})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--private-root', required=True)
    prep.add_argument('--db', required=True)
    prep.add_argument('--claude-settings', required=True)
    prep.add_argument('--codex-hooks', required=True)
    prep.add_argument('--plan', required=True)
    execute = sub.add_parser('apply')
    execute.add_argument('--plan', required=True)
    execute.add_argument('--backups', required=True)
    args = parser.parse_args()
    if args.action == 'prepare':
        plan = prepare(args.private_root, args.db,
                       {'claude': args.claude_settings, 'codex': args.codex_hooks})
        Path(args.plan).write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status': 'prepared', 'runtime_sha256': plan['runtime_sha256'],
                          'hosts': [c['host'] for c in plan['changes']]}))
    else:
        print(json.dumps(apply(json.loads(Path(args.plan).read_text(encoding='utf-8')), args.backups)))


if __name__ == '__main__':
    main()
