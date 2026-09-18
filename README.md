# Gauntlet Loop

A skill for coding agents (Codex, Claude Code, or any host with subagents) that turns an ambitious goal into a deliverable which survives comparison against a real reference and independent, evidence-based checks. Build, have a separate critic judge against a concrete bar, revise, and stop only on a verified win or an exhausted budget. Version 5.0.0, September 2026. Work in progress: see [STATUS.md](STATUS.md).

## What is here

| Path | What it is |
| --- | --- |
| [skill/](skill/SKILL.md) | The current package: entrypoint plus seven references (execution contract, team method, learning, prompt drafting, software quality, agent language, research basis) |
| [releases/v5/](releases/v5/) | The same package as one portable Markdown file and as an installable ZIP, with hashes in [provenance/v5/](provenance/v5/package-verification.json) |
| [docs/thesis/v5-thesis.md](docs/thesis/v5-thesis.md) | Why v5 is shaped the way it is: six September 2026 papers, each judged for transfer, what was adopted, adapted, rejected |
| [research/scan-2026-09-17/](research/scan-2026-09-17/README.md) | One note per paper with the abstract verbatim, the paraphrase checked line by line, limits, and the adoption judgment |
| [research/program/](research/program/gauntlet-bench-v2-hypothesis.md) | The research program: from "which agent architecture wins" to "which is the cheapest that reliably solves this task", a pre-registered paired-study protocol, and the backlog |
| [gauntlet/v5-upgrade-2026-09-17/](gauntlet/v5-upgrade-2026-09-17/progress.md) | The run that produced v5 by applying the skill to itself: frozen contract, probes, six independent critic verdicts, events, evidence |
| [tools/](tools/) | Deterministic tooling: package validator, release builder, run ledger, paired-study harness, public-readiness audit |
| [docs/RESEARCH-INTAKE.md](docs/RESEARCH-INTAKE.md) | How a new paper becomes, or does not become, a rule |
| [versions/](versions/) | The original v1 (CC BY 4.0) and the previous v4 package, byte for byte |

## Using the skill

Copy `skill/` into your host's skills directory under the name `gauntlet-loop` (for Codex: `~/.codex/skills/gauntlet-loop`), or use the single-file `releases/v5/gauntlet-loop-v5-SKILL.md` where a host takes one file. Invoke with `$gauntlet-loop` or by asking for a gauntlet ("gauntlet this", "loop until it beats X", "make a gauntlet prompt"). By default it drafts one paste-ready prompt; when asked to run, it executes as the lead with a separate critic. Nothing in the skill starts a benchmark, installs anything, or schedules work.

## What v5 changed

Every expensive mechanism is gated on verifiability, and every run records enough to test where the gate belongs:

- Evidence classes on every finding (`deterministic`, `external`, `judgment`) and a revision ladder: from a piece's third review round, an uncorroborated judgment finding is advisory and cannot force a revision or block acceptance.
- A recorded difficulty and verifiability estimate, a recorded topology decision, and a `light` topology for low-difficulty work with deterministic checks.
- A retrieval allowance and a per-lesson utility ledger when cross-run learning is on: lessons earn `active` status from downstream benefit, not from sounding important.
- A resume validation record before any dispatch after a pause; a later success never validates an invalid resume.
- Completion-time accounting and an observational tuple in every milestone.

No benchmark establishes that v5 outperforms v4. The thesis states what would falsify each design choice; the research program states how the question would be answered.

## Contributing research

Papers arrive faster than versions should. [docs/RESEARCH-INTAKE.md](docs/RESEARCH-INTAKE.md) is the fixed path from abstract to note to backlog row to, possibly, a rule adopted through an upgrade run with frozen checks and independent critics. Use [research/scan-template.md](research/scan-template.md). The paired-study protocol in [research/program/phase2-paired-study.md](research/program/phase2-paired-study.md) is pre-registered; predictions are stated before any pair runs.

## Verifying this copy

```bash
PYTHONPATH=.validation-deps python tools/validate_package.py --version 5.0.0 --export releases/v5/gauntlet-loop-v5-SKILL.md
python tools/verify_release.py
python tools/public_audit.py
python tools/paired_study/analyze_pairs.py --selftest
```

PyYAML and pytest are expected in a local `.validation-deps/` directory (`pip install --target .validation-deps pyyaml pytest`).

## Working in this repository

From 18 September 2026 this is the canonical working repository; the private original is frozen. Personal paths never enter it:

- Real paths go in gitignored local files: `ledger/config.local.json` (roots for the run ledger; its first root also resolves `<projects-root>` in task specs, or set `GAUNTLET_PROJECTS_ROOT`), `tools/paired_study/survey_config.local.json`, and `tools/private_terms.local.json` (terms that must never appear here). `*.local.json` is ignored.
- Install the guard once per clone: `git config core.hooksPath tools/hooks`. Every commit is then scanned by `tools/hooks/check_staged.py` and refused if a staged text file contains a personal path, machine identity, personal identity, secret, or a private term.
- Run records, ledger outputs, task specs, and evidence are welcome when they pass the guard; refer to another project by name only if that project is public.

## What is not here

This is a curated export of a private canonical repository. Excluded on purpose: run evidence and provenance that contain local paths, earlier intermediate versions (v2, v3, a pre-team customization), the study archives and raw research feeds, commissioned pitches, a repository survey, and the run ledger outputs, which name other private projects. The export boundary is enforced by `tools/public_audit.py` (zero hard hits on every tracked file) and the copy is rebuilt deterministically from the private repository; nothing is edited by hand after export.

## Lineage and license

The gauntlet technique is Matt Shumer's; v1 was packaged by Jay E at RoboNuggets under CC BY 4.0; v2 to v5 are by Franco Ribera. See [docs/LINEAGE.md](docs/LINEAGE.md) and [research/historical-lineage.md](research/historical-lineage.md). Skill text, docs, and research notes are CC BY 4.0; tools are MIT. See [LICENSE.md](LICENSE.md).
