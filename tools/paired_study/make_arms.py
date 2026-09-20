"""Generate the two arm prompts for one paired-study task and flag, plus a manifest with the spec hash and order.

Zero model tokens. The prompts follow the v5 prompt-drafting template; the only difference between arms is the
flag block. Usage:
  python tools/paired_study/make_arms.py --spec task.yaml --flag F1 [--out research/program/paired-study/pairs]
Flags: F1 light-vs-compact, F2 ladder-on-vs-off, F3 parallel-lenses-vs-single-critic, F4 retrieval-on-vs-off.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / '.validation-deps'))
import yaml  # noqa: E402


def spec_path_for_record(given):
    """Record the spec path relative to the repository, never as it was typed.

    Passing an absolute path once put a personal home directory into a tracked manifest of a public repository.
    """
    p = Path(given)
    try:
        return str(p.resolve().relative_to(repo)).replace(chr(92), '/')
    except ValueError:
        raise SystemExit(f'spec must live inside the repository, got {given}')


def projects_root():
    """Real projects root from GAUNTLET_PROJECTS_ROOT or the gitignored ledger/config.local.json; never committed."""
    import os
    env = os.environ.get('GAUNTLET_PROJECTS_ROOT')
    if env:
        return env
    local = repo / 'ledger/config.local.json'
    if local.exists():
        roots = json.loads(local.read_text(encoding='utf-8')).get('roots') or []
        if roots:
            return roots[0]
    return '<projects-root>'

FLAGS = {
    'F1': {
        'name': 'light-vs-compact',
        'A': 'Topology: light. One bounded build, then one independent evidence-based review that reruns the checks; no preference comparison loop. A light review that does not accept escalates to compact with the reason recorded.',
        'B': 'Topology: compact. A lead/builder and a separate critic with fresh context; build, independent review, revise, until the checks pass and the comparison favors ours, within the budget.',
    },
    # Same contrast as F1, run on the excision task class. It is a separate key so its rows can never pool with the
    # mutation series: the third amendment forbids averaging over two task populations.
    'F1-excision': {
        'name': 'light-vs-compact, excision tasks',
        'A': 'Topology: light. One bounded build, then one independent evidence-based review that reruns the checks; no preference comparison loop. A light review that does not accept escalates to compact with the reason recorded.',
        'B': 'Topology: compact. A lead/builder and a separate critic with fresh context; build, independent review, revise, until the checks pass and the comparison favors ours, within the budget.',
    },
    'F2': {
        'name': 'ladder-on-vs-off',
        'A': 'Class every finding deterministic, external, or judgment. From this piece\'s third review round on, an uncorroborated judgment finding is advisory: recorded, but it cannot be the biggest gap, force a revision, or block acceptance. Compare each revision against the retained best and name drift.',
        'B': 'Class every finding deterministic, external, or judgment for the record only. In every round, any finding the critic names as the biggest gap drives the next revision, whatever its class. Compare each revision against the retained best and name drift.',
    },
    'F3': {
        'name': 'parallel-lenses-vs-single-critic',
        'A': 'Each review round dispatches three independent critics in parallel with distinct lenses (behavior and tests; code and regressions; requirements and evidence); the three verdicts form one round and share one review index.',
        'B': 'Each review round dispatches one independent generalist critic.',
    },
    'F4': {
        'name': 'retrieval-on-vs-off',
        'A': 'Cross-run learning is on for this project: retrieve at most three active or experimental lessons by applicability, record each retrieval with its cost, and write each retrieval outcome to the utility ledger.',
        'B': 'Cross-run learning is on for this project for recording only: nominate lessons at the milestone, but inject no stored lesson into working context.',
    },
}


def reserve(cap):
    return math.ceil(0.2 * cap)


def build_prompt(spec, flag_text):
    cap = int(spec.get('review_cap', 8))
    res = reserve(cap)
    failing = spec.get('failing_tests') or [spec['failing_test']]
    checks = f"the failing test{'s' if len(failing) > 1 else ''} {', '.join(failing)} pass{'' if len(failing) > 1 else 'es'}; the full suite ({spec['test_command']}) passes with no new failures and no skips; changes stay within {', '.join(spec.get('allowed_paths', ['the files the task names']))}; regression coverage addresses the failure class, not one example"
    return f"""Complete the following repair for the maintainers of this repository: {spec['description'].strip()} Compare the result against the failing original on behavior, not style: record the pre-fix revision, run `{spec['test_command']}` and keep the output as the reference snapshot. Required checks: {checks}. Reuse existing authorization and project constraints.

Difficulty is {spec['difficulty']['estimate']} because {', '.join(spec['difficulty']['proxies'])}; required checks are {spec['verifiability']}. {flag_text} Builders may run focused tests and formatters in isolation; the independent critic inspects the actual artifact and reruns the checks. Inherit configured models and record actual assignments where observable.

Each verdict carries candidate identity, reference snapshot, criteria version, winner ours/bar/none, the biggest gap, all blocking findings, each check as passed/failed/blocked/not applicable, any HOLD, and concrete evidence. Resolve disputed facts by discriminating observations. Acceptance requires ours to win, every required check to pass, and no blocking HOLD.

Budget: {cap} critic reviews total, hard; reserve the last {res} for integration and handoff, so converge at {cap - res}. All workers share one ledger; splitting or resuming does not refill it. Disclose unobservable usage.

After two repeated unresolved-gap verdicts, diagnose before editing. Checkpoint after each verdict with identities, obligations, holds, owners, next action, and remaining budget; after any pause, record a resume validation decision before dispatching. Keep a readable progress file. At acceptance or budget exhaustion, append one milestone line to gauntlet/runs.jsonl in the v5 milestone shape (difficulty, verifiability, topology, reviews used, advisory-only reviews, outcome state, wall-clock, models) and stop. No benchmark, model sweep, or scheduled follow-up."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--flag', required=True, choices=sorted(FLAGS))
    ap.add_argument('--out', default=str(repo / 'research/program/paired-study/pairs'))
    args = ap.parse_args()
    spec_bytes = Path(args.spec).read_bytes()
    spec = yaml.safe_load(spec_bytes)
    if isinstance(spec.get('repo'), str):
        spec['repo'] = spec['repo'].replace('<projects-root>', projects_root())
    for key in ('base_commit', 'answer_commit'):
        if key in spec:
            spec[key] = str(spec[key])  # an all-digit hash would otherwise parse as an integer
    spec_hash = hashlib.sha256(spec_bytes).hexdigest()
    flag = FLAGS[args.flag]
    order = ['A', 'B'] if int(hashlib.sha256(spec['task_id'].encode()).hexdigest(), 16) % 2 == 0 else ['B', 'A']
    out = Path(args.out) / spec['task_id'] / args.flag
    out.mkdir(parents=True, exist_ok=True)
    prompts = {arm: build_prompt(spec, flag[arm]) for arm in ('A', 'B')}
    for arm, text in prompts.items():
        (out / f'arm{arm}.prompt.md').write_text(text + '\n', encoding='utf-8')
    manifest = {
        'generator_identity': {'name': 'make_arms.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'task_id': spec['task_id'], 'flag': args.flag, 'flag_name': flag['name'], 'spec_path': spec_path_for_record(args.spec), 'spec_sha256': spec_hash,
        'order': order, 'arm_prompt_sha256': {arm: hashlib.sha256(t.encode()).hexdigest() for arm, t in prompts.items()},
        'only_difference': {'A': flag['A'], 'B': flag['B']}, 'review_cap': spec.get('review_cap', 8), 'reserve': reserve(int(spec.get('review_cap', 8))),
        'status': 'generated', 'runs': {}, 'model_tokens_used_by_generator': 0,
    }
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    words = {arm: len(t.split()) for arm, t in prompts.items()}
    print(json.dumps({'out': str(out), 'order': order, 'prompt_words': words, 'spec_sha256': spec_hash[:12]}))


if __name__ == '__main__':
    main()
