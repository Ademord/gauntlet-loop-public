"""Prepare/review/apply explicit observer hooks; never approve native host trust."""
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
TOOL_EVENTS = {'PreToolUse', 'PostToolUse', 'PostToolUseFailure'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _definition(runtime, database, python, host, auto_enroll=False):
    argv = [Path(python).resolve().as_posix(), '-B',
            (Path(runtime) / 'observer_host.py').as_posix(), '--db',
            Path(database).as_posix(), '--host', host, 'hook']
    if auto_enroll:
        argv.append('--auto-enroll')
    command = argv[0] if host == 'claude' else subprocess.list2cmdline(argv)
    args = argv[1:] if host == 'claude' else None
    hook = {'type': 'command', 'command': command, 'timeout': 3}
    if args is not None:
        hook['args'] = args
    return hook


def _entries(settings):
    hooks = settings.get('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('Existing hooks must be an object')
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            raise ValueError('Existing event hooks must be a list')
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get('hooks'), list):
                raise ValueError('Invalid hook wrapper')
            for index, hook in enumerate(entry['hooks']):
                if not isinstance(hook, dict):
                    raise ValueError('Invalid hook handler')
                yield event, entry, index, hook


def _same_command(hook, expected):
    return hook.get('command') == expected['command'] and hook.get('args') == expected.get('args')


def _references(hook, path):
    # Recognition only triggers refusal; it never authorizes deleting a handler.
    normalized = str(path).replace('\\', '/').casefold()
    args = hook.get('args')
    values = [hook.get('command'), *(args if isinstance(args, list) else [args])]
    return any(isinstance(value, str) and normalized in value.replace('\\', '/').casefold()
               for value in values)


def _owned_slots(settings, host, expected, runtime):
    slots = {}
    for event, entry, index, hook in _entries(settings):
        if not _same_command(hook, expected) and not _references(hook, Path(runtime) / 'observer_host.py'):
            continue
        wrapper = {'matcher': '.*'} if event in TOOL_EVENTS else {}
        if (event not in EVENTS[host] or hook != expected or
                {key: value for key, value in entry.items() if key != 'hooks'} != wrapper or event in slots):
            raise ValueError('Previous observer definitions are modified or ambiguous')
        slots[event] = (entry, index)
    if set(slots) != set(EVENTS[host]):
        raise ValueError('Previous observer definitions are missing')
    return slots


def _previous(previous_plan, database):
    if isinstance(previous_plan, (str, os.PathLike)):
        previous_plan = json.loads(Path(previous_plan).read_text(encoding='utf-8-sig'))
    if not isinstance(previous_plan, dict) or previous_plan.get('schema_version') != 1:
        raise ValueError('Expected an explicit previous installation plan')
    for field in ('runtime', 'database', 'python'):
        if not isinstance(previous_plan.get(field), str) or not Path(previous_plan[field]).is_absolute():
            raise ValueError('Previous installation paths must be absolute')
    if Path(previous_plan['database']).resolve() != database:
        raise ValueError('Previous installation belongs to another database')
    if type(previous_plan.get('auto_enroll', False)) is not bool:
        raise ValueError('Invalid previous enrollment mode')
    runtime = Path(previous_plan['runtime'])
    identity = digest(b''.join(name.encode() + (runtime / name).read_bytes() for name in MODULES))
    if identity != previous_plan.get('runtime_sha256') or runtime.name != identity:
        raise ValueError('Previous frozen runtime identity mismatch')
    if not isinstance(previous_plan.get('changes'), list):
        raise ValueError('Previous installation changes are missing')
    changes = {}
    for change in previous_plan['changes']:
        if not isinstance(change, dict) or change.get('host') not in EVENTS or change['host'] in changes:
            raise ValueError('Ambiguous previous host changes')
        host = change['host']
        expected = _definition(runtime, Path(previous_plan['database']), previous_plan['python'],
                               host, previous_plan.get('auto_enroll', False))
        if (not isinstance(change.get('target'), str) or not Path(change['target']).is_absolute() or
                change.get('command') != expected['command'] or not isinstance(change.get('after_utf8'), str) or
                digest(change['after_utf8'].encode()) != change.get('after_sha256')):
            raise ValueError('Previous installation definition identity mismatch')
        old_settings = json.loads(change['after_utf8'])
        if not isinstance(old_settings, dict):
            raise ValueError('Invalid previous settings')
        _owned_slots(old_settings, host, expected, runtime)
        changes[host] = (change, expected)
    return previous_plan, changes


def _replace_hooks(settings, host, expected, replacement, runtime, new_runtime):
    merged = json.loads(json.dumps(settings))
    slots = _owned_slots(merged, host, expected, runtime)
    if replacement != expected and any(hook != expected and (
            _same_command(hook, replacement) or _references(hook, Path(new_runtime) / 'observer_host.py'))
            for _, _, _, hook in _entries(merged)):
        raise ValueError('New observer definition already exists beside previous definition')
    for entry, index in slots.values():
        entry['hooks'][index] = dict(replacement)
    return merged


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
        if event in TOOL_EVENTS:
            entry['matcher'] = '.*'
        entries.append(entry)
    return merged


def prepare(private_root, database, targets, python=sys.executable, *, auto_enroll=False, previous_plan=None):
    private_root, database = Path(private_root).resolve(), Path(database).resolve()
    if type(auto_enroll) is not bool:
        raise ValueError('auto_enroll must be boolean')
    previous, old_changes = _previous(previous_plan, database) if previous_plan is not None else (None, {})
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
            'auto_enroll': auto_enroll,
            'created_utc': datetime.now(timezone.utc).isoformat(), 'changes': []}
    for host, target in targets.items():
        if host not in EVENTS:
            raise ValueError('Unsupported host')
        target = Path(target).resolve()
        before = target.read_bytes() if target.exists() else None
        settings = json.loads(before.decode('utf-8-sig')) if before is not None else {}
        if not isinstance(settings, dict):
            raise ValueError('Settings must be an object')
        definition = _definition(runtime, database, python, host, auto_enroll)
        if previous is not None:
            if host not in old_changes or Path(old_changes[host][0]['target']).resolve() != target:
                raise ValueError('Previous installation target does not match')
            merged = _replace_hooks(settings, host, old_changes[host][1], definition, previous['runtime'], runtime)
        else:
            if auto_enroll:
                found_current = False
                for _, _, _, hook in _entries(settings):
                    if _references(hook, 'observer_host.py'):
                        if not _same_command(hook, definition):
                            raise ValueError('Existing observer requires an explicit previous installation plan')
                        found_current = True
                if found_current:
                    _owned_slots(settings, host, definition, runtime)
            merged = merge_hooks(settings, host, definition['command'], definition.get('args'))
        after = (json.dumps(merged, indent=2) + '\n').encode()
        plan['changes'].append({'host': host, 'target': str(target),
                               'before_sha256': digest(before) if before is not None else None,
                               'after_sha256': digest(after), 'after_utf8': after.decode(),
                               'command': definition['command']})
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
    prep.add_argument('--auto-enroll', action='store_true', help='Opt in to metadata capture for arriving local sessions')
    prep.add_argument('--previous-plan', help='Exact prior installation plan for an ownership-checked upgrade')
    execute = sub.add_parser('apply')
    execute.add_argument('--plan', required=True)
    execute.add_argument('--backups', required=True)
    args = parser.parse_args()
    if args.action == 'prepare':
        plan = prepare(args.private_root, args.db,
                       {'claude': args.claude_settings, 'codex': args.codex_hooks},
                       auto_enroll=args.auto_enroll, previous_plan=args.previous_plan)
        Path(args.plan).write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status': 'prepared', 'runtime_sha256': plan['runtime_sha256'],
                          'hosts': [c['host'] for c in plan['changes']]}))
    else:
        print(json.dumps(apply(json.loads(Path(args.plan).read_text(encoding='utf-8')), args.backups)))


if __name__ == '__main__':
    main()
