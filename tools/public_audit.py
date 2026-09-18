"""Public-readiness audit: scan the tracked working tree, the release archives, and every commit in git history
for content that must not be published (personal paths, machine identity, personal identity, secrets), plus terms a
person must review (client or company project names, a possible never-name nickname, third-party persons,
job-search material). Classify every tracked path by the ship plan in tools/public_audit_config.json and compute
what blocks a public copy. Zero model tokens. Read-only.

Usage: python tools/public_audit.py            writes .audit/PUBLIC-READINESS.md and .audit/public-readiness.json
"""
import json
import re
import subprocess
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
cfg = json.loads((repo / 'tools/public_audit_config.json').read_text(encoding='utf-8'))
_local = repo / 'tools/private_terms.local.json'
if _local.exists():
    for _k, _v in json.loads(_local.read_text(encoding='utf-8')).get('review_terms', {}).items():
        cfg['review_terms'][_k] = _v

HARD = {cat: [re.compile(p) for p in pats] for cat, pats in cfg['hard_patterns'].items()}
REVIEW = {cat: [re.compile(p, re.I if cat != 'possible_never_name_nickname' else 0) for p in pats] for cat, pats in cfg['review_terms'].items()}
TEXT_EXT = set(cfg['text_extensions'])


def git(args):
    return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


def is_text(name):
    return Path(name).suffix.lower() in TEXT_EXT or Path(name).name in TEXT_EXT


def scan_text(text):
    hits = defaultdict(int)
    for cat, pats in HARD.items():
        for p in pats:
            hits[f'hard:{cat}'] += len(p.findall(text))
    for cat, pats in REVIEW.items():
        for p in pats:
            hits[f'review:{cat}'] += len(p.findall(text))
    return {k: v for k, v in hits.items() if v}


ALLOWLIST = set(cfg.get('audit_allowlist', []))


def plan_for(path):
    """Longest matching prefix wins; `override` files ship from public/overrides and are audited as shipped."""
    best, action = '', cfg.get('default_action', 'unclassified')
    for prefix, act in cfg['ship_plan'].items():
        if (path == prefix or path.startswith(prefix.rstrip('/') + '/')) and len(prefix) > len(best):
            best, action = prefix, act
    return action


def main():
    tracked = [l for l in git(['ls-files']).splitlines() if l]
    tree = {}
    for path in tracked:
        p = repo / path
        if not p.exists():
            continue
        if is_text(path):
            tree[path] = scan_text(p.read_text(encoding='utf-8', errors='replace'))
        elif path.lower().endswith('.zip'):
            zhits, entries_with_hits = defaultdict(int), []
            with zipfile.ZipFile(p) as z:
                for info in z.infolist():
                    if info.is_dir():
                        continue
                    name_hits = scan_text(info.filename)
                    content_hits = scan_text(z.read(info).decode('utf-8', errors='replace')) if is_text(info.filename) else {}
                    merged = defaultdict(int)
                    for h in (name_hits, content_hits):
                        for k, v in h.items():
                            merged[k] += v
                    if merged:
                        entries_with_hits.append({'entry': info.filename, 'hits': dict(merged)})
                        for k, v in merged.items():
                            zhits[k] += v
            tree[path] = dict(zhits)
            tree[path + '::entries'] = entries_with_hits
        else:
            tree[path] = {}

    # history: every commit on every branch, text blobs only
    commits = [c for c in git(['rev-list', '--all']).splitlines() if c]
    history = {}
    seen_blobs = {}
    for c in commits:
        files_with_hits = {}
        for line in git(['ls-tree', '-r', c]).splitlines():
            meta, path = line.split('\t', 1)
            blob = meta.split()[2]
            if not is_text(path) or path in ALLOWLIST:
                continue  # pattern-definition files are exempt in history as in the tree
            if blob not in seen_blobs:
                seen_blobs[blob] = {k: v for k, v in scan_text(git(['show', blob])).items() if k.startswith('hard:')}
            if seen_blobs[blob]:
                files_with_hits[path] = seen_blobs[blob]
        history[c] = files_with_hits

    # ship plan
    plan_rows = []
    blocking = defaultdict(int)
    overrides_dir = repo / 'public/overrides'
    for path in tracked:
        hits = tree.get(path, {})
        action = plan_for(path)
        if action == 'override' and (overrides_dir / path).exists() and is_text(path):
            # the copy ships the override's content, so audit that, not the private original
            hits = scan_text((overrides_dir / path).read_text(encoding='utf-8', errors='replace'))
        allow = path in ALLOWLIST  # files that define the patterns themselves
        hard = {} if allow else {k: v for k, v in hits.items() if k.startswith('hard:')}
        review = {} if allow else {k: v for k, v in hits.items() if k.startswith('review:')}
        plan_rows.append({'path': path, 'action': action, 'hard': hard, 'review': review, 'allowlisted': allow})
        if action in ('ship', 'override', 'scrub', 'unclassified'):
            for k, v in hard.items():
                blocking[k] += v
    ship_hard = sum(v for r in plan_rows if r['action'] in ('ship', 'override', 'unclassified') for v in r['hard'].values())
    ship_review = sum(v for r in plan_rows if r['action'] in ('ship', 'override', 'unclassified') for v in r['review'].values())
    scrub_hard = sum(v for r in plan_rows if r['action'] == 'scrub' for v in r['hard'].values())
    history_commits_with_hits = sum(1 for c, f in history.items() if f)
    verdict = 'NOT READY FOR PUBLIC' if (ship_hard or scrub_hard or history_commits_with_hits) else 'READY FOR A CURATED PUBLIC COPY'

    result = {
        'generated_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'branch': git(['branch', '--show-current']).strip(), 'head': git(['rev-parse', 'HEAD']).strip(),
        'tracked_files': len(tracked), 'verdict': verdict, 'ship_set_hard_hits': ship_hard, 'ship_set_review_hits': ship_review, 'scrub_set_hard_hits': scrub_hard,
        'history_commits_scanned': len(commits), 'history_commits_with_hard_hits': history_commits_with_hits,
        'blocking_by_category': dict(blocking), 'plan': plan_rows,
        'zips': {p: tree[p + '::entries'] for p in tracked if p.lower().endswith('.zip') and (p + '::entries') in tree},
        'history': {c[:10]: {'files_with_hard_hits': len(f), 'sample': sorted(f)[:8]} for c, f in history.items()},
        'model_tokens_used': 0,
    }
    (repo / '.audit').mkdir(exist_ok=True)
    (repo / '.audit/public-readiness.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

    def fmt(d):
        return ', '.join(f'{k.split(":", 1)[1]}={v}' for k, v in sorted(d.items())) or ''

    md = [f'# Public-readiness audit', '', f'Generated {result["generated_utc"]} by `tools/public_audit.py` on branch `{result["branch"]}` at `{result["head"][:10]}`. Read-only, zero model tokens. Hard patterns are personal paths, machine identity, personal identity, and secrets; review terms are names a person must decide on. The ship plan (ship / scrub / exclude) is the lead\'s proposal in `tools/public_audit_config.json`; the owner decides.', '',
          f'## Verdict: {verdict}', '',
          f'- Tracked files: {len(tracked)}. Ship set hard hits: {ship_hard}. Scrub set hard hits: {scrub_hard} (must be removed by hand before those files ship). Ship set review-term hits: {ship_review}.',
          f'- Git history: {len(commits)} commits scanned on all branches; {history_commits_with_hits} contain text blobs with hard hits. A public copy must therefore be a fresh repository, not this one made public.', '',
          '## Hits by top-level path (working tree)', '', '| path | action | hard hits | review hits |', '| --- | --- | --- | --- |']
    agg = {}
    for r in plan_rows:
        top = r['path'].split('/')[0] if '/' in r['path'] else r['path']
        key = top if top in ('README.md', 'STATUS.md', '.gitignore', '.gitattributes') or '/' not in r['path'] else '/'.join(r['path'].split('/')[:2])
        a = agg.setdefault(key, {'action': set(), 'hard': defaultdict(int), 'review': defaultdict(int)})
        a['action'].add(r['action'])
        for k, v in r['hard'].items():
            a['hard'][k] += v
        for k, v in r['review'].items():
            a['review'][k] += v
    for key in sorted(agg):
        a = agg[key]
        md.append(f"| {key} | {', '.join(sorted(a['action']))} | {fmt(a['hard'])} | {fmt(a['review'])} |")
    md += ['', '## Release archives', '']
    for z, entries in result['zips'].items():
        md.append(f'- `{z}`: {len(entries)} entries with hits' + ('' if not entries else '; e.g. ' + '; '.join(f"{e['entry']} ({fmt(e['hits'])})" for e in entries[:5])))
    md += ['', '## Git history', '', '| commit | files with hard hits | sample |', '| --- | --- | --- |']
    for c, h in result['history'].items():
        md.append(f"| {c} | {h['files_with_hard_hits']} | {', '.join(h['sample'][:4])} |")
    md += ['', '## Files with hard hits that the plan would ship or scrub', '', '| path | action | hard hits |', '| --- | --- | --- |']
    for r in plan_rows:
        if r['hard'] and r['action'] in ('ship', 'override', 'scrub', 'unclassified'):
            md.append(f"| {r['path']} | {r['action']} | {fmt(r['hard'])} |")
    md += ['', '## Files with review-term hits (any action)', '', '| path | action | review hits |', '| --- | --- | --- |']
    for r in plan_rows:
        if r['review']:
            md.append(f"| {r['path']} | {r['action']} | {fmt(r['review'])} |")
    md += ['', '## Export checklist mapped to this audit', '',
           '1. Private repository and project names: see review-term hits; the client site and company directories appear only in excluded paths if the plan holds, but the owner must confirm the never-name project is not referenced anywhere (the audit flags one candidate nickname for review).',
           '2. Secrets and identity: hard-pattern counts above; the personal email appears only in historical commit metadata if at all.',
           '3. History: dirty (see table); publish a fresh repository built from a curated export, never this one.',
           '4. Generated and bundled output: release ZIPs and exports are scanned; entries with hits are listed.',
           '5. Evidence: run records, ledger, pitches, task specs, and provenance are excluded from the plan; redacted excerpts can be added later by hand.',
           '6. Private original: this repository stays private and canonical.',
           '7. Standalone proof: the curated copy must pass `tools/validate_package.py` and `tools/verify_archive.py` from its own tree before publication (not yet done).']
    (repo / '.audit/PUBLIC-READINESS.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('verdict', 'tracked_files', 'ship_set_hard_hits', 'scrub_set_hard_hits', 'ship_set_review_hits', 'history_commits_scanned', 'history_commits_with_hard_hits', 'blocking_by_category')}, indent=2))


if __name__ == '__main__':
    main()
