"""Mint medium-difficulty paired-study tasks by excision (backlog B-027). Zero model tokens.

A mutation task is one flipped token: the first look at flag F1 found every compact arm accepting on its first
review, so the revision loop never fired and the flag measured nothing but exploration overhead. This script mints
the next class up. It removes a whole function body, leaving the signature, the decorators and the docstring, and
replacing the body with a raise. The builder must reimplement behavior that several tests pin, which is work a
first review can plausibly reject.

Kept only if the excision makes at least `--min-failing` tests fail with no collection error, so the task has a
deterministic oracle like the mutation class. The answer is the original commit; history is orphaned by the runner,
so the removed body is not reachable from the arm's clone.

Usage:
  python tools/paired_study/mint_excisions.py --repo intelligence-pipeline --files evaluate.py validation.py schema.py
         [--min-body-lines 10] [--max-body-lines 40] [--min-failing 3] [--max-tasks 8] [--max-candidates 30] [--seed 29]
Writes research/program/paired-study/tasks/x<NNN>-*.yaml and tasks/excision-index.json.
"""
import argparse
import ast
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
repo = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(repo / '.validation-deps'))
import yaml  # noqa: E402
from mint_mutations import run_suite  # noqa: E402
from run_pair import projects_root, rmtree  # noqa: E402

PLACEHOLDER = 'raise NotImplementedError("This function was removed for a repair task; reimplement it.")'


def body_span(node, lines):
    """1-based [start, end] line span of a function body, docstring excluded, trailing in-body comments included."""
    body = node.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if not body:
        return None
    start, end = body[0].lineno, body[-1].end_lineno
    def_indent = node.col_offset
    while end < len(lines):
        nxt = lines[end]  # the line after `end`, since `lines` is 0-based
        stripped = nxt.strip()
        if not stripped:
            break
        if not stripped.startswith('#'):
            break
        if (len(nxt) - len(nxt.lstrip())) <= def_indent:
            break
        end += 1
    return start, end


def candidates(rel, src, min_body_lines):
    lines = src.split('\n')
    tree = ast.parse(src)
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        span = body_span(node, lines)
        if not span:
            continue
        start, end = span
        if end - start + 1 < min_body_lines:
            continue
        owner = parents.get(node)
        qual = f'{owner.name}.{node.name}' if isinstance(owner, ast.ClassDef) else node.name
        has_doc = bool(node.body and isinstance(node.body[0], ast.Expr)
                       and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str))
        found.append({'file': rel, 'qualname': qual, 'name': node.name, 'start_line': start, 'end_line': end,
                      'body_lines': end - start + 1, 'has_docstring': has_doc,
                      'indent': len(lines[start - 1]) - len(lines[start - 1].lstrip())})
        found[-1]['body_sha256'] = body_sha256(lines, found[-1])
    return found


def apply(path, c):
    """Replace the body span with the placeholder. Returns the original text for restoration."""
    original = path.read_text(encoding='utf-8')
    lines = original.split('\n')
    lines[c['start_line'] - 1:c['end_line']] = [' ' * c['indent'] + PLACEHOLDER]
    path.write_text('\n'.join(lines), encoding='utf-8')
    return original


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--files', nargs='+', required=True)
    ap.add_argument('--test-command', default='python -m pytest -q -p no:cacheprovider')
    ap.add_argument('--min-body-lines', type=int, default=10)
    ap.add_argument('--max-body-lines', type=int, default=40, help='exclude bodies larger than this; the big reporting '
                    'functions are pinned by exact-output tests and reimplementing them is guesswork, not repair')
    ap.add_argument('--min-failing', type=int, default=3)
    ap.add_argument('--max-tasks', type=int, default=8)
    ap.add_argument('--max-candidates', type=int, default=30)
    ap.add_argument('--seed', type=int, default=29)
    ap.add_argument('--out', default=str(repo / 'research/program/paired-study/tasks'))
    ap.add_argument('--dry-run', action='store_true', help='list candidates and their sizes; run no suites')
    args = ap.parse_args()
    source = Path(projects_root()) / args.repo
    work = Path(tempfile.mkdtemp(prefix='gauntlet-excise-'))
    try:
        subprocess.run(['git', 'clone', '-q', str(source), str(work / 'r')], check=True, capture_output=True)
        wt = work / 'r'
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=wt, capture_output=True, text=True, check=True).stdout.strip()
        pool = [c for f in args.files for c in candidates(f, (wt / f).read_text(encoding='utf-8'), args.min_body_lines)
                if c['body_lines'] <= args.max_body_lines]
        random.Random(args.seed).shuffle(pool)
        if args.dry_run:
            listed = sorted(((c['body_lines'], c['file'], c['qualname'], c['has_docstring']) for c in pool), reverse=True)
            print(json.dumps({'candidates': len(pool), 'by_size': listed[:40]}, indent=2))
            return
        rc, failed, _, base_s = run_suite(args.test_command, wt)
        if rc != 0:
            raise SystemExit(f'baseline suite does not pass (rc={rc}, failed={failed}); refusing to mint')
        out_dir = Path(args.out)
        index_path = out_dir / 'excision-index.json'
        prior = json.loads(index_path.read_text(encoding='utf-8')) if index_path.exists() else []
        used = {(e['file'], e['qualname']) for e in prior}
        n = len(sorted(out_dir.glob('x[0-9][0-9][0-9]-*.yaml')))
        minted, tried, rejected = [], 0, []
        for c in pool[:args.max_candidates]:
            if len(minted) >= args.max_tasks:
                break
            if (c['file'], c['qualname']) in used:
                continue
            tried += 1
            original = apply(wt / c['file'], c)
            rc, failed, ids, secs = run_suite(args.test_command, wt)
            (wt / c['file']).write_text(original, encoding='utf-8')
            if rc in (None, 0) or failed == 'error' or failed < args.min_failing:
                rejected.append({'qualname': c['qualname'],
                                 'why': 'suite still passes' if rc == 0 else
                                        ('collection error' if failed == 'error' else f'only {failed} failing')})
                continue
            used.add((c['file'], c['qualname']))
            n += 1
            task_id = f'x{n:03d}-{args.repo[:12]}-{Path(c["file"]).stem}-{c["name"]}'
            doc_clause = ' and docstring are' if c['has_docstring'] else ' is'
            spec = {
                'task_id': task_id, 'repo': f'<projects-root>/{args.repo}', 'base_commit': head, 'answer_commit': head,
                'excision': {'file': c['file'], 'start_line': c['start_line'], 'end_line': c['end_line'],
                             'indent': c['indent'], 'placeholder': PLACEHOLDER, 'qualname': c['qualname'],
                             'body_sha256': c['body_sha256']},
                'test_files_from_answer': [], 'held_out_files': [], 'held_out_study_files': [], 'setup_copy_from_repo': [],
                'protected_paths': ['tests', 'test'],
                'description': (f'`{c["qualname"]}` in {c["file"]} has been removed: its body now raises NotImplementedError, and '
                                f'{failed} tests fail. Reimplement it so the whole suite passes. Its signature{doc_clause} '
                                f'unchanged and the tests state the behavior; do not change any test. '
                                f'Local-only; no hosting, no CI.'),
                'test_command': args.test_command, 'failing_tests': ids, 'allowed_paths': [c['file']],
                'difficulty': {'estimate': 'medium',
                               'proxies': [f'{c["body_lines"]} lines of removed implementation, not a single token',
                                           f'{failed} failing tests pin the behavior',
                                           'the docstring states intent; the tests state the contract' if c['has_docstring']
                                           else 'no docstring: the tests are the only statement of the contract',
                                           f'suite runs in about {max(1, round(base_s))} seconds']},
                'verifiability': 'deterministic', 'task_class': 'code-fix', 'review_cap': 8,
                'mint': {'minted_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'kind': 'excision',
                         'failing_count': failed, 'body_lines': c['body_lines'], 'suite_seconds': round(secs, 1),
                         'seed': args.seed, 'method': 'tools/paired_study/mint_excisions.py',
                         'size_band': [args.min_body_lines, args.max_body_lines]},
            }
            (out_dir / f'{task_id}.yaml').write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding='utf-8')
            minted.append({'task_id': task_id, 'file': c['file'], 'qualname': c['qualname'], 'body_lines': c['body_lines'],
                           'failing': failed, 'start_line': c['start_line'], 'end_line': c['end_line']})
        index_path.write_text(json.dumps(prior + minted, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'repo': args.repo, 'head': head[:10], 'baseline_s': round(base_s, 1), 'candidates': len(pool),
                          'tried': tried, 'minted': len(minted), 'tasks': [m['task_id'] for m in minted],
                          'rejected': rejected, 'model_tokens_used': 0}, indent=2))
    finally:
        rmtree(work)


if __name__ == '__main__':
    main()
