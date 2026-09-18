"""Phase-0 monthly report: a Markdown file a person reads in ten minutes. Zero model tokens.

Reads ledger/runs.jsonl, ledger/unrecorded.jsonl, ledger/cells.tsv, ledger/feature-usefulness.tsv and the
program backlog; writes ledger/report-<YYYY-MM>.md. Every number is a count from the records; no inference.
Usage: python tools/ledger/report.py [--month YYYY-MM]
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
UNKNOWN = 'unknown'


def read_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()] if path.exists() else []


def tsv_to_md(path):
    if not path.exists():
        return '(missing)'
    lines = [l.split('\t') for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
    if not lines:
        return '(empty)'
    out = ['| ' + ' | '.join(lines[0]) + ' |', '| ' + ' | '.join('---' for _ in lines[0]) + ' |']
    out += ['| ' + ' | '.join(l) + ' |' for l in lines[1:]]
    return '\n'.join(out)


def fmt(v):
    if isinstance(v, dict):
        return '; '.join(f'{k}={fmt(x)}' for k, x in v.items()) or UNKNOWN
    if isinstance(v, list):
        return ', '.join(str(x) for x in v) or 'none'
    return str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--month', default=datetime.now(timezone.utc).strftime('%Y-%m'))
    args = ap.parse_args()
    runs = read_jsonl(repo / 'ledger/runs.jsonl')
    unrecorded = read_jsonl(repo / 'ledger/unrecorded.jsonl')
    backlog = (repo / 'research/program/backlog.md')
    candidates = sum(1 for l in backlog.read_text(encoding='utf-8').splitlines() if l.startswith('| B-') and '| candidate |' in l) if backlog.exists() else 0
    lesson_files = [p for p in repo.rglob('lessons/*.md') if 'utility_ledger' in p.read_text(encoding='utf-8', errors='replace')]

    unknown_counts = {}
    for r in runs:
        for k in ('difficulty', 'verifiability', 'topology', 'task_class', 'features_enabled'):
            v = r.get(k, UNKNOWN)
            if v == UNKNOWN or (isinstance(v, dict) and v.get('estimate', v.get('chosen')) == UNKNOWN):
                unknown_counts[k] = unknown_counts.get(k, 0) + 1
        if r.get('cost', {}).get('subagent_tokens') == UNKNOWN:
            unknown_counts['subagent_tokens'] = unknown_counts.get('subagent_tokens', 0) + 1

    md = [f'# Gauntlet run ledger report, {args.month}', '',
          f'Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} by `tools/ledger/report.py` from committed records. Zero model tokens. Counts only; no causal claim.', '',
          '## Totals', '',
          f'- Recorded runs: {len(runs)} (by shape: ' + ', '.join(f'{s}={sum(1 for r in runs if r["source_shape"] == s)}' for s in sorted({r["source_shape"] for r in runs})) + ')',
          f'- Gauntlet directories with no machine-readable milestone: {len(unrecorded)} (the denominator; a missing row is a row)',
          f'- Fields unknown across recorded runs: ' + (', '.join(f'{k}={v}' for k, v in sorted(unknown_counts.items())) or 'none'),
          f'- Lesson files in the v5 schema found: {len(lesson_files)}',
          f'- Program backlog rows in `candidate` status: {candidates}', '',
          '## Runs', '',
          '| project | run | skill | state | difficulty | verifiability | topology | reviews used | subagent tokens | wall clock s |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in runs:
        md.append('| ' + ' | '.join(str(x) for x in (r['project'], r['run_id'], r['skill_version'], r['state'], (r.get('difficulty') or {}).get('estimate', UNKNOWN), r.get('verifiability', UNKNOWN), (r.get('topology') or {}).get('chosen', UNKNOWN), r['reviews'].get('used', UNKNOWN), r['cost'].get('subagent_tokens', UNKNOWN), r['cost'].get('wall_clock_s', UNKNOWN))) + ' |')
    md += ['', '## Cells (difficulty x verifiability x topology)', '', tsv_to_md(repo / 'ledger/cells.tsv'), '',
           '## Feature contrasts (observational, confounded; `insufficient` below the threshold in ledger/config.json)', '', tsv_to_md(repo / 'ledger/feature-usefulness.tsv'), '',
           '## Unrecorded gauntlet directories', '']
    for u in unrecorded:
        md.append(f'- `{u.get("path")}` ({u.get("project")}): {u.get("note")}; prose files: {fmt(u.get("prose_files", []))}; subdirs: {fmt(u.get("subdirs", []))}')
    md += ['', '## What to do with this', '',
           '1. Every run that is not in the Runs table above is a recording defect, not a data point. Add its milestone line in the v5 shape (execution contract, milestone summary) if the run record still exists; otherwise leave it unrecorded.',
           '2. Cells and contrasts marked `insufficient` stay that way until the threshold is met. Do not read a number from a cell with fewer runs than the threshold.',
           '3. Self-report mismatches (difficulty `low` with more than three reviews) are printed by `tools/ledger/features.py`; look at them, do not score them.',
           '4. Proposals go to `research/program/backlog.md` as `candidate` rows and are adopted only through the skill\'s bounded workflow-improvement process, by the owner.']
    out = repo / f'ledger/report-{args.month}.md'
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(out.relative_to(repo)), 'recorded_runs': len(runs), 'unrecorded_dirs': len(unrecorded), 'model_tokens_used': 0}))


if __name__ == '__main__':
    main()
