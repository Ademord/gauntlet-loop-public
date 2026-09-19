"""Run one pair: for each arm, clone the task repository outside any other repository, build the task base, launch
a headless agent with the arm prompt, verify independently of the agent, and append a results row.

Usage:
  python tools/paired_study/run_pair.py --pair research/program/paired-study/pairs/<task>/<flag> --dry-run
  python tools/paired_study/run_pair.py --pair ... --execute [--model claude-sonnet-5] [--timeout-min 45] [--arms A]

The task base is the spec's base commit with the answer commit's test files copied in and held-out files removed,
or the base commit with one recorded mutation applied (mutation-minted tasks). Execute mode spends model tokens:
each arm runs `claude -p` with the prompt on stdin, stream-json output, a pinned model, permission mode acceptEdits,
and a tool allowlist. Verification never trusts the agent: protected test paths are restored to the task base
before the suite runs (editing a failing test cannot pass it), changed files outside the allowed paths are reported,
and held-out tests run last. Measured cost, tokens, turns, and critic dispatches come from the transcript.
The runner refuses a spec whose hash changed after the pair was generated.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / '.validation-deps'))
import yaml  # noqa: E402

ALLOWED_TOOLS = ['Read', 'Edit', 'Write', 'Glob', 'Grep', 'Agent', 'Task', 'TodoWrite',
                 'Bash(python:*)', 'Bash(python3:*)', 'Bash(py:*)', 'Bash(pytest:*)', 'Bash(npm:*)', 'Bash(node:*)',
                 'Bash(git status:*)', 'Bash(git diff:*)', 'Bash(git log:*)', 'Bash(git show:*)', 'Bash(git rev-parse:*)',
                 'Bash(ls:*)', 'Bash(cat:*)', 'Bash(head:*)', 'Bash(tail:*)', 'Bash(grep:*)', 'Bash(wc:*)',
                 'Bash(sha256sum:*)', 'Bash(mkdir:*)', 'Bash(echo:*)', 'Bash(cd:*)', 'Bash(tee:*)', 'Bash(find:*)', 'Bash(diff:*)',
                 'Bash(sed:*)', 'Bash(awk:*)', 'Bash(cut:*)', 'Bash(sort:*)', 'Bash(uniq:*)', 'Bash(date:*)', 'Bash(pwd:*)', 'Bash(printf:*)']
DENIED_TOOLS = ['WebSearch', 'WebFetch', 'ToolSearch', 'ScheduleWakeup', 'NotebookEdit']  # an arm stays offline and local
GIT_ID = ['-c', 'user.name=paired-study', '-c', 'user.email=paired-study@example.invalid']
ISOLATION = ['--setting-sources', 'project,local', '--strict-mcp-config', '--disable-slash-commands']  # no user hooks, plugins, MCP servers, or skills in an arm


def argv_for(command):
    """Split a committed command string without a shell and resolve the executable (npm.cmd on Windows)."""
    parts = shlex.split(command, posix=True)
    return [shutil.which(parts[0]) or parts[0], *parts[1:]]


def projects_root():
    """Real projects root from GAUNTLET_PROJECTS_ROOT or the gitignored ledger/config.local.json; never committed."""
    env = os.environ.get('GAUNTLET_PROJECTS_ROOT')
    if env:
        return env
    local = repo / 'ledger/config.local.json'
    if local.exists():
        roots = json.loads(local.read_text(encoding='utf-8')).get('roots') or []
        if roots:
            return roots[0]
    return '<projects-root>'


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def rmtree(path):
    def onerror(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=onerror)


def load(pair):
    manifest = json.loads((pair / 'manifest.json').read_text(encoding='utf-8'))
    spec_path = Path(manifest['spec_path'])
    if not spec_path.is_absolute():
        spec_path = repo / spec_path
    spec_bytes = spec_path.read_bytes()
    if hashlib.sha256(spec_bytes).hexdigest() != manifest['spec_sha256']:
        raise SystemExit('REFUSED: spec changed since the pair was generated; regenerate the pair or restore the spec')
    spec = yaml.safe_load(spec_bytes)
    spec['repo'] = str(spec['repo']).replace('<projects-root>', projects_root())
    for key in ('base_commit', 'answer_commit'):
        if key in spec:
            spec[key] = str(spec[key])
    return manifest, spec


def build_task_base(spec, wt):
    if wt.exists():
        rmtree(wt)
    run(['git', 'clone', '-q', spec['repo'], str(wt)])  # a local clone writes nothing into the source repository
    run(['git', 'checkout', '-q', '--detach', spec['base_commit']], cwd=wt)
    for f in spec.get('test_files_from_answer', []) or []:
        run(['git', 'checkout', '-q', spec['answer_commit'], '--', f], cwd=wt)
    held_contents = {}
    for f in spec.get('held_out_files', []) or []:
        shown = subprocess.run(['git', 'show', f"{spec['answer_commit']}:{f}"], cwd=wt, capture_output=True)
        if shown.returncode == 0:
            held_contents[f] = shown.stdout
        (wt / f).unlink(missing_ok=True)
    mut = spec.get('mutation')
    if mut:
        target = wt / mut['file']
        lines = target.read_bytes().split(b'\n')
        line = lines[mut['line'] - 1]
        if line[mut['col_start']:mut['col_end']] != mut['original'].encode():
            raise SystemExit(f"mutation anchor mismatch in {mut['file']}:{mut['line']}")
        lines[mut['line'] - 1] = line[:mut['col_start']] + mut['mutated'].encode() + line[mut['col_end']:]
        target.write_bytes(b'\n'.join(lines))
    # Drop the history: with the upstream fix (or the pre-mutation commit) reachable, an arm could read the answer
    # instead of solving the task. The task base becomes a single commit in a fresh repository.
    rmtree(wt / '.git')
    run(['git', 'init', '-q', '-b', 'main'], cwd=wt)
    run(['git', *GIT_ID, 'add', '-A'], cwd=wt)
    run(['git', *GIT_ID, 'commit', '-q', '-m', 'task base'], cwd=wt)
    for rel in spec.get('setup_copy_from_repo', []) or []:
        src = Path(spec['repo']) / rel
        if src.is_dir():
            shutil.copytree(src, wt / rel, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copyfile(src, wt / rel)
    return run(['git', 'rev-parse', 'HEAD'], cwd=wt).stdout.strip(), held_contents


def parse_stream(text):
    result, dispatches, tools = None, 0, {}
    for line in text.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get('type') == 'assistant' and ev.get('parent_tool_use_id') is None:
            for c in (ev.get('message') or {}).get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    tools[c.get('name')] = tools.get(c.get('name'), 0) + 1
                    if c.get('name') in ('Agent', 'Task'):
                        dispatches += 1
        elif ev.get('type') == 'result':
            result = ev
    return result, dispatches, tools


def preflight(model, env):
    """Spend a few tokens to confirm the CLI is authenticated before anything is cloned."""
    cmd = [shutil.which('claude') or 'claude', '-p', '--output-format', 'json', '--model', model, *ISOLATION]
    try:
        p = subprocess.run(cmd, input='Reply with the single word OK.', capture_output=True, text=True, encoding='utf-8',
                           errors='replace', env=env, timeout=180)
        res = json.loads(p.stdout or '{}')
    except (subprocess.TimeoutExpired, ValueError) as exc:
        return False, f'preflight error: {exc}'
    if res.get('is_error') or not res:
        return False, str(res.get('result') or p.stderr)[:200]
    return True, f"authenticated; preflight cost {res.get('total_cost_usd')} USD"


def under(path, prefixes):
    return any(path == p.rstrip('/') or path.startswith(p.rstrip('/') + '/') for p in prefixes)


def verify(spec, wt, base, held_contents):
    protected = spec.get('protected_paths', ['tests', 'test'])
    copied = spec.get('setup_copy_from_repo', []) or []
    tracked = [t for t in run(['git', 'ls-tree', '-r', '--name-only', base], cwd=wt).stdout.split('\n') if t]
    protected_tracked = [t for t in tracked if under(t, protected)]
    protected_modified = [t for t in run(['git', 'diff', '--name-only', base, '--', *protected], cwd=wt).stdout.split() if t in protected_tracked] if protected_tracked else []
    if protected_tracked:
        run(['git', 'checkout', '-q', base, '--', *protected_tracked], cwd=wt)
    changed = set(run(['git', 'diff', '--name-only', base], cwd=wt).stdout.split())
    changed |= set(run(['git', 'ls-files', '--others', '--exclude-standard'], cwd=wt).stdout.split())
    changed = {c for c in changed if not under(c, copied) and not under(c, ['gauntlet'])}
    out_of_scope = sorted(c for c in changed if c not in (spec.get('allowed_paths') or []) and not under(c, protected))
    suite = subprocess.run(argv_for(spec['test_command']), cwd=wt, capture_output=True, text=True, timeout=900)
    held = None
    if spec.get('held_out_files') or spec.get('held_out_study_files'):
        for f, data in held_contents.items():
            (wt / f).parent.mkdir(parents=True, exist_ok=True)
            (wt / f).write_bytes(data)
        for item in spec.get('held_out_study_files', []) or []:
            (wt / item['dst']).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / item['src'], wt / item['dst'])
        held = subprocess.run(argv_for(spec['test_command']), cwd=wt, capture_output=True, text=True, timeout=900)
    return {'suite_rc': suite.returncode, 'suite_tail': suite.stdout.strip().splitlines()[-1:] if suite.stdout.strip() else [],
            'held_out_passed': (held.returncode == 0) if held is not None else 'not applicable',
            'protected_modified': protected_modified, 'changed_files': sorted(changed), 'out_of_scope': out_of_scope}


def milestone_of(wt):
    rj = wt / 'gauntlet/runs.jsonl'
    if not rj.exists():
        return None
    lines = [l for l in rj.read_text(encoding='utf-8', errors='replace').splitlines() if l.strip()]
    try:
        return json.loads(lines[-1]) if lines else None
    except ValueError:
        return None


def find_key(obj, names):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in names and isinstance(v, (int, str)) and not isinstance(v, bool):
                return v
        for v in obj.values():
            found = find_key(v, names)
            if found is not None:
                return found
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pair', required=True)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--execute', action='store_true')
    ap.add_argument('--model', default='claude-sonnet-5')
    ap.add_argument('--timeout-min', type=int, default=45)
    ap.add_argument('--arms', default='')
    ap.add_argument('--worktrees', default=str(Path(tempfile.gettempdir()) / 'gauntlet-pairs'))
    args = ap.parse_args()
    pair = Path(args.pair).resolve()
    manifest, spec = load(pair)
    results_path = repo / 'research/program/paired-study/results.jsonl'
    arms = [a for a in manifest['order'] if not args.arms or a in args.arms]
    base_cmd = [shutil.which('claude') or 'claude', '-p', '--output-format', 'stream-json', '--verbose', '--model', args.model,
                '--permission-mode', 'acceptEdits', *ISOLATION, '--disallowedTools', *DENIED_TOOLS, '--allowedTools', *ALLOWED_TOOLS]
    if args.dry_run or not args.execute:
        print(json.dumps({'mode': 'dry-run', 'task_id': spec['task_id'], 'flag': manifest['flag'], 'order': arms, 'model': args.model,
                          'worktrees': args.worktrees, 'command': base_cmd[1:13] + ['--allowedTools', f'<{len(ALLOWED_TOOLS)} tools>'],
                          'repo_resolved': Path(spec['repo']).exists(), 'model_tokens_used': 0}, indent=2))
        return 0
    env = dict(os.environ, PYTHONPATH=str(repo / '.validation-deps'))
    ok, detail = preflight(args.model, env)
    print(json.dumps({'preflight': ok, 'detail': detail}), flush=True)
    if not ok:
        print('PREFLIGHT FAILED: nothing was cloned or run. For the claude CLI, log in once in a terminal (claude, then /login).', file=sys.stderr)
        return 3
    for arm in arms:
        wt = Path(args.worktrees) / spec['task_id'] / manifest['flag'] / arm
        base, held_contents = build_task_base(spec, wt)
        prompt = (pair / f'arm{arm}.prompt.md').read_text(encoding='utf-8')
        t0 = time.time()
        timed_out = False
        try:
            proc = subprocess.run(base_cmd, cwd=wt, input=prompt, capture_output=True, text=True, encoding='utf-8', errors='replace',
                                  env=env, timeout=args.timeout_min * 60)
            stdout, rc = proc.stdout, proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, rc, timed_out = (exc.stdout.decode(errors='replace') if isinstance(exc.stdout, bytes) else exc.stdout or ''), -1, True
        wall = round(time.time() - t0)
        (pair / f'arm{arm}.transcript.jsonl').write_text(stdout, encoding='utf-8')
        if (wt / 'gauntlet').exists():
            shutil.copytree(wt / 'gauntlet', pair / f'arm{arm}.gauntlet', dirs_exist_ok=True)
        result, dispatches, tools = parse_stream(stdout)
        checks = verify(spec, wt, base, held_contents)
        ms = milestone_of(wt)
        usage = (result or {}).get('usage') or {}
        tokens = sum(usage.get(k, 0) or 0 for k in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'))
        milestone_reviews = find_key(ms, {'reviews_used', 'run_used', 'critic_reviews'}) if ms else None
        row = {'task_id': spec['task_id'], 'flag': manifest['flag'], 'arm': arm, 'model': args.model, 'task_base': base, 'history_orphaned': True,
               'accepted': checks['suite_rc'] == 0 and not checks['out_of_scope'],
               'suite_rc': checks['suite_rc'], 'suite_tail': checks['suite_tail'], 'held_out_passed': checks['held_out_passed'],
               'protected_modified': checks['protected_modified'], 'out_of_scope': checks['out_of_scope'], 'changed_files': checks['changed_files'],
               'agent_state': find_key(ms, {'state', 'outcome_state', 'outcome'}) if ms else None,
               'reviews_used': milestone_reviews if isinstance(milestone_reviews, int) else dispatches,
               'critic_dispatches': dispatches, 'tool_calls': tools,
               'cost_usd': (result or {}).get('total_cost_usd'), 'total_tokens': tokens or None, 'usage': usage or None,
               'num_turns': (result or {}).get('num_turns'), 'agent_duration_s': round(((result or {}).get('duration_ms') or 0) / 1000),
               'wall_clock_s': wall, 'permission_denials': len((result or {}).get('permission_denials') or []),
               'is_error': (result or {}).get('is_error'), 'timed_out': timed_out,
               'harness_failure': timed_out or rc != 0 or result is None or bool((result or {}).get('is_error') and ((result or {}).get('num_turns') or 0) <= 1),
               'harness_failure_reason': 'timeout' if timed_out else ('no result event' if result is None else (str(result.get('result'))[:160] if result.get('is_error') and (result.get('num_turns') or 0) <= 1 else '')),
               'finished_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with results_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        manifest['runs'][arm] = {'finished_utc': row['finished_utc'], 'model': args.model, 'harness_rc': rc, 'accepted': row['accepted']}
        (pair / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: row[k] for k in ('arm', 'accepted', 'suite_rc', 'held_out_passed', 'out_of_scope', 'reviews_used', 'critic_dispatches',
                                              'cost_usd', 'total_tokens', 'num_turns', 'wall_clock_s', 'permission_denials', 'harness_failure')}), flush=True)
        if row['harness_failure'] and (row['num_turns'] or 0) <= 1:
            print('ARM FAILED AT STARTUP: stopping the pair so the other arm is not spent on a broken harness.', file=sys.stderr)
            break
    return 0


if __name__ == '__main__':
    sys.exit(main())
