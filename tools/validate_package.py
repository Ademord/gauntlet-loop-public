"""Deterministic package checks for a Gauntlet skill package (structure, size, links, YAML, export boundary).

Usage: python tools/validate_package.py [--package skill] [--version 5.0.0]
       [--max-skill-bytes 16000] [--export dist/gauntlet-loop-v5-SKILL.md --max-export-bytes 90000]

Exit code 0 means every check passed. Prints a JSON summary. No benchmark, no model call.
"""
import argparse
import json
import re
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / '.validation-deps'))
import yaml  # noqa: E402

FORBIDDEN = [r'C:\\Users', r'C:/Users', r'/c/Users', r'Ademord', r'\bFranco\b', r'gho_', r'ghp_', r'sk-ant-', r'AKIA[0-9A-Z]{12}']
EXPECTED_FILES = 8


def frontmatter(text):
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not match:
        raise ValueError('missing frontmatter')
    data = yaml.safe_load(match.group(1))
    allowed = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
    unexpected = set(data) - allowed
    if unexpected:
        raise ValueError(f'unexpected frontmatter keys: {sorted(unexpected)}')
    name = data['name']
    if not re.match(r'^[a-z0-9-]+$', name) or '--' in name or len(name) > 64:
        raise ValueError(f'bad name {name!r}')
    description = data['description']
    if '<' in description or '>' in description or len(description) > 1024:
        raise ValueError('bad description')
    return data, text[match.end():]


def fenced_blocks(text):
    """Yield (language, body) for each fenced block; raise if a fence is left open."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r'^[ \t]*(`{3,}|~{3,})(.*)$', lines[i])
        if not m:
            i += 1
            continue
        marker, lang = m.group(1), m.group(2).strip()
        body = []
        i += 1
        while i < len(lines) and not re.match(r'^[ \t]*' + re.escape(marker[0]) + '{' + str(len(marker)) + r',}\s*$', lines[i]):
            body.append(lines[i])
            i += 1
        if i >= len(lines):
            raise ValueError('unclosed fence')
        yield lang, '\n'.join(body)
        i += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', default='skill')
    ap.add_argument('--version', required=True)
    ap.add_argument('--max-skill-bytes', type=int, default=16000)
    ap.add_argument('--export')
    ap.add_argument('--max-export-bytes', type=int, default=90000)
    args = ap.parse_args()
    package = repo / args.package
    failures = []
    files = sorted(p for p in package.rglob('*') if p.is_file())
    if len(files) != EXPECTED_FILES:
        failures.append(f'expected {EXPECTED_FILES} files, found {len(files)}')
    skill_text = (package / 'SKILL.md').read_bytes()
    if len(skill_text) > args.max_skill_bytes:
        failures.append(f'SKILL.md is {len(skill_text)} bytes > {args.max_skill_bytes}')
    try:
        data, body = frontmatter(skill_text.decode('utf-8'))
        if data['name'] != 'gauntlet-loop':
            failures.append(f"name is {data['name']!r}")
        if str(data.get('metadata', {}).get('version')) != args.version:
            failures.append(f"metadata.version is {data.get('metadata', {}).get('version')!r}, expected {args.version}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f'frontmatter: {exc}')
    links_checked = yaml_blocks = 0
    for path in files:
        try:
            text = path.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            failures.append(f'{path.name}: not UTF-8')
            continue
        for pattern in FORBIDDEN:
            if re.search(pattern, text):
                failures.append(f'{path.relative_to(repo)}: forbidden pattern {pattern}')
        for label, target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', text):
            if target.startswith(('https://', 'http://')):
                continue
            file_part, _, anchor = target.partition('#')
            destination = (path.parent / file_part).resolve() if file_part else path.resolve()
            links_checked += 1
            if not destination.exists():
                failures.append(f'{path.relative_to(repo)}: broken link {target}')
            elif anchor and f'id="{anchor}"' not in destination.read_text(encoding='utf-8') and not re.search(r'^#+\s+' + re.escape(anchor), destination.read_text(encoding='utf-8'), re.M):
                failures.append(f'{path.relative_to(repo)}: missing anchor {target}')
        try:
            for lang, block in fenced_blocks(text):
                if lang in ('yaml', 'yml'):
                    yaml_blocks += 1
                    yaml.safe_load(block)
        except Exception as exc:  # noqa: BLE001
            failures.append(f'{path.relative_to(repo)}: {exc}')
    export_bytes = None
    if args.export:
        export_path = repo / args.export
        if not export_path.exists():
            failures.append(f'export missing: {args.export}')
        else:
            portable = export_path.read_text(encoding='utf-8')
            export_bytes = len(portable.encode('utf-8'))
            if export_bytes > args.max_export_bytes:
                failures.append(f'export is {export_bytes} bytes > {args.max_export_bytes}')
            for anchor in re.findall(r'\]\(#([^)]+)\)', portable):
                if f'id="{anchor}"' not in portable:
                    failures.append(f'export: unresolved anchor #{anchor}')
    summary = {
        'package': args.package, 'version': args.version, 'files': len(files), 'skill_md_bytes': len(skill_text),
        'export_bytes': export_bytes, 'local_links_checked': links_checked, 'yaml_blocks_parsed': yaml_blocks,
        'failures': failures, 'passed': not failures, 'benchmarks_run': False,
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0 if not failures else 1)


if __name__ == '__main__':
    main()
