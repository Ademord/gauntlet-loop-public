"""Verify the public copy stands alone: package hashes against provenance/v5/package-verification.json, the release
ZIP and portable export, and every local Markdown link. No benchmark, no model call.

Usage: python tools/verify_release.py
"""
import hashlib
import json
import re
import zipfile
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
hash_file = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

record = json.loads((repo / 'provenance/v5/package-verification.json').read_text(encoding='utf-8'))
for name, expected in record['package_files_sha256'].items():
    assert hash_file(repo / 'skill' / name) == expected, f'skill/{name} hash differs from the release record'
archive = repo / 'releases/v5/gauntlet-loop-v5.zip'
assert hash_file(archive) == record['archive_sha256'], 'release zip hash differs'
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    for name, expected in record['package_files_sha256'].items():
        assert hashlib.sha256(bundle.read('gauntlet-loop/' + name)).hexdigest() == expected, f'zip entry {name}'
portable = repo / 'releases/v5/gauntlet-loop-v5-SKILL.md'
assert hash_file(portable) == record['portable_sha256'], 'portable export hash differs'
text = portable.read_text(encoding='utf-8')
for anchor in re.findall(r'\]\(#([^)]+)\)', text):
    assert f'id="{anchor}"' in text, f'portable anchor {anchor}'

broken = []
for path in sorted(repo.rglob('*.md')):
    if '.git' in path.parts or 'node_modules' in path.parts:
        continue
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8', errors='replace')):
        if target.startswith(('https://', 'http://', '#', 'mailto:')):
            continue
        if not (path.parent / target.split('#')[0]).exists():
            broken.append(f'{path.relative_to(repo)}: {target}')
assert not broken, 'broken local links:\n' + '\n'.join(broken)
print(json.dumps({'package_files_verified': len(record['package_files_sha256']), 'zip': 'verified', 'portable': 'verified', 'markdown_links': 'verified', 'benchmarks_run': False}))
