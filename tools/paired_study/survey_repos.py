"""Deterministic task-pool survey: find git repositories with test suites and recent commits that touched tests.

Zero model tokens; read-only git commands only. Replaces the agent survey that died on a session rate limit.
Writes research/program/paired-study/task-pool-survey-<date>.md and .json.
Usage: python tools/paired_study/survey_repos.py [--root C:/path/to/projects] [--days 120] [--max-commits 8]
"""
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
_cfg = json.loads((Path(__file__).resolve().parent / 'survey_config.json').read_text(encoding='utf-8'))
EXCLUDE_NAMES = set(_cfg['exclude_dir_names'])
FLAG_SUBSTRINGS = tuple(_cfg['flag_name_substrings'])
TEST_PATTERNS = re.compile(r'(^|/)(tests?|__tests__|e2e|spec)(/|$)|(^|/)test_[^/]+\.py$|_test\.py$|\.test\.[cm]?[jt]sx?$|\.spec\.[cm]?[jt]sx?$')


def git(args, cwd, timeout=60):
    try:
        p = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        return p.stdout if p.returncode == 0 else ''
    except (subprocess.TimeoutExpired, OSError):
        return ''


def find_repos(root, max_depth=2):
    found = []

    def walk(d, depth):
        if depth > max_depth:
            return
        try:
            kids = sorted(p for p in d.iterdir() if p.is_dir())
        except OSError:
            return
        for k in kids:
            if k.name in EXCLUDE_NAMES:
                continue
            if (k / '.git').exists():
                found.append(k)
                continue
            walk(k, depth + 1)

    walk(Path(root), 1)
    return found


def detect_runner(path):
    runners, cmd, browser = [], None, False
    pkg = path / 'package.json'
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding='utf-8', errors='replace'))
        except json.JSONDecodeError:
            data = {}
        scripts = data.get('scripts', {}) or {}
        deps = {**(data.get('dependencies') or {}), **(data.get('devDependencies') or {})}
        if 'test' in scripts:
            cmd = f"npm test  ({scripts['test']})"
        for name in ('vitest', 'jest', 'mocha', 'playwright', '@playwright/test', 'puppeteer', 'cypress'):
            if name in deps or (cmd and '/' not in name and name in cmd):
                runners.append(name)
        if cmd and re.search(r'\b(node|tsx)\s+(--test|-?-?test)\b', cmd):
            runners.append('node:test')
        if any(n in deps for n in ('playwright', '@playwright/test', 'puppeteer', 'cypress')):
            browser = True
    if (path / 'pyproject.toml').exists() or (path / 'pytest.ini').exists() or (path / 'setup.cfg').exists() or list(path.glob('tests/test_*.py')) or list(path.glob('test_*.py')):
        runners.append('pytest')
        cmd = cmd or 'python -m pytest -q'
    return sorted(set(runners)), cmd, browser


def recent_test_commits(path, days, limit):
    out = git(['log', f'--since={days}.days', '--no-merges', '--date=short', '--format=%h|%ad|%s', '--name-only'], path, timeout=120)
    commits, cur = [], None
    for line in out.splitlines():
        if '|' in line and re.match(r'^[0-9a-f]{7,}\|', line):
            if cur:
                commits.append(cur)
            h, d, s = line.split('|', 2)
            cur = {'hash': h, 'date': d, 'subject': s[:90], 'files': []}
        elif line.strip() and cur is not None:
            cur['files'].append(line.strip())
    if cur:
        commits.append(cur)
    picked = []
    for c in commits:
        tests = [f for f in c['files'] if TEST_PATTERNS.search(f)]
        if not tests:
            continue
        stat = git(['show', '--shortstat', '--format=', c['hash']], path)
        m = re.search(r'(\d+) insertions?', stat)
        n = re.search(r'(\d+) deletions?', stat)
        changed = (int(m.group(1)) if m else 0) + (int(n.group(1)) if n else 0)
        picked.append({**c, 'files_touched': len(c['files']), 'test_files': tests[:6], 'lines_changed': changed,
                       'fix_like': bool(re.search(r'\b(fix|bug|regress|repair|broken|correct)\b', c['subject'], re.I))})
        if len(picked) >= limit:
            break
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=_cfg['root'])
    ap.add_argument('--days', type=int, default=120)
    ap.add_argument('--max-commits', type=int, default=8)
    args = ap.parse_args()
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    rows = []
    for r in find_repos(args.root):
        runners, cmd, browser = detect_runner(r)
        commit_count = git(['rev-list', '--count', 'HEAD'], r).strip() or 'unknown'
        last = git(['log', '-1', '--date=short', '--format=%ad'], r).strip() or 'unknown'
        tracked = git(['ls-files'], r).splitlines()
        src = [f for f in tracked if re.search(r'\.(py|[cm]?[jt]sx?|html|css)$', f) and 'node_modules' not in f]
        flagged = any(s in r.name.lower() or s in r.parent.name.lower() for s in FLAG_SUBSTRINGS)
        rows.append({'repo': str(r), 'name': r.name, 'commits': commit_count, 'last_commit': last, 'tracked_files': len(tracked), 'source_files': len(src),
                     'runners': runners, 'test_command': cmd, 'browser_needed': browser, 'flagged_name': flagged,
                     'test_commits': recent_test_commits(r, args.days, args.max_commits) if runners else []})
    out_dir = repo / 'research/program/paired-study'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f'task-pool-survey-{today}.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    with_tests = [r for r in rows if r['runners']]
    md = [f'# Task-pool survey, {today}', '', f'Generated by `tools/paired_study/survey_repos.py` over `{args.root}` (depth 2), read-only git, zero model tokens. Excluded directory names: {", ".join(sorted(EXCLUDE_NAMES))}. Repositories whose name suggests client or company data are flagged, not read further.', '',
          f'Repositories found: {len(rows)}. With a detectable test runner: {len(with_tests)}. Candidate commits touching tests in the last {args.days} days: {sum(len(r["test_commits"]) for r in rows)}.', '',
          '## Repositories with test runners', '', '| repo | commits | last commit | source files | runners | test command | browser | flagged |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in with_tests:
        md.append(f"| {r['name']} | {r['commits']} | {r['last_commit']} | {r['source_files']} | {', '.join(r['runners'])} | {r['test_command'] or 'unknown'} | {'yes' if r['browser_needed'] else 'no'} | {'yes' if r['flagged_name'] else 'no'} |")
    md += ['', '## Candidate commits (touched a test file)', '', '| repo | hash | date | subject | files | test files | lines changed | fix-like |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in with_tests:
        for c in r['test_commits']:
            md.append(f"| {r['name']} | {c['hash']} | {c['date']} | {c['subject'].replace('|', '/')} | {c['files_touched']} | {len(c['test_files'])} | {c['lines_changed']} | {'yes' if c['fix_like'] else 'no'} |")
    md += ['', '## Repositories without a detected runner', '', ', '.join(r['name'] for r in rows if not r['runners']) or 'none', '',
           '## Reading this', '', 'A candidate commit becomes a task by reverting its non-test changes at a new base commit and keeping its tests; the original commit is the answer. Rank by: deterministic runner, no browser, lines changed under about 80, fix-like subject, unflagged repository. Ranking is a judgment step done by a person or the lead, recorded in `phase2-paired-study.md` section 2.']
    (out_dir / f'task-pool-survey-{today}.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'repos': len(rows), 'with_runner': len(with_tests), 'candidate_commits': sum(len(r['test_commits']) for r in rows), 'flagged': [r['name'] for r in rows if r['flagged_name']], 'out': str(out_dir), 'model_tokens_used': 0}))


if __name__ == '__main__':
    main()
