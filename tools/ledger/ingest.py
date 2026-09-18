"""Phase-0 ledger ingest: walk project roots for gauntlet run records and normalize them to ledger/SCHEMA.md.

Zero model tokens. Reads runs.jsonl files in three known shapes (the v5 milestone line and two earlier project-specific shapes, alh and gym),
records directories that have no machine-readable milestone as `unrecorded`, and writes:
  ledger/runs.jsonl        one normalized row per run (deduplicated by project + run_id)
  ledger/unrecorded.jsonl  one row per gauntlet directory without a runs.jsonl
Usage: python tools/ledger/ingest.py [--config ledger/config.json]
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
UNKNOWN = 'unknown'


def load_config(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def find_gauntlet_dirs(root, names, excludes, max_depth):
    root = Path(root)
    found = []
    if not root.exists():
        return found

    def walk(d, depth):
        if depth > max_depth:
            return
        try:
            children = sorted(p for p in d.iterdir() if p.is_dir())
        except (PermissionError, OSError):
            return
        for c in children:
            if c.name in excludes:
                continue
            if c.name in names:
                found.append(c)
                continue
            walk(c, depth + 1)

    walk(root, 1)
    return found


def parse_wall_clock(text):
    """Return seconds from strings like 'about 2 h 25 min' or 'PT1H', else unknown."""
    if not isinstance(text, str):
        return UNKNOWN
    m = re.search(r'(\d+)\s*h(?:ours?)?\s*(\d+)?\s*(?:min)?', text)
    if m:
        return int(m.group(1)) * 3600 + (int(m.group(2)) * 60 if m.group(2) else 0)
    m = re.search(r'(\d+)\s*min', text)
    if m:
        return int(m.group(1)) * 60
    return UNKNOWN


def map_v5(rec, project, source):
    pieces = rec.get('pieces', {}) or {}
    per_piece = {k: v.get('reviews_used', UNKNOWN) for k, v in pieces.items()} if isinstance(pieces, dict) else UNKNOWN
    advisory = sum(v.get('advisory_only_reviews', 0) or 0 for v in pieces.values()) if isinstance(pieces, dict) else UNKNOWN
    reviews = rec.get('reviews', {}) or {}
    telemetry = rec.get('telemetry', {}) or {}
    tokens = telemetry.get('subagent_tokens_harness_reported', UNKNOWN)
    if isinstance(tokens, dict):
        tokens = sum(v for v in tokens.values() if isinstance(v, int))
    timing = rec.get('timing', {}) or {}
    wall = timing.get('wall_clock_minutes_approx', UNKNOWN)
    wall_s = wall * 60 if isinstance(wall, (int, float)) else UNKNOWN
    models = reviews.get('per_review_models', UNKNOWN)
    return {
        'run_id': rec.get('run_id', UNKNOWN), 'project': project, 'source_path': source, 'source_shape': 'v5',
        'skill_version': rec.get('skill_version_governing_run', rec.get('skill_version', UNKNOWN)),
        'state': rec.get('state', UNKNOWN),
        'difficulty': rec.get('difficulty', {'estimate': UNKNOWN, 'proxies': []}),
        'verifiability': rec.get('verifiability', UNKNOWN),
        'topology': {'chosen': (rec.get('topology') or {}).get('chosen', UNKNOWN), 'reason': (rec.get('topology') or {}).get('reason', UNKNOWN)},
        'task_class': rec.get('task_class', UNKNOWN),
        'features_enabled': rec.get('features_enabled', UNKNOWN),
        'reviews': {'used': reviews.get('run_used', UNKNOWN), 'per_piece': per_piece, 'advisory_only': advisory},
        'models': {'lead': UNKNOWN, 'builders': UNKNOWN, 'critics': models},
        'cost': {'subagent_tokens': tokens, 'wall_clock_s': wall_s},
        'lessons_retrieved': rec.get('lessons_retrieved', []),
        'later_defects': rec.get('later_defects', 'not assessed'),
        'holds_open': rec.get('holds_open', []),
    }


def map_alh(rec, project, source):
    return {
        'run_id': rec.get('run', UNKNOWN), 'project': project, 'source_path': source, 'source_shape': 'alh',
        'skill_version': rec.get('skill', UNKNOWN), 'state': rec.get('state', UNKNOWN),
        'difficulty': {'estimate': UNKNOWN, 'proxies': []}, 'verifiability': UNKNOWN,
        'topology': {'chosen': UNKNOWN, 'reason': UNKNOWN}, 'task_class': UNKNOWN, 'features_enabled': UNKNOWN,
        'reviews': {'used': rec.get('reviewCount', UNKNOWN), 'per_piece': UNKNOWN, 'advisory_only': UNKNOWN},
        'models': {'lead': UNKNOWN, 'builders': UNKNOWN, 'critics': UNKNOWN},
        'cost': {'subagent_tokens': UNKNOWN, 'wall_clock_s': UNKNOWN},
        'lessons_retrieved': [], 'later_defects': rec.get('laterDefects', 'not assessed'), 'holds_open': rec.get('holds', []),
        'raw': rec,
    }


def map_gym(rec, project, source):
    models = rec.get('models', {}) or {}
    return {
        'run_id': rec.get('task_id', UNKNOWN), 'project': project, 'source_path': source, 'source_shape': 'gym',
        'skill_version': rec.get('workflow', UNKNOWN),
        'state': 'accepted' if rec.get('pieces_won') and not rec.get('pieces_parked_budget') and not rec.get('pieces_blocked') else UNKNOWN,
        'difficulty': {'estimate': UNKNOWN, 'proxies': []}, 'verifiability': UNKNOWN,
        'topology': {'chosen': rec.get('tier', UNKNOWN), 'reason': UNKNOWN}, 'task_class': UNKNOWN, 'features_enabled': UNKNOWN,
        'reviews': {'used': sum(v for v in (rec.get('rounds_per_piece') or {}).values() if isinstance(v, int)) if rec.get('rounds_per_piece') else UNKNOWN,
                    'per_piece': rec.get('rounds_per_piece', UNKNOWN), 'advisory_only': UNKNOWN},
        'models': {'lead': models.get('lead', UNKNOWN), 'builders': models.get('builders', UNKNOWN), 'critics': models.get('critics', UNKNOWN)},
        'cost': {'subagent_tokens': rec.get('subagent_tokens_total', UNKNOWN), 'wall_clock_s': parse_wall_clock(rec.get('wall_time'))},
        'lessons_retrieved': [], 'later_defects': 'not assessed' if rec.get('defects_found_next_7_days') is None else rec.get('defects_found_next_7_days'),
        'holds_open': [], 'raw': rec,
    }


def detect_shape(rec):
    if 'run_id' in rec and 'difficulty' in rec:
        return 'v5'
    if 'run' in rec and 'reviewCount' in rec:
        return 'alh'
    if 'task_id' in rec and 'rounds_per_piece' in rec:
        return 'gym'
    return None


MAPPERS = {'v5': map_v5, 'alh': map_alh, 'gym': map_gym}


def ingest_dir(gdir, project, rows, unrecorded, now):
    runs_file = gdir / 'runs.jsonl'
    prose = [n for n in ('PROGRESS.md', 'LOG.md', 'status.json', 'progress.md', 'STOPPING.md') if (gdir / n).exists()]
    subdirs = sorted(p.name for p in gdir.iterdir() if p.is_dir()) if gdir.exists() else []
    if not runs_file.exists():
        unrecorded.append({'project': project, 'path': str(gdir), 'prose_files': prose, 'subdirs': subdirs[:12], 'note': 'no runs.jsonl; prose or round files only', 'ingested_at': now})
        return
    for i, line in enumerate(runs_file.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            unrecorded.append({'project': project, 'path': f'{runs_file}:{i}', 'note': f'unparseable line: {exc}', 'ingested_at': now})
            continue
        shape = detect_shape(rec)
        if not shape:
            unrecorded.append({'project': project, 'path': f'{runs_file}:{i}', 'note': 'unknown record shape', 'keys': sorted(rec)[:20], 'ingested_at': now})
            continue
        row = MAPPERS[shape](rec, project, f'{runs_file}:{i}')
        row['schema_version'] = 1
        row['ingested_at'] = now
        rows.append(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=str(repo / ('ledger/config.local.json' if (repo / 'ledger/config.local.json').exists() else 'ledger/config.json')))
    args = ap.parse_args()
    cfg = load_config(args.config)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    rows, unrecorded = [], []
    for root in cfg['roots']:
        for gdir in find_gauntlet_dirs(root, cfg['gauntlet_dir_names'], set(cfg['exclude_dir_names']), cfg['max_depth']):
            project = gdir.parent.name if gdir.parent != Path(root) else gdir.name
            ingest_dir(gdir, project, rows, unrecorded, now)
    self_dir = repo / cfg.get('self_repo_gauntlet', 'gauntlet')
    if self_dir.exists():
        ingest_dir(self_dir, repo.name, rows, unrecorded, now)
    seen, deduped = set(), []
    for r in rows:
        key = (r['project'], r['run_id'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    out_dir = repo / 'ledger'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'runs.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in deduped), encoding='utf-8')
    (out_dir / 'unrecorded.jsonl').write_text(''.join(json.dumps(u, ensure_ascii=False) + '\n' for u in unrecorded), encoding='utf-8')
    shapes = {}
    for r in deduped:
        shapes[r['source_shape']] = shapes.get(r['source_shape'], 0) + 1
    print(json.dumps({'recorded_runs': len(deduped), 'by_shape': shapes, 'unrecorded_dirs': len(unrecorded), 'model_tokens_used': 0}))


if __name__ == '__main__':
    sys.exit(main())
