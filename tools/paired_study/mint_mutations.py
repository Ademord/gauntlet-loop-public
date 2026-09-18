"""Mint low-difficulty paired-study tasks by mutation (backlog B-014). Zero model tokens.

Apply one semantic mutation to a test-covered source line of a Python repository (flip a comparison, swap and/or,
drop a `not`, change a small integer or a boolean literal), run the project's test command, and keep the mutant only
if exactly 1 or 2 tests fail and nothing errors. The task base is the original commit with the mutation applied;
the answer is the original line. At most one task per source line, candidates shuffled with a fixed seed.

Usage:
  python tools/paired_study/mint_mutations.py --repo intelligence-pipeline --files validation.py evaluate.py schema.py
         [--test-command "python -m pytest -q -p no:cacheprovider"] [--max-tasks 12] [--max-candidates 200] [--seed 17]
Writes research/program/paired-study/tasks/m<NNN>-*.yaml and tasks/mutation-index.json. The repository is resolved
under <projects-root> (see run_pair.projects_root) and recorded with the placeholder, never the local path.
"""
import argparse
import ast
import json
import random
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
repo = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(repo / '.validation-deps'))
import yaml  # noqa: E402
from run_pair import argv_for, projects_root, rmtree  # noqa: E402

COMPARE = {'<': '<=', '<=': '<', '>': '>=', '>=': '>', '==': '!=', '!=': '==', 'is': 'is not', 'is not': 'is', 'in': 'not in', 'not in': 'in'}
BOOL = {'and': 'or', 'or': 'and'}


def candidates(rel, src):
    lines = src.split(b'\n')
    found = []

    def seg(line, a, b):
        return lines[line - 1][a:b]

    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            for i in range(len(node.ops)):
                a, b = operands[i], operands[i + 1]
                if a.end_lineno != b.lineno:
                    continue
                s = seg(a.end_lineno, a.end_col_offset, b.col_offset)
                text = s.strip()
                norm = ' '.join(text.decode(errors='replace').split())
                if norm in COMPARE and b'(' not in s and b')' not in s:
                    start = a.end_col_offset + (len(s) - len(s.lstrip()))
                    found.append((rel, a.end_lineno, start, start + len(text), text.decode(), COMPARE[norm], 'compare'))
        elif isinstance(node, ast.BoolOp):
            for a, b in zip(node.values, node.values[1:]):
                if a.end_lineno != b.lineno:
                    continue
                s = seg(a.end_lineno, a.end_col_offset, b.col_offset)
                m = re.search(rb'\b(and|or)\b', s)
                if m:
                    word = m.group(1).decode()
                    found.append((rel, a.end_lineno, a.end_col_offset + m.start(), a.end_col_offset + m.end(), word, BOOL[word], 'boolop'))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not) and node.lineno == node.operand.lineno:
            s = seg(node.lineno, node.col_offset, node.operand.col_offset)
            if s.strip() == b'not':
                found.append((rel, node.lineno, node.col_offset, node.operand.col_offset, s.decode(), '', 'drop-not'))
        elif isinstance(node, ast.Constant) and node.lineno == node.end_lineno:
            text = seg(node.lineno, node.col_offset, node.end_col_offset).decode(errors='replace')
            if isinstance(node.value, bool):
                found.append((rel, node.lineno, node.col_offset, node.end_col_offset, text, 'False' if node.value else 'True', 'bool'))
            elif isinstance(node.value, int) and text.isdigit() and len(text) <= 4:
                found.append((rel, node.lineno, node.col_offset, node.end_col_offset, text, str(node.value + 1), 'int'))
    return found


def apply(path, c):
    data = path.read_bytes()
    lines = data.split(b'\n')
    line = lines[c[1] - 1]
    assert line[c[2]:c[3]] == c[4].encode(), c
    lines[c[1] - 1] = line[:c[2]] + c[5].encode() + line[c[3]:]
    path.write_bytes(b'\n'.join(lines))
    return data


def run_suite(cmd, cwd):
    t0 = time.time()
    try:
        p = subprocess.run(argv_for(cmd), cwd=cwd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return None, 'timeout', [], time.time() - t0
    out = p.stdout + p.stderr
    failed = int(m.group(1)) if (m := re.search(r'(\d+) failed', out)) else 0
    errors = bool(re.search(r'\d+ errors?\b', out))
    return p.returncode, ('error' if errors else failed), re.findall(r'^FAILED (\S+)', out, re.M), time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--test-command', default='python -m pytest -q -p no:cacheprovider')
    ap.add_argument('--max-tasks', type=int, default=12)
    ap.add_argument('--max-candidates', type=int, default=200)
    ap.add_argument('--seed', type=int, default=17)
    ap.add_argument('--out', default=str(repo / 'research/program/paired-study/tasks'))
    args = ap.parse_args()
    source = Path(projects_root()) / args.repo
    work = Path(tempfile.mkdtemp(prefix='gauntlet-mint-'))
    try:
        subprocess.run(['git', 'clone', '-q', str(source), str(work / 'r')], check=True, capture_output=True)
        wt = work / 'r'
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=wt, capture_output=True, text=True, check=True).stdout.strip()
        rc, failed, _, base_s = run_suite(args.test_command, wt)
        if rc != 0:
            raise SystemExit(f'baseline suite does not pass (rc={rc}, failed={failed}); refusing to mint')
        pool = [c for f in args.files for c in candidates(f, (wt / f).read_bytes())]
        random.Random(args.seed).shuffle(pool)
        out_dir = Path(args.out)
        existing = sorted(out_dir.glob('m[0-9][0-9][0-9]-*.yaml'))
        n = len(existing)
        used_lines, minted, tried = set(), [], 0
        for c in pool[:args.max_candidates]:
            if len(minted) >= args.max_tasks:
                break
            if (c[0], c[1]) in used_lines:
                continue
            tried += 1
            original = apply(wt / c[0], c)
            rc, failed, ids, secs = run_suite(args.test_command, wt)
            (wt / c[0]).write_bytes(original)
            if rc in (None, 0) or failed == 'error' or not (1 <= failed <= 2):
                continue
            used_lines.add((c[0], c[1]))
            n += 1
            stem = Path(c[0]).stem
            task_id = f'm{n:03d}-{args.repo[:12]}-{stem}-L{c[1]}'
            spec = {
                'task_id': task_id, 'repo': f'<projects-root>/{args.repo}', 'base_commit': head, 'answer_commit': head,
                'mutation': {'file': c[0], 'line': c[1], 'col_start': c[2], 'col_end': c[3], 'original': c[4], 'mutated': c[5], 'kind': c[6]},
                'test_files_from_answer': [], 'held_out_files': [], 'held_out_study_files': [], 'setup_copy_from_repo': [],
                'protected_paths': ['tests', 'test'],
                'description': (f'A recent change to {c[0]} broke behavior the test suite covers: {failed} test{"s" if failed > 1 else ""} '
                                f'now fail{"" if failed > 1 else "s"}. Find the defect and restore the intended behavior without changing any test. '
                                f'Local-only; no hosting, no CI.'),
                'test_command': args.test_command, 'failing_tests': ids, 'allowed_paths': [c[0]],
                'difficulty': {'estimate': 'low', 'proxies': [f'one-token defect in {c[0]}', f'{failed} failing test{"s" if failed > 1 else ""} pin it',
                                                              f'suite runs in about {max(1, round(base_s))} seconds']},
                'verifiability': 'deterministic', 'task_class': 'code-fix', 'review_cap': 8,
                'mint': {'minted_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'kind': c[6], 'failing_count': failed,
                         'suite_seconds': round(secs, 1), 'seed': args.seed, 'method': 'tools/paired_study/mint_mutations.py'},
            }
            (out_dir / f'{task_id}.yaml').write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding='utf-8')
            minted.append({'task_id': task_id, 'file': c[0], 'line': c[1], 'kind': c[6], 'original': c[4], 'mutated': c[5], 'failing': failed})
        index = out_dir / 'mutation-index.json'
        prior = json.loads(index.read_text(encoding='utf-8')) if index.exists() else []
        index.write_text(json.dumps(prior + minted, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'repo': args.repo, 'head': head[:10], 'baseline_s': round(base_s, 1), 'candidates': len(pool), 'tried': tried,
                          'minted': len(minted), 'tasks': [m['task_id'] for m in minted], 'model_tokens_used': 0}, indent=2))
    finally:
        rmtree(work)


if __name__ == '__main__':
    main()
