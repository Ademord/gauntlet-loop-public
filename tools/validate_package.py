"""Deterministic package checks for a Gauntlet skill package (structure, size, links, YAML, export boundary).

Usage: python tools/validate_package.py [--package skill] [--version 5.1.0] [--expect-files 9]
       [--max-skill-bytes 16000] [--export dist/gauntlet-loop-v5-SKILL.md --max-export-bytes 110000]

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
EXPECTED_FILES = 8   # the v4 and v5.0 package shape; 5.1 adds a ninth file, so callers pass --expect-files
EXPECTED_INCLUDES = 8  # bullets the drafting reference requires a prompt to carry; the marker table below tracks them


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


def example_includes(package):
    """Check that each worked example carries a marker for every include the drafting reference lists.

    Three review rounds in a row found the sentence "the two worked examples carry every include" untrue, each time
    by less. A critic's diagnosis was that a prose claim of exhaustive coverage needs a mechanical check rather than
    another manual pass, and this is it. It checks that a marker for each include is present, not that the include
    is well expressed; a missing marker is always a real gap, a present one is necessary and not sufficient.
    """
    path = package / 'references/bars-and-examples.md'
    if not path.exists():
        return []
    text = path.read_text(encoding='utf-8')
    examples = [block.split('```')[0] for block in text.split('```text')[1:]]
    if not examples:
        return []
    markers = {
        'reference and comparison dimension': ['Compare the result against'],
        'difficulty and topology': ['Difficulty is'],
        'evidence classes': ['deterministic, external, or judgment'],
        'third-round ladder': ['advisory'],
        'revision drift': ['drift'],
        'resume validation': ['resume validation decision'],
        'task class and features': ['Task class is'],
        'model assignment': ['Inherit the configured models'],
        'builder-local testing': ['focused tests', 'own feedback'],
        'integrated checks': ['Independently verify'],
        'verdict vocabulary': ['winner ours/bar/none'],
        'budget and reserve': ['Budget:'],
        'checkpoint': ['Checkpoint after each verdict'],
    }
    metadata, _ = frontmatter((package / 'SKILL.md').read_text(encoding='utf-8'))
    version = tuple(int(n) for n in str(metadata.get('metadata', {}).get('version', '0.0')).split('.')[:2])
    if version >= (5, 2):
        markers.update({
            'incoming-message continuity': ['Keep unfinished objectives'],
            'conceptual reconsideration': ['Conceptual dissatisfaction'],
        })
    failures = []
    # The marker table is written by hand against the include list, so it can drift from it exactly as the three
    # vocabulary copies did. Bind them: if the include list changes length, this check must be revisited.
    drafting = package / 'references/prompt-drafting.md'
    if drafting.exists():
        text_d = drafting.read_text(encoding='utf-8')
        after = text_d.split('Carry the acceptance contract into the prompt', 1)
        if len(after) == 2:
            bullets = 0
            for line in after[1].splitlines():
                if line.startswith('- '):
                    bullets += 1
                elif bullets and not line.strip():
                    break
            if bullets != EXPECTED_INCLUDES:
                failures.append(f'the drafting reference lists {bullets} includes, not the {EXPECTED_INCLUDES} this '
                                f'marker table was written against; revisit the table and update EXPECTED_INCLUDES')
    for i, example in enumerate(examples, 1):
        for include, alternatives in markers.items():
            if not any(a in example for a in alternatives):
                failures.append(f'worked example {i} carries no marker for the {include} include')
    return failures


def vocabularies(package, version):
    """Check the two closed vocabularies against every other copy of them in this repository.

    The 5.1 upgrade shipped an invented pair of lists in review round 1 and the repository's only real milestone
    record failed all three of its values. Prose in three documents saying "change all copies together" is not a
    control; this is. Silent for a package that states no vocabularies, which is every version before 5.1.
    """
    def tokens(line, drop):
        """Values named in a line, whether written one per backtick or pipe-separated inside one span."""
        found = set()
        for span in re.findall(r'`([^`]+)`', line):
            for part in span.split('|'):
                part = part.strip()
                if re.fullmatch(r'[a-z][a-z_-]*', part):
                    found.add(part)
        return found - drop

    contract = package / 'references/execution-contract.md'
    if not contract.exists():
        return []
    lines = contract.read_text(encoding='utf-8').splitlines()
    skill = {}
    for field in ('task_class', 'features_enabled'):
        row = [l for l in lines if re.match(rf'^\s*[-*+]\s+`{field}`', l)]
        if row:
            skill[field] = tokens(row[0], {'task_class', 'features_enabled', 'features_not_enabled', 'unknown'})
    if len(skill) < 2:
        # Silence is correct for a package that predates these fields, and a lie for one that does not. A critic
        # showed this check could be disabled by changing a bullet marker, with no signal at all.
        if version >= (5, 1):
            missing = sorted({'task_class', 'features_enabled'} - set(skill))
            return [f'version {version[0]}.{version[1]} states no parseable vocabulary row for: {", ".join(missing)}']
        return []
    failures = []
    schema_path = repo / 'ledger/SCHEMA.md'
    if schema_path.exists():
        for field, values in skill.items():
            row = [l for l in schema_path.read_text(encoding='utf-8').splitlines() if l.startswith(f'| `{field}`')]
            if not row:
                failures.append(f'ledger/SCHEMA.md has no row for {field}')
            else:
                other = tokens(row[0], {'task_class', 'features_enabled', 'features_not_enabled', 'unknown', 'string'})
                if other != values:
                    failures.append(f'{field} differs from ledger/SCHEMA.md: only in skill {sorted(values - other)}, '
                                    f'only in schema {sorted(other - values)}')
    features_py = repo / 'tools/ledger/features.py'
    if features_py.exists() and 'features_enabled' in skill:
        text = features_py.read_text(encoding='utf-8')
        block = re.search(r'FEATURES = \[(.*?)\]', text, re.S)
        if not block:
            failures.append('tools/ledger/features.py has no FEATURES list')
        else:
            coded = set(re.findall(r"'([a-z_]+)'", block.group(1)))
            if coded != skill['features_enabled']:
                failures.append(f'features_enabled differs from tools/ledger/features.py: only in skill '
                                f'{sorted(skill["features_enabled"] - coded)}, only in code '
                                f'{sorted(coded - skill["features_enabled"])}')
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', default='skill')
    ap.add_argument('--version', required=True)
    ap.add_argument('--max-skill-bytes', type=int, default=16000)
    ap.add_argument('--export')
    ap.add_argument('--max-export-bytes', type=int, default=90000)
    ap.add_argument('--expect-files', type=int, default=EXPECTED_FILES,
                    help='how many files the package must contain; 8 through 5.0.0, 9 from 5.1.0')
    args = ap.parse_args()
    package = repo / args.package
    failures = []
    files = sorted(p for p in package.rglob('*') if p.is_file())
    if len(files) != args.expect_files:
        failures.append(f'expected {args.expect_files} files, found {len(files)}')
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
    parts = tuple(int(n) for n in re.findall(r"\d+", args.version)[:2]) or (0, 0)
    failures += vocabularies(package, parts)
    failures += example_includes(package)
    export_bytes = None
    if args.export:
        export_path = repo / args.export
        if not export_path.exists():
            failures.append(f'export missing: {args.export}')
        else:
            raw = export_path.read_bytes()
            portable = raw.decode('utf-8')
            export_bytes = len(raw)  # bytes on disk: decoding first collapses CRLF and undercounts by a byte a line
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
