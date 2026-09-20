"""Controlled review-stage calibration. Preparation/grading is free; --execute calls Claude.

Each task has one build, a stop baseline, a context-preserving self-check fork,
and a fresh review followed by a separate correction fork. Hidden grades are
never supplied to workers. Raw session counters are cumulative on resume;
incremental stage usage subtracts the frozen parent result.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

from telemetry import parse_stream

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / 'research/program/calibration/tasks'
PROTOCOL = ROOT / 'research/program/calibration/PROTOCOL.md'
CAPS = {'build': .55, 'self_check': .85, 'reviewer': .45, 'repair': .40}
MODEL_KEYS = ('inputTokens', 'outputTokens', 'cacheReadInputTokens', 'cacheCreationInputTokens')
COMMON = ('Work only in this workspace. Do not delegate, use network, inspect parent directories, '
          'or read external project/session files. Modify only the allowed source paths. '
          'Use the visible tests and add local tests if useful, but do not weaken existing tests. '
          'Requirements are authoritative. Finish with a concise explanation of the result.')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tree_hashes(folder):
    return {p.relative_to(folder).as_posix(): digest(p.read_bytes())
            for p in sorted(folder.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and p.suffix != '.pyc' and '.git' not in p.parts}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def append(path, value):
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(value, sort_keys=True) + '\n')


def task_context(spec):
    requirements = '\n'.join('- ' + r for r in spec['requirements'])
    return (spec['description'] + '\nRequirements:\n' + requirements
            + '\nAllowed source paths: ' + ', '.join(spec['allowed_paths'])
            + '\nRun visible tests with: python -m unittest discover -s tests -v\n')


def task_prompt(spec):
    return task_context(spec) + COMMON


def review_prompt(spec, visible_output):
    return ('You are an independent reviewer. Inspect the current implementation read-only against the public task below. '
            'You may run tests and in-memory probes; do not edit files or produce an implementation. '
            'Do not delegate, access network, inspect parent directories, or read external project/session files. '
            'Return concrete requirement violations with reproducible examples, or state none found. '
            'Do not invent a required change. Keep the review concise.\nThe original builder task:\n'
            + task_context(spec) + '\nVisible test output supplied by the harness:\n' + visible_output)


def safe_rel(value):
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Unsafe relative path in task')
    return p


def grade(task, candidate):
    """Use author-owned tests and candidate source in a distinct evaluator tree."""
    spec = json.loads((task / 'task.json').read_text(encoding='utf-8'))
    outcomes = {}
    for kind, directory in [('visible', 'tests'), ('hidden', 'heldout')]:
        # Each suite starts from an independent copy. An import in the visible
        # suite must not rewrite what the hidden suite will execute later.
        with tempfile.TemporaryDirectory(prefix='gauntlet-grade-') as td:
            sandbox = Path(td)
            shutil.copytree(task / 'base', sandbox, dirs_exist_ok=True)
            for rel in spec['allowed_paths']:
                rel = safe_rel(rel)
                src = candidate / rel
                if not src.is_file():
                    return {'visible_passed': False, 'hidden_passed': False, 'missing_source': str(rel)}
                (sandbox / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, sandbox / rel)
            if kind == 'hidden':
                shutil.copytree(task / 'heldout', sandbox / 'heldout')
            before = tree_hashes(sandbox)
            p = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', directory, '-v'],
                               cwd=sandbox, capture_output=True, text=True, timeout=30)
            changed = changed_paths(before, tree_hashes(sandbox))
            outcomes[kind + '_passed'] = p.returncode == 0 and not changed
            outcomes[kind + '_integrity_changes'] = changed
            outcomes[kind + '_output'] = (p.stdout + p.stderr).replace(str(sandbox), '<evaluation>').replace(sandbox.as_posix(), '<evaluation>')
    return outcomes


def validate_fixture(task):
    base, oracle = grade(task, task / 'base'), grade(task, task / 'oracle')
    valid = base['visible_passed'] and not base['hidden_passed'] and oracle['visible_passed'] and oracle['hidden_passed']
    return {'task_id': task.name, 'valid': valid, 'base': base, 'oracle': oracle}


def incremental_usage(result, parent=None):
    """Subtract inherited session counters; refuse unknown/malformed/negative totals."""
    def validate_record(record):
        models = record.get('modelUsage')
        if not isinstance(models, dict) or not models:
            raise ValueError('Missing complete modelUsage; cannot account for stage')
        cost = record.get('total_cost_usd')
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
            raise ValueError('Missing or invalid session cost')
        for model in models.values():
            for key in (*MODEL_KEYS, 'costUSD'):
                value = model.get(key)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    raise ValueError('Missing or invalid model usage category')
                if key in MODEL_KEYS and int(value) != value:
                    raise ValueError('Token counts must be integers')
        if abs(sum(m['costUSD'] for m in models.values()) - cost) > 1e-6:
            raise ValueError('Session model costs do not reconcile')
        return models
    models = validate_record(result)
    parents = validate_record(parent) if parent is not None else {}
    delta_models = {}
    for name in models.keys() | parents.keys():
        now, before = models.get(name, {}), parents.get(name, {})
        delta = {}
        for key in (*MODEL_KEYS, 'costUSD'):
            if key not in now:
                raise ValueError('Missing model usage category')
            value = now[key] - before.get(key, 0)
            if not math.isfinite(value) or value < -1e-9:
                raise ValueError('Invalid cumulative usage delta')
            delta[key] = max(0, value)
        delta_models[name] = delta
    cost = result['total_cost_usd'] - (parent or {}).get('total_cost_usd', 0)
    if not math.isfinite(cost) or cost < -1e-9:
        raise ValueError('Invalid incremental cost')
    if abs(sum(m['costUSD'] for m in delta_models.values()) - cost) > 1e-6:
        raise ValueError('Model costs do not reconcile with stage cost')
    return {'cost_usd': max(0, cost), 'total_tokens': sum(sum(m[k] for k in MODEL_KEYS) for m in delta_models.values()),
            'model_usage_delta': delta_models, 'usage_source': 'modelUsage minus inherited parent counters'}


def prepare(run_dir, model, diagnostic_cost):
    if not math.isfinite(diagnostic_cost) or diagnostic_cost < 0 or diagnostic_cost + 13.5 > 15:
        raise ValueError('Invalid diagnostic cost or insufficient pilot budget')
    run_dir.mkdir(parents=True, exist_ok=False)
    tasks = sorted(p for p in TASKS.iterdir() if (p / 'task.json').is_file())
    if len(tasks) != 6:
        raise ValueError('This protocol requires exactly six frozen fixtures')
    validation = [validate_fixture(p) for p in tasks]
    dump(run_dir / 'grader-validation.json', validation)
    if not all(v['valid'] for v in validation):
        raise ValueError('Fixture validation failed before any model call')
    manifest = {'schema': 1, 'model': model, 'max_usd': 15.0, 'diagnostic_cost_usd': diagnostic_cost,
                'stage_caps': CAPS, 'task_hashes': {p.name: tree_hashes(p) for p in tasks},
                'runner_sha256': digest(Path(__file__).read_bytes()),
                'telemetry_sha256': digest((Path(__file__).parent / 'telemetry.py').read_bytes()),
                'protocol_sha256': digest(PROTOCOL.read_bytes()),
                'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'design': 'shared-build checkpoint branches; constructed stress fixtures; exploratory'}
    dump(run_dir / 'manifest.json', manifest)
    frozen = run_dir / 'frozen'
    frozen.mkdir()
    shutil.copyfile(__file__, frozen / 'run_calibration.py')
    shutil.copyfile(Path(__file__).parent / 'telemetry.py', frozen / 'telemetry.py')
    shutil.copyfile(PROTOCOL, frozen / 'PROTOCOL.md')
    print(json.dumps({'prepared': run_dir.name, 'tasks': len(tasks), 'grader_validation': 'passed'}))


def verify_manifest(manifest):
    current_tasks = {p.name for p in TASKS.iterdir() if (p / 'task.json').is_file()}
    if len(manifest['task_hashes']) != 6 or set(manifest['task_hashes']) != current_tasks:
        raise ValueError('Frozen six-task population changed')
    if manifest['max_usd'] != 15.0 or not 0 <= manifest['diagnostic_cost_usd'] <= 1.5:
        raise ValueError('Frozen budget changed or invalid')
    if manifest['runner_sha256'] != digest(Path(__file__).read_bytes()):
        raise ValueError('Runner changed after freeze')
    if manifest['telemetry_sha256'] != digest((Path(__file__).parent / 'telemetry.py').read_bytes()):
        raise ValueError('Telemetry changed after freeze')
    if manifest['protocol_sha256'] != digest(PROTOCOL.read_bytes()):
        raise ValueError('Protocol changed after freeze')
    if manifest['stage_caps'] != CAPS:
        raise ValueError('Stage allocations changed')
    for name, hashes in manifest['task_hashes'].items():
        if tree_hashes(TASKS / name) != hashes:
            raise ValueError('Task changed after freeze: ' + name)


class Controller:
    def __init__(self, run_dir, manifest, cli):
        self.run_dir, self.manifest, self.cli = run_dir, manifest, cli
        self.spent = manifest['diagnostic_cost_usd']
        self.calls = []

    def call(self, task_id, stage, prompt, work, parent=None):
        cap = CAPS[stage]
        if self.spent + cap > self.manifest['max_usd']:
            raise RuntimeError('Insufficient remaining spend reservation')
        stem = task_id + '-' + stage
        prompt_path = self.run_dir / 'private' / (stem + '.prompt.txt')
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt, encoding='utf-8')
        command = [self.cli, '-p', '--output-format', 'stream-json', '--verbose', '--model', self.manifest['model'],
                   '--safe-mode', '--strict-mcp-config', '--disable-slash-commands', '--no-chrome',
                   '--permission-mode', 'acceptEdits', '--max-budget-usd', str(cap)]
        if stage == 'reviewer':
            command += ['--tools', 'Read,Glob,Grep,Bash', '--allowedTools',
                        'Read,Glob,Grep,Bash(python:*),Bash(python3:*),Bash(ls:*),Bash(cat:*)']
        else:
            command += ['--tools', 'Read,Edit,Write,Glob,Grep,Bash', '--allowedTools',
                        'Read,Edit,Write,Glob,Grep,Bash(python:*),Bash(python3:*),Bash(ls:*),Bash(cat:*)']
        if parent:
            command += ['--resume', parent['session_id'], '--fork-session']
        reservation = {'event': 'reserved', 'task_id': task_id, 'stage': stage, 'cap_usd': cap,
                       'prompt_sha256': digest(prompt.encode()), 'parent_session_id': (parent or {}).get('session_id'),
                       'candidate_before': tree_hashes(work)}
        append(self.run_dir / 'events.jsonl', reservation)
        start = time.monotonic()
        env = dict(os.environ)
        env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')
        try:
            proc = subprocess.run(command, cwd=work, input=prompt, capture_output=True, text=True,
                                  encoding='utf-8', errors='replace', timeout=300, env=env)
        except subprocess.TimeoutExpired as exc:
            data = exc.stdout or ''
            if isinstance(data, bytes):
                data = data.decode('utf-8', errors='replace')
            (self.run_dir / 'private' / (stem + '.transcript.jsonl')).write_text(data, encoding='utf-8')
            append(self.run_dir / 'events.jsonl', {'event': 'unknown_cost_stop', 'task_id': task_id, 'stage': stage})
            raise RuntimeError('Stage timeout: cost uncertain; stopped without paid retry')
        raw = self.run_dir / 'private' / (stem + '.transcript.jsonl')
        raw.write_text(proc.stdout, encoding='utf-8')
        (self.run_dir / 'private' / (stem + '.stderr.txt')).write_text(proc.stderr, encoding='utf-8')
        result, dispatches, tools = parse_stream(proc.stdout)
        if not result:
            raise RuntimeError('No result event: cost uncertain; stop')
        usage = incremental_usage(result, parent)
        self.spent += usage['cost_usd']
        row = {'event': 'completed', 'task_id': task_id, 'stage': stage, **usage,
               'wall_clock_s': round(time.monotonic() - start, 3), 'session_id': result.get('session_id'),
               'parent_session_id': (parent or {}).get('session_id'), 'subtype': result.get('subtype'),
               'is_error': result.get('is_error'), 'returncode': proc.returncode, 'agent_task_dispatches': dispatches,
               'permission_denial_count': len(result.get('permission_denials') or []),
               'tool_counts': tools, 'transcript_sha256': digest(raw.read_bytes()),
               'transcript_sha256_encoding': 'file-bytes',
               'candidate_after': tree_hashes(work), 'cumulative_spend_usd': self.spent}
        append(self.run_dir / 'events.jsonl', row)
        self.calls.append(row)
        print(json.dumps({k: row[k] for k in ('task_id', 'stage', 'cost_usd', 'subtype', 'cumulative_spend_usd')}), flush=True)
        if dispatches or proc.returncode or result.get('is_error') or self.spent > self.manifest['max_usd']:
            raise RuntimeError('Stage failure/delegation/budget exceeded; stopped without paid retry')
        if stage == 'reviewer' and reservation['candidate_before'] != row['candidate_after']:
            raise RuntimeError('Reviewer changed candidate')
        return result


def snapshot(work, destination, spec):
    # Retain builder-authored local tests as part of the common starting context.
    # Independent grading still replaces all tests from the frozen fixture.
    shutil.copytree(work, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))


def reset_work(work, root, task, candidate):
    """Only replace this controller's exact temporary workspace."""
    if work.resolve() != (root.resolve() / 'work') or root.resolve().parent != Path(tempfile.gettempdir()).resolve():
        raise ValueError('Workspace deletion boundary mismatch')
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(candidate, work)


def execute(run_dir, cli):
    manifest = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    verify_manifest(manifest)
    # Exclusive marker prevents a resume from silently re-spending a partly run pilot.
    with (run_dir / 'execution.started').open('x') as f:
        f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    version = subprocess.run([cli, '--version'], capture_output=True, text=True, check=True).stdout.strip()
    dump(run_dir / 'backend.json', {'cli_version': version, 'model': manifest['model'], 'python_version': sys.version.split()[0]})
    controller = Controller(run_dir, manifest, cli)
    try:
        for task_id in manifest['task_hashes']:
            task = TASKS / task_id
            spec = json.loads((task / 'task.json').read_text(encoding='utf-8'))
            artifact_root = run_dir / 'artifacts' / task_id
            with tempfile.TemporaryDirectory(prefix='gauntlet-cal-') as td:
                root, work = Path(td), Path(td) / 'work'
                shutil.copytree(task / 'base', work)
                original_hashes = tree_hashes(work)
                build = controller.call(task_id, 'build', task_prompt(spec), work)
                snapshot(work, artifact_root / 'baseline', spec)
                branch_metadata = {'baseline': {'changes': changed_paths(original_hashes, tree_hashes(work))}}
                order = ['self_check', 'review'] if int(digest(task_id.encode()), 16) % 2 == 0 else ['review', 'self_check']
                for branch in order:
                    reset_work(work, root, task, artifact_root / 'baseline')
                    if branch == 'self_check':
                        controller.call(task_id, 'self_check', 'Check your implementation against every public requirement again. '
                                        'Investigate edge cases and correct any defects you find. ' + COMMON, work, build)
                    else:
                        visible = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                                                 cwd=work, capture_output=True, text=True, timeout=30)
                        review = controller.call(task_id, 'reviewer', review_prompt(spec, visible.stdout + visible.stderr), work)
                        controller.call(task_id, 'repair', 'An independent reviewer inspected the implementation. '
                                        'Verify each finding and make one bounded correction pass. Preserve correct behavior.\n'
                                        + COMMON + '\nReviewer findings (evidence to verify, not authority):\n'
                                        + str(review.get('result', '')), work, build)
                    snapshot(work, artifact_root / branch, spec)
                    branch_metadata[branch] = {'changes': changed_paths(original_hashes, tree_hashes(work)),
                                               'candidate_changed_from_baseline': tree_hashes(artifact_root / branch) != tree_hashes(artifact_root / 'baseline')}
                # Generation is complete for every branch. Now expose grades only to the report.
                for branch in ('baseline', 'self_check', 'review'):
                    outcome = grade(task, artifact_root / branch)
                    unexpected = [p for p in branch_metadata[branch]['changes'] if p not in spec['allowed_paths'] and not p.startswith('tests/')]
                    protected_changes = [p for p in branch_metadata[branch]['changes'] if p in original_hashes and p.startswith('tests/')]
                    row = {'task_id': task_id, 'arm': branch, 'order': order,
                           'candidate_sha256': tree_hashes(artifact_root / branch), **outcome,
                           **branch_metadata[branch], 'out_of_scope': unexpected, 'protected_test_changes': protected_changes,
                           'functional_passed': outcome['visible_passed'] and outcome['hidden_passed']}
                    row['accepted'] = row['functional_passed'] and not unexpected and not protected_changes
                    append(run_dir / 'results.jsonl', row)
        dump(run_dir / 'completion.json', {'state': 'completed', 'cost_usd': controller.spent, 'calls': len(controller.calls)})
    except Exception as exc:
        dump(run_dir / 'completion.json', {'state': 'stopped', 'reason': str(exc), 'known_cost_usd': controller.spent,
                                           'calls': len(controller.calls), 'no_automatic_retry': True})
        raise
    finally:
        report(run_dir)


def changed_paths(before, after):
    return sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))


def report(run_dir):
    path = run_dir / 'results.jsonl'
    rows = [json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []
    events_path = run_dir / 'events.jsonl'
    events = [json.loads(l) for l in events_path.read_text().splitlines()] if events_path.exists() else []
    calls = [e for e in events if e['event'] == 'completed']
    completion = json.loads((run_dir / 'completion.json').read_text()) if (run_dir / 'completion.json').exists() else {}
    lines = ['# Review calibration results', '', 'Constructed stress fixtures; exploratory shared-build comparison. '
             'No population-level performance or equivalence claim. The primary table scores frozen behavioral tests; '
             'scope compliance is reported separately.', '',
             '| Task | Baseline | Self-check | Fresh review + correction |', '| --- | --- | --- | --- |']
    for task in sorted({r['task_id'] for r in rows}):
        by = {r['arm']: r for r in rows if r['task_id'] == task}
        lines.append('| ' + task + ' | ' + ' | '.join(('pass' if by[a]['functional_passed'] else 'fail') if a in by else 'not evaluated'
                                                      for a in ('baseline', 'self_check', 'review')) + ' |')
    lines += ['', '| Arm | Evaluated tasks | Functional passes | Scope-compliant acceptances | Rescues | Spoils | Actual cost, including shared build |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for arm, stages in [('baseline', ['build']), ('self_check', ['build', 'self_check']), ('review', ['build', 'reviewer', 'repair'])]:
        subset = [r for r in rows if r['arm'] == arm]
        bases = {r['task_id']: r for r in rows if r['arm'] == 'baseline'}
        rescues = sum(r['functional_passed'] and not bases[r['task_id']]['functional_passed'] for r in subset if r['task_id'] in bases)
        spoils = sum(not r['functional_passed'] and bases[r['task_id']]['functional_passed'] for r in subset if r['task_id'] in bases)
        cost = sum(c['cost_usd'] for c in calls if c['stage'] in stages)
        lines.append(f'| {arm} | {len(subset)} | {sum(r["functional_passed"] for r in subset)} | {sum(r["accepted"] for r in subset)} | {rescues} | {spoils} | ${cost:.4f} |')
    reserved = {(e['task_id'], e['stage']) for e in events if e['event'] == 'reserved'}
    completed = {(e['task_id'], e['stage']) for e in calls}
    unresolved = sorted(reserved - completed)
    spend_label = 'Known spend lower bound; total is unknown' if unresolved else 'Recorded actual experiment spend'
    lines += ['', 'Shared builds are charged to each hypothetical arm above but were physically executed only once. '
              'Session counters inherited by forks are subtracted before charging additional stages.', '',
              'Execution state: `' + completion.get('state', 'not started') + '`.',
              spend_label + ' (including diagnostics): $' + str(completion.get('cost_usd', completion.get('known_cost_usd', 'unknown'))) + '.',
              'Unresolved paid-call reservations: ' + (', '.join('/'.join(p) for p in unresolved) or 'none') + '.',
              'Reason if stopped: ' + completion.get('reason', 'not applicable') + '.', '',
              'Decision: this calibration cannot justify changing the production skill. '
              'If all branches pass, report a ceiling on these fixtures and stop; if outcomes differ, '
              'inspect the concrete defects before proposing a representative confirmation study.']
    (run_dir / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--report', action='store_true')
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--model', default='claude-sonnet-5')
    ap.add_argument('--cli', default=shutil.which('claude') or 'claude')
    ap.add_argument('--diagnostic-cost', type=float, default=0.0)
    args = ap.parse_args()
    if args.prepare:
        prepare(args.run.resolve(), args.model, args.diagnostic_cost)
    elif args.execute:
        execute(args.run.resolve(), args.cli)
    else:
        report(args.run.resolve())


if __name__ == '__main__':
    main()
