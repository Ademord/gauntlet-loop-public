"""Verify the repository stands alone: skill/ against dist/package-verification.json, the release zip and portable
export in dist/, every stored version against versions/SHA256SUMS, and every local Markdown link outside versions/
(frozen versions keep their original links; v3's four references were never supplied). No benchmark, no model call.

Usage: python tools/verify_release.py                       verify
       python tools/verify_release.py --write-version-sums  regenerate versions/SHA256SUMS first (after adding a version)
"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
hash_file = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
sums = repo / 'versions/SHA256SUMS'
if '--write-version-sums' in sys.argv:
    files = sorted(p for p in (repo / 'versions').rglob('*') if p.is_file() and p.name not in ('README.md', 'SHA256SUMS'))
    sums.write_bytes(''.join(f'{hash_file(p)}  {p.relative_to(repo).as_posix()}\n' for p in files).encode('utf-8'))

record = json.loads((repo / 'dist/package-verification.json').read_text(encoding='utf-8'))
major = record['version'].split('.')[0]
for name, expected in record['package_files_sha256'].items():
    assert hash_file(repo / 'skill' / name) == expected, f'skill/{name} differs from dist/package-verification.json'
archive = repo / f'dist/gauntlet-loop-v{major}.zip'
assert hash_file(archive) == record['archive_sha256'], 'release zip hash differs'
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    for name, expected in record['package_files_sha256'].items():
        assert hashlib.sha256(bundle.read('gauntlet-loop/' + name)).hexdigest() == expected, f'zip entry {name}'
portable = repo / f'dist/gauntlet-loop-v{major}-SKILL.md'
assert hash_file(portable) == record['portable_sha256'], 'portable export hash differs'
text = portable.read_text(encoding='utf-8')
for anchor in re.findall(r'\]\(#([^)]+)\)', text):
    assert f'id="{anchor}"' in text, f'portable anchor {anchor}'

version_files = 0
for line in sums.read_text(encoding='utf-8').splitlines():
    digest, rel = line.split('  ', 1)
    assert hash_file(repo / rel) == digest, f'versions checksum differs: {rel}'
    version_files += 1

broken = []
for path in sorted(repo.rglob('*.md')):
    top = path.relative_to(repo).parts[0]
    if top in ('.git', 'versions', '.validation-deps', '.audit', 'node_modules') or top.startswith('.paired'):
        continue
    for target in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)', path.read_text(encoding='utf-8', errors='replace')):
        if target.startswith(('https://', 'http://', '#', 'mailto:')):
            continue
        if not (path.parent / target.split('#')[0]).exists():
            broken.append(f'{path.relative_to(repo)}: {target}')
assert not broken, 'broken local links:\n' + '\n'.join(broken)
print(json.dumps({'package_files_verified': len(record['package_files_sha256']), 'zip': 'verified', 'portable': 'verified',
                  'version_files_verified': version_files, 'markdown_links': 'verified', 'benchmarks_run': False}))
