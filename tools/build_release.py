"""Build the release artifacts for the current package: portable single file, reproducible ZIP, verification record.

Usage: python tools/build_release.py
Reads the version from skill/SKILL.md, writes releases/v<major>/gauntlet-loop-v<major>.zip (entries under
gauntlet-loop/, fixed timestamps so the archive hash is reproducible), regenerates the single-file export, and
writes provenance/v<major>/package-verification.json with per-file and archive SHA256. No benchmark, no model call.
"""
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
skill = repo / 'skill'
entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
full_version = re.search(r'^\s*version:\s*"?([\d.]+)', entry, re.M).group(1)
major = full_version.split('.')[0]
release_dir = repo / f'releases/v{major}'
release_dir.mkdir(parents=True, exist_ok=True)

subprocess.run([sys.executable, str(repo / 'tools/export_single_file.py')], check=True, cwd=repo)

files = sorted(p for p in skill.rglob('*') if p.is_file())
hashes = {p.relative_to(skill).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

archive = release_dir / f'gauntlet-loop-v{major}.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
    for p in files:
        info = zipfile.ZipInfo('gauntlet-loop/' + p.relative_to(skill).as_posix(), date_time=(2026, 9, 17, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        bundle.writestr(info, p.read_bytes())

portable = release_dir / f'gauntlet-loop-v{major}-SKILL.md'
record = {
    'version': full_version,
    'files': len(files),
    'package_files_sha256': hashes,
    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'portable_sha256': hashlib.sha256(portable.read_bytes()).hexdigest(),
    'portable_bytes': portable.stat().st_size,
    'zip_matches_package': True,
    'benchmarks_run': False,
}
with zipfile.ZipFile(archive) as bundle:
    for name, expected in hashes.items():
        assert hashlib.sha256(bundle.read('gauntlet-loop/' + name)).hexdigest() == expected, name
out = repo / f'provenance/v{major}/package-verification.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'archive': str(archive.relative_to(repo)), 'record': str(out.relative_to(repo)), 'files': len(files), 'archive_sha256': record['archive_sha256']}))
