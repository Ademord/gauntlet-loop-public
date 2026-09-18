"""Generate a portable Markdown skill with every local reference embedded.

The output path follows the package's own version: releases/v<major>/gauntlet-loop-v<major>-SKILL.md.
"""
import re
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
skill = repo / 'skill'
references = sorted((skill / 'references').glob('*.md'))
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
version = re.search(r'^\s*version:\s*"?(\d+)', entry, re.M).group(1)
parts = [rewrite(skill / 'SKILL.md')]
for path in references:
    parts.append(f'\n---\n\n<a id="{anchors[path.resolve()]}"></a>\n\n' + rewrite(path))
output = repo / f'releases/v{version}/gauntlet-loop-v{version}-SKILL.md'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text('\n'.join(parts), encoding='utf-8')
print(output)
