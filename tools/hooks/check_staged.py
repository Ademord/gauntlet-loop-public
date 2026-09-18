"""Pre-commit guard: refuse a commit whose staged text files contain a personal path, machine identity, personal
identity, secret (patterns in tools/public_audit_config.json), or any term in the gitignored
tools/private_terms.local.json. Zero model tokens. Install once per clone: git config core.hooksPath tools/hooks
"""
import json
import re
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
cfg = json.loads((repo / 'tools/public_audit_config.json').read_text(encoding='utf-8'))
patterns = [(f'hard:{cat}', re.compile(p)) for cat, pats in cfg['hard_patterns'].items() for p in pats]
local = repo / 'tools/private_terms.local.json'
if local.exists():
    for cat, pats in json.loads(local.read_text(encoding='utf-8')).get('review_terms', {}).items():
        patterns += [(f'private-term:{cat}', re.compile(p, re.I)) for p in pats]
allow = set(cfg.get('audit_allowlist', [])) | {'tools/hooks/check_staged.py'}
text_ext = set(cfg['text_extensions'])
staged = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'], cwd=repo, capture_output=True, text=True).stdout.split()
bad = []
for path in staged:
    if path in allow or not (Path(path).suffix.lower() in text_ext or Path(path).name in text_ext):
        continue
    content = subprocess.run(['git', 'show', f':{path}'], cwd=repo, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
    for kind, pat in patterns:
        if pat.search(content):
            bad.append(f'{path}: {kind} ({pat.pattern})')
if bad:
    print('COMMIT REFUSED by tools/hooks/check_staged.py:\n  ' + '\n  '.join(bad), file=sys.stderr)
    sys.exit(1)
print(f'check_staged: {len(staged)} staged files clean')
