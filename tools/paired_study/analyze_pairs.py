"""Paired analysis for the phase-2 study: exact tests and bootstrap intervals in pure Python. Zero model tokens.

Input: a JSONL of per-run results, one object per (task_id, flag, arm):
  {"task_id": "...", "flag": "F1", "arm": "A", "accepted": true, "reviews_used": 3, "subagent_tokens": 210000,
   "wall_clock_s": 900, "harness_failure": false}
Usage:
  python tools/paired_study/analyze_pairs.py --results results.jsonl [--flag F1] [--alpha 0.05 --looks 3]
  python tools/paired_study/analyze_pairs.py --selftest
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path


def binom_two_sided(k, n, p=0.5):
    """Exact two-sided binomial p-value (sum of probabilities <= P(k))."""
    if n == 0:
        return 1.0
    probs = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    pk = probs[k]
    return min(1.0, sum(x for x in probs if x <= pk + 1e-12))


def sign_test(diffs):
    nonzero = [d for d in diffs if d != 0]
    pos = sum(1 for d in nonzero if d > 0)
    return {'n_nonzero': len(nonzero), 'positive': pos, 'p_value': binom_two_sided(pos, len(nonzero))}


def bootstrap_mean_ci(diffs, resamples=10000, seed=17):
    if not diffs:
        return {'mean': None, 'ci95': [None, None]}
    rng = random.Random(seed)
    means = []
    n = len(diffs)
    for _ in range(resamples):
        sample = [diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    return {'mean': sum(diffs) / n, 'ci95': [means[int(0.025 * resamples)], means[int(0.975 * resamples) - 1]]}


def analyze(results, flag, alpha, looks):
    rows = [r for r in results if r.get('flag') == flag]
    by_task = {}
    for r in rows:
        by_task.setdefault(r['task_id'], {})[r['arm']] = r
    complete, excluded = {}, []
    for task, arms in by_task.items():
        if 'A' in arms and 'B' in arms and not arms['A'].get('harness_failure') and not arms['B'].get('harness_failure'):
            complete[task] = arms
        else:
            excluded.append(task)
    n = len(complete)
    per_look_alpha = alpha / looks
    out = {'flag': flag, 'pairs': n, 'excluded_pairs': excluded, 'alpha_per_look': per_look_alpha}
    # acceptance: McNemar exact on discordant pairs
    a_only = sum(1 for t in complete.values() if t['A']['accepted'] and not t['B']['accepted'])
    b_only = sum(1 for t in complete.values() if t['B']['accepted'] and not t['A']['accepted'])
    out['acceptance'] = {'accepted_A': sum(1 for t in complete.values() if t['A']['accepted']),
                         'accepted_B': sum(1 for t in complete.values() if t['B']['accepted']),
                         'discordant_A_only': a_only, 'discordant_B_only': b_only,
                         'p_value': binom_two_sided(a_only, a_only + b_only),
                         'significant_at_look': binom_two_sided(a_only, a_only + b_only) < per_look_alpha}
    for metric in ('reviews_used', 'subagent_tokens', 'wall_clock_s'):
        diffs = [t['A'][metric] - t['B'][metric] for t in complete.values()
                 if isinstance(t['A'].get(metric), (int, float)) and isinstance(t['B'].get(metric), (int, float))]
        st = sign_test(diffs)
        out[metric] = {'pairs_with_values': len(diffs), 'A_minus_B': bootstrap_mean_ci(diffs), 'sign_test': st,
                       'significant_at_look': st['p_value'] < per_look_alpha if diffs else False}
    out['reading'] = ('no difference detected' if not out['acceptance']['significant_at_look'] and not any(out[m]['significant_at_look'] for m in ('reviews_used', 'subagent_tokens', 'wall_clock_s'))
                      else 'a primary outcome crossed the per-look threshold; read the direction from the estimates')
    return out


def selftest():
    rng = random.Random(3)
    results = []
    for i in range(30):
        base_reviews = rng.randint(2, 6)
        # synthetic truth: arm A uses one fewer review on average, same acceptance
        ra = max(1, base_reviews - 1 + rng.choice([0, 0, 1, -1]))
        rb = base_reviews + rng.choice([0, 0, 1])
        acc = rng.random() < 0.9
        for arm, rv in (('A', ra), ('B', rb)):
            results.append({'task_id': f't{i}', 'flag': 'F1', 'arm': arm, 'accepted': acc, 'reviews_used': rv,
                            'subagent_tokens': rv * 60000 + rng.randint(-5000, 5000), 'wall_clock_s': rv * 300, 'harness_failure': False})
    results.append({'task_id': 'broken', 'flag': 'F1', 'arm': 'A', 'accepted': False, 'reviews_used': 0, 'harness_failure': True})
    out = analyze(results, 'F1', 0.05, 3)
    assert out['pairs'] == 30 and out['excluded_pairs'] == ['broken'], out
    assert out['reviews_used']['A_minus_B']['mean'] < 0, 'direction should be negative (A fewer reviews)'
    assert out['reviews_used']['sign_test']['p_value'] < 0.05 / 3, 'planted effect should be detected at n=30'
    assert out['acceptance']['discordant_A_only'] == 0 and out['acceptance']['discordant_B_only'] == 0
    null = [dict(r, reviews_used=3, subagent_tokens=100000, wall_clock_s=600) for r in results if not r['harness_failure']]
    out_null = analyze(null, 'F1', 0.05, 3)
    assert out_null['reading'] == 'no difference detected', out_null['reading']
    print(json.dumps({'selftest': 'passed', 'planted_effect_mean_diff': round(out['reviews_used']['A_minus_B']['mean'], 2), 'p': out['reviews_used']['sign_test']['p_value']}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results')
    ap.add_argument('--flag', default='F1')
    ap.add_argument('--alpha', type=float, default=0.05)
    ap.add_argument('--looks', type=int, default=3)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    results = [json.loads(l) for l in Path(args.results).read_text(encoding='utf-8').splitlines() if l.strip()]
    print(json.dumps(analyze(results, args.flag, args.alpha, args.looks), indent=2))


if __name__ == '__main__':
    sys.exit(main())
