"""Generate a portable single-file Markdown skill: the entrypoint, then every reference with an anchor, links rewritten.

Usage: python tools/export_single_file.py                                  skill/ -> dist/gauntlet-loop-v<major>-SKILL.md
       python tools/export_single_file.py --package versions/v4 --out v4.md  any stored version
"""
import argparse
import re
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--package', default='skill')
ap.add_argument('--out')
args = ap.parse_args()
skill = repo / args.package
references = sorted((skill / 'references').glob('*.md')) if (skill / 'references').exists() else []
anchors = {path.resolve(): 'reference-' + path.stem for path in references}


def rewrite(path):
    text = path.read_text(encoding='utf-8')

    def link(match):
        label, target = match.groups()
        if target.startswith(('https://', 'http://', '#')):
            return match.group(0)
        destination = (path.parent / target).resolve()
        if destination not in anchors:
            raise ValueError(f'Unresolved portable link: {path.name}: {target}')
        return f'[{label}](#{anchors[destination]})'
    return re.sub(r'\[([^\]]*)\]\(([^)]+)\)', link, text)


entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
version = re.search(r'^\s*version:\s*"?(\d+)', entry, re.M)
if args.out:
    output = Path(args.out)
elif version and args.package == 'skill':
    output = repo / f'dist/gauntlet-loop-v{version.group(1)}-SKILL.md'
else:
    raise SystemExit('--out is required for a stored version')
parts = [rewrite(skill / 'SKILL.md')]
for path in references:
    parts.append(f'\n---\n\n<a id="{anchors[path.resolve()]}"></a>\n\n' + rewrite(path))
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text('\n'.join(parts), encoding='utf-8')
print(output)
