"""Run several pairs one after another for one flag, skipping pairs that already have counted rows.

This script itself costs nothing; each pair it runs spends model tokens. It stops on a preflight failure (a dead
CLI login) and after two consecutive pairs whose arms failed for harness reasons, so a broken setup cannot burn a
whole series. Pilot rows and harness-failure rows do not count as done, so a pair with only those is run again.

Usage:
  python tools/paired_study/run_series.py --flag F1 --dry-run
  python tools/paired_study/run_series.py --flag F1 [--only m0 --only t002] [--max-pairs 13] [--model claude-sonnet-5]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
RESULTS = repo / 'research/program/paired-study/results.jsonl'


def counted_rows():
    done = {}
    if RESULTS.exists():
        for line in RESULTS.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get('pilot') or r.get('harness_failure'):
                continue
            done.setdefault((r['task_id'], r['flag']), set()).add(r['arm'])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--flag', default='F1')
    ap.add_argument('--only', action='append', default=[], help='substring filter on the task id; repeatable')
    ap.add_argument('--max-pairs', type=int, default=0)
    ap.add_argument('--model', default='claude-sonnet-5')
    ap.add_argument('--timeout-min', type=int, default=40)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    pairs_root = repo / 'research/program/paired-study/pairs'
    pairs = sorted(p for p in pairs_root.glob(f'*/{args.flag}') if p.is_dir())
    if args.only:
        pairs = [p for p in pairs if any(o in p.parent.name for o in args.only)]
    done = counted_rows()
    todo = [p for p in pairs if len(done.get((p.parent.name, args.flag), set())) < 2]
    if args.max_pairs:
        todo = todo[:args.max_pairs]
    print(json.dumps({'flag': args.flag, 'pairs_found': len(pairs), 'already_counted': len(pairs) - len([p for p in pairs if len(done.get((p.parent.name, args.flag), set())) < 2]),
                      'to_run': [p.parent.name for p in todo], 'model': args.model}, indent=2), flush=True)
    if args.dry_run:
        return 0
    consecutive_failures = 0
    for i, pair in enumerate(todo, 1):
        t0 = time.time()
        print(f'--- [{i}/{len(todo)}] {pair.parent.name}', flush=True)
        proc = subprocess.run([sys.executable, str(repo / 'tools/paired_study/run_pair.py'), '--pair', str(pair), '--execute',
                               '--model', args.model, '--timeout-min', str(args.timeout_min)], capture_output=True, text=True)
        print(proc.stdout.strip(), flush=True)
        if proc.returncode == 3:
            print('PREFLIGHT FAILED: stopping the series.', file=sys.stderr)
            return 3
        rows = [json.loads(l) for l in RESULTS.read_text(encoding='utf-8').splitlines() if l.strip()]
        last = [r for r in rows if r['task_id'] == pair.parent.name and r['flag'] == args.flag][-2:]
        failed = any(r.get('harness_failure') for r in last) or len(last) < 2
        consecutive_failures = consecutive_failures + 1 if failed else 0
        print(json.dumps({'pair': pair.parent.name, 'minutes': round((time.time() - t0) / 60, 1),
                          'cost_usd': round(sum(r.get('cost_usd') or 0 for r in last), 2),
                          'accepted': [r.get('accepted') for r in last], 'harness_failure': failed}), flush=True)
        if consecutive_failures >= 2:
            print('Two consecutive pairs failed for harness reasons: stopping the series.', file=sys.stderr)
            return 4
    return 0


if __name__ == '__main__':
    sys.exit(main())
