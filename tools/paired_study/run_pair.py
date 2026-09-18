"""Run one pair: create a worktree per arm from the spec's base commit, launch a headless agent session with the
arm prompt, collect the milestone line, and append a results row. Dry-run mode prints what would happen.

Usage:
  python tools/paired_study/run_pair.py --pair research/program/paired-study/pairs/<task>/<flag> --dry-run
  python tools/paired_study/run_pair.py --pair ... --execute --agent claude   # or --agent codex

Execute mode is UNTESTED at the time of writing (17 September 2026). It shells out to the host CLI
(`claude -p <prompt>` or `codex exec <prompt>`) inside the arm's worktree, which spends model tokens. The first
pair is the harness test; run it on the cheapest task and read the transcript before trusting the results row.
The runner refuses to execute when the spec hash in the manifest no longer matches the spec file.
"""
import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


def argv_for(command):
    """Split a committed command string without a shell and resolve the executable (npm.cmd on Windows)."""
    parts = shlex.split(command, posix=True)
    exe = shutil.which(parts[0]) or parts[0]
    return [exe, *parts[1:]]

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / '.validation-deps'))
import yaml  # noqa: E402


def projects_root():
    """Real projects root from GAUNTLET_PROJECTS_ROOT or the gitignored ledger/config.local.json; never committed."""
    import os
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pair', required=True)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--execute', action='store_true')
    ap.add_argument('--agent', choices=['claude', 'codex'], default='claude')
    ap.add_argument('--worktrees', default=str(repo / '.paired-worktrees'))
    args = ap.parse_args()
    pair = Path(args.pair)
    manifest = json.loads((pair / 'manifest.json').read_text(encoding='utf-8'))
    spec_path = Path(manifest['spec_path'])
    spec_bytes = spec_path.read_bytes()
    if hashlib.sha256(spec_bytes).hexdigest() != manifest['spec_sha256']:
        print('REFUSED: spec changed since the pair was generated; regenerate the pair or restore the spec', file=sys.stderr)
        return 2
    spec = yaml.safe_load(spec_bytes)
    if isinstance(spec.get('repo'), str):
        spec['repo'] = spec['repo'].replace('<projects-root>', projects_root())
    for key in ('base_commit', 'answer_commit'):
        if key in spec:
            spec[key] = str(spec[key])  # an all-digit hash would otherwise parse as an integer
    results_path = pair.parent.parent.parent / 'results.jsonl'
    plan = []
    for arm in manifest['order']:
        wt = Path(args.worktrees) / spec['task_id'] / manifest['flag'] / arm
        prompt_file = pair / f'arm{arm}.prompt.md'
        if args.agent == 'claude':
            cmd = ['claude', '-p', f'@{prompt_file}', '--output-format', 'json']
        else:
            cmd = ['codex', 'exec', prompt_file.read_text(encoding='utf-8')]
        plan.append({'arm': arm, 'worktree': str(wt), 'base_commit': spec['base_commit'], 'command': cmd[:3] + (['...'] if len(cmd) > 3 else []), 'results_row_to': str(results_path)})
    if args.dry_run or not args.execute:
        print(json.dumps({'mode': 'dry-run', 'task_id': spec['task_id'], 'flag': manifest['flag'], 'plan': plan, 'model_tokens_used': 0}, indent=2))
        return 0
    for step in plan:
        wt = Path(step['worktree'])
        if wt.exists():
            shutil.rmtree(wt)
        # A local clone shares objects read-only and writes nothing into the source repository's .git.
        run(['git', 'clone', '-q', spec['repo'], str(wt)])
        run(['git', 'checkout', '-q', '--detach', spec['base_commit']], cwd=wt)
        for test_file in spec.get('test_files_from_answer', []):
            run(['git', 'checkout', '-q', spec['answer_commit'], '--', test_file], cwd=wt)
        for held in spec.get('held_out_files', []):
            (wt / held).unlink(missing_ok=True)
        run(['git', 'commit', '-q', '--allow-empty', '-am', 'paired-study task base: tests from answer commit, held-out removed'], cwd=wt, check=False)
        for rel in spec.get('setup_copy_from_repo', []) or []:
            # e.g. node_modules, so the clone runs offline; copied in Python, no shell involved
            src = Path(spec['repo']) / rel
            if src.is_dir():
                shutil.copytree(src, wt / rel, dirs_exist_ok=True)
            elif src.is_file():
                shutil.copyfile(src, wt / rel)
        t0 = time.time()
        arm = step['arm']
        prompt = (pair / f'arm{arm}.prompt.md').read_text(encoding='utf-8')
        cmd = [shutil.which('claude') or 'claude', '-p', prompt, '--output-format', 'json'] if args.agent == 'claude' else [shutil.which('codex') or 'codex', 'exec', prompt]
        proc = subprocess.run(cmd, cwd=wt, capture_output=True, text=True)
        (pair / f'arm{arm}.transcript.json').write_text(proc.stdout, encoding='utf-8')
        # stage 1: the suite exactly as the builder saw it
        verify = subprocess.run(argv_for(spec['test_command']), cwd=wt, capture_output=True, text=True)
        # stage 2: add held-out tests (from the answer commit or from the study's own files) and rerun
        for held in spec.get('held_out_files', []):
            run(['git', 'checkout', '-q', spec['answer_commit'], '--', held], cwd=wt, check=False)
        for item in spec.get('held_out_study_files', []):
            dst = wt / item['dst']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / item['src'], dst)
        verify_heldout = subprocess.run(argv_for(spec['test_command']), cwd=wt, capture_output=True, text=True) if (spec.get('held_out_files') or spec.get('held_out_study_files')) else None
        milestone = None
        rj = wt / 'gauntlet/runs.jsonl'
        if rj.exists():
            lines = [l for l in rj.read_text(encoding='utf-8').splitlines() if l.strip()]
            milestone = json.loads(lines[-1]) if lines else None
        row = {'task_id': spec['task_id'], 'flag': manifest['flag'], 'arm': arm, 'accepted': verify.returncode == 0 and bool(milestone) and milestone.get('state') == 'accepted',
               'independent_test_rc': verify.returncode,
               'held_out_passed': (verify_heldout.returncode == 0) if verify_heldout is not None else 'not applicable',
               'reviews_used': (milestone or {}).get('reviews', {}).get('run_used', 'unknown') if milestone else 'unknown',
               'subagent_tokens': 'unknown', 'wall_clock_s': round(time.time() - t0), 'harness_failure': proc.returncode != 0, 'milestone': milestone}
        with results_path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        manifest['runs'][arm] = {'finished_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'harness_rc': proc.returncode, 'independent_test_rc': verify.returncode}
        (pair / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
