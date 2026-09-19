"""Write the human-readable look report for one flag from results.jsonl. Zero model tokens, no interpretation.

Every number comes from the recorded rows; the exact tests and bootstrap intervals come from analyze_pairs, which
is the file committed before the first pair ran. Pilot rows and harness failures are listed but never pooled.

Usage: python tools/paired_study/report_pairs.py --flag F1 [--out research/program/paired-study/look-F1.md]
"""
import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
repo = HERE.parents[1]
sys.path.insert(0, str(HERE))
from analyze_pairs import analyze  # noqa: E402

ARMS = {'A': 'light', 'B': 'compact'}


def fmt(v, nd=0):
    if v is None:
        return 'unknown'
    if isinstance(v, float):
        return f'{v:.2f}' if nd else f'{v:,.0f}'
    if isinstance(v, int):
        return f'{v:,}'
    return str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--flag', default='F1')
    ap.add_argument('--out')
    ap.add_argument('--alpha', type=float, default=0.05)
    ap.add_argument('--looks', type=int, default=3)
    args = ap.parse_args()
    results_path = repo / 'research/program/paired-study/results.jsonl'
    rows = [json.loads(l) for l in results_path.read_text(encoding='utf-8').splitlines() if l.strip()]
    flag_rows = [r for r in rows if r.get('flag') == args.flag]
    counted = [r for r in flag_rows if not r.get('pilot') and not r.get('harness_failure')]
    pilots = [r for r in flag_rows if r.get('pilot')]
    failures = [r for r in flag_rows if r.get('harness_failure')]
    by_task = {}
    for r in counted:
        by_task.setdefault(r['task_id'], {})[r['arm']] = r
    complete = {t: a for t, a in by_task.items() if 'A' in a and 'B' in a}
    stats = analyze(rows, args.flag, args.alpha, args.looks)

    md = [f'# Paired study, flag {args.flag}: look at {len(complete)} pairs', '',
          f'Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} by `tools/paired_study/report_pairs.py` from '
          f'`results.jsonl`. Arm A is the light topology (one bounded build, one independent evidence-based review, no preference '
          f'loop); arm B is compact (build, independent critic, revise). Everything else about the two arms is identical, including '
          f'the model. Acceptance is an independent rerun of the suite after the protected tests are restored, with no file changed '
          f'outside the allowed paths.', '',
          f'- Counted pairs: {len(complete)}. Pilot rows excluded: {len(pilots)}. Harness-failure rows excluded: {len(failures)}.', '']
    if complete:
        md += ['## Per task', '',
               '| Task | A accepted | B accepted | held-out A/B | reviews A/B | turns A/B | tokens A/B | cost A/B | seconds A/B |',
               '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        for task in sorted(complete):
            a, b = complete[task]['A'], complete[task]['B']
            md.append(f"| {task} | {'yes' if a['accepted'] else 'no'} | {'yes' if b['accepted'] else 'no'} "
                      f"| {a.get('held_out_passed')}/{b.get('held_out_passed')} | {fmt(a.get('reviews_used'))}/{fmt(b.get('reviews_used'))} "
                      f"| {fmt(a.get('num_turns'))}/{fmt(b.get('num_turns'))} | {fmt(a.get('total_tokens'))}/{fmt(b.get('total_tokens'))} "
                      f"| ${fmt(a.get('cost_usd'), 2)}/${fmt(b.get('cost_usd'), 2)} | {fmt(a.get('wall_clock_s'))}/{fmt(b.get('wall_clock_s'))} |")
        md.append('')
        md += ['## Totals', '', '| Measure | A, light | B, compact |', '| --- | --- | --- |']
        for label, key, nd in (('accepted', 'accepted', 0), ('median reviews', 'reviews_used', 0), ('median turns', 'num_turns', 0),
                               ('median tokens', 'total_tokens', 0), ('total cost', 'cost_usd', 2), ('median seconds', 'wall_clock_s', 0)):
            va = [complete[t]['A'].get(key) for t in complete]
            vb = [complete[t]['B'].get(key) for t in complete]
            if key == 'accepted':
                md.append(f'| accepted | {sum(1 for x in va if x)} of {len(va)} | {sum(1 for x in vb if x)} of {len(vb)} |')
            elif key == 'cost_usd':
                md.append(f'| total cost | ${sum(x or 0 for x in va):.2f} | ${sum(x or 0 for x in vb):.2f} |')
            else:
                na = [x for x in va if isinstance(x, (int, float))]
                nb = [x for x in vb if isinstance(x, (int, float))]
                md.append(f'| {label} | {fmt(statistics.median(na)) if na else "unknown"} | {fmt(statistics.median(nb)) if nb else "unknown"} |')
        md.append('')
    md += ['## Paired tests', '',
           'From `analyze_pairs.py`, committed before the first pair ran. The per-look threshold is the alpha split across the '
           f'planned looks: {stats["alpha_per_look"]:.4f}. A difference is reported as detected only below that threshold.', '',
           '```json', json.dumps(stats, indent=2), '```', '',
           '## What this does and does not show', '',
           '- Tasks are one-token defects and small repairs in one public Python repository, run on one model. Nothing here '
           'generalizes to harder work, other languages, or other models.',
           '- Acceptance is binary and every task has a deterministic oracle, so the comparison is about cost and effort far more '
           'than about quality.',
           '- The planned first look is thirty pairs; a smaller look is reported for what it is.',
           '- Cost figures are the transcript\'s own `total_cost_usd`, which is API-equivalent pricing, not what a subscription is '
           'billed.']
    out = Path(args.out) if args.out else repo / f'research/program/paired-study/look-{args.flag}.md'
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')
    shown = str(out.relative_to(repo)) if out.is_relative_to(repo) else str(out)
    print(json.dumps({'report': shown, 'pairs': len(complete), 'pilots_excluded': len(pilots),
                      'harness_failures_excluded': len(failures), 'reading': stats['reading']}, indent=2))


if __name__ == '__main__':
    main()
