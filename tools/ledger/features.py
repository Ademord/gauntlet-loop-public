"""Phase-0 feature table: aggregate ledger/runs.jsonl into cells and feature contrasts, printing `insufficient`
below the configured threshold instead of a delta. Zero model tokens.

Writes ledger/cells.tsv (difficulty x verifiability x topology) and ledger/feature-usefulness.tsv (per feature:
with vs without). Also flags self-report mismatches (difficulty low but reviews used above 3).
Usage: python tools/ledger/features.py [--config ledger/config.json]
"""
import argparse
import json
import statistics
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
UNKNOWN = 'unknown'
FEATURES = ['evidence_ladder', 'light_topology', 'order_swap', 'delegates', 'team', 'isolation', 'learning', 'retrieval_allowance', 'parallel_critics']


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def median_or_unknown(values):
    vals = [v for v in values if v is not None]
    return statistics.median(vals) if vals else UNKNOWN


def summarize(rows, threshold):
    n = len(rows)
    if n < threshold:
        return {'n': n, 'accepted_rate': 'insufficient', 'median_reviews': 'insufficient', 'median_tokens': 'insufficient'}
    accepted = sum(1 for r in rows if r.get('state') == 'accepted')
    return {
        'n': n,
        'accepted_rate': round(accepted / n, 2),
        'median_reviews': median_or_unknown([num(r['reviews'].get('used')) for r in rows]),
        'median_tokens': median_or_unknown([num(r['cost'].get('subagent_tokens')) for r in rows]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=str(repo / ('ledger/config.local.json' if (repo / 'ledger/config.local.json').exists() else 'ledger/config.json')))
    args = ap.parse_args()
    threshold = json.loads(Path(args.config).read_text(encoding='utf-8')).get('insufficient_below', 3)
    rows = [json.loads(l) for l in (repo / 'ledger/runs.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]

    cells = {}
    for r in rows:
        key = ((r.get('difficulty') or {}).get('estimate', UNKNOWN), r.get('verifiability', UNKNOWN), (r.get('topology') or {}).get('chosen', UNKNOWN))
        cells.setdefault(key, []).append(r)
    lines = ['difficulty\tverifiability\ttopology\tn\taccepted_rate\tmedian_reviews\tmedian_tokens']
    for key in sorted(cells, key=lambda k: tuple(str(x) for x in k)):
        s = summarize(cells[key], threshold)
        lines.append('\t'.join(str(x) for x in (*key, s['n'], s['accepted_rate'], s['median_reviews'], s['median_tokens'])))
    (repo / 'ledger/cells.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    flines = ['feature\tn_with\tn_without\tn_unknown\taccepted_with\taccepted_without\tdelta_pp\tmedian_reviews_with\tmedian_reviews_without\tdelta_reviews']
    for f in FEATURES:
        with_, without, unk = [], [], 0
        for r in rows:
            fe = r.get('features_enabled', UNKNOWN)
            if fe == UNKNOWN or not isinstance(fe, list):
                unk += 1
            elif f in fe:
                with_.append(r)
            else:
                without.append(r)
        sw, so = summarize(with_, threshold), summarize(without, threshold)
        if sw['accepted_rate'] == 'insufficient' or so['accepted_rate'] == 'insufficient':
            delta_pp = delta_reviews = 'insufficient'
        else:
            delta_pp = round((sw['accepted_rate'] - so['accepted_rate']) * 100)
            delta_reviews = (sw['median_reviews'] - so['median_reviews']) if UNKNOWN not in (sw['median_reviews'], so['median_reviews']) else UNKNOWN
        flines.append('\t'.join(str(x) for x in (f, len(with_), len(without), unk, sw['accepted_rate'], so['accepted_rate'], delta_pp, sw['median_reviews'], so['median_reviews'], delta_reviews)))
    (repo / 'ledger/feature-usefulness.tsv').write_text('\n'.join(flines) + '\n', encoding='utf-8')

    mismatches = [r['run_id'] for r in rows if (r.get('difficulty') or {}).get('estimate') == 'low' and (num(r['reviews'].get('used')) or 0) > 3]
    print(json.dumps({'runs': len(rows), 'cells': len(cells), 'features': len(FEATURES), 'insufficient_cells': sum(1 for k in cells if len(cells[k]) < threshold), 'self_report_mismatches': mismatches, 'model_tokens_used': 0}))


if __name__ == '__main__':
    main()
