# Status, 18 September 2026

Work in progress. This file is the public handoff: what exists, what is verified, what is untested, and what is next. Everything here was produced with deterministic scripts or with independent critic reviews recorded under `gauntlet/`; nothing claims a measured performance gain.

## State

| Item | State | Evidence |
| --- | --- | --- |
| Skill package 5.0.0 | reviewed and accepted by a gauntlet run on itself; not installed anywhere by this repository | `gauntlet/v5-upgrade-2026-09-17/` (six critic reviews in three rounds, nine frozen checks all passed), `provenance/v5/` |
| Portable export and ZIP | reproducible byte for byte from `skill/`; hashes recorded | `tools/build_release.py`, `tools/verify_release.py` |
| Thesis and per-paper notes | written; abstracts verified verbatim by an independent critic; full papers not read | `docs/thesis/v5-thesis.md`, `research/scan-2026-09-17/` |
| Research program | proposal and pre-registered paired-study protocol written; predictions stated | `research/program/` |
| Run ledger (phase 0) | scripts run over the author's projects: three recorded runs, five unrecorded run directories, every cell `insufficient` at n = 3; outputs kept private (they name other projects) | `tools/ledger/`, `ledger/SCHEMA.md` |
| Paired-study harness | analysis self-test passes; arm generator produces prompts that differ only in the flag block; runner dry-runs; execute mode never run | `tools/paired_study/` |
| Task pool | two tasks minted from public repositories and checked empirically; supply for thirty pairs proposed (mutation-minted tasks) but not built | `research/program/paired-study/tasks/`, backlog B-014 |
| First paired run | not executed; it is the harness test and costs model tokens | backlog B-016 |
| Installation into a live skills directory | not done; owner's decision | backlog B-010 |

## Known limitations, stated plainly

- Only abstracts of the six papers were read.
- The difficulty estimate every run records is the lead's self-report.
- One consistency fix in the v5 run was verified by the lead deterministically after the last critic read; disclosed in `provenance/v5/release-review.md`.
- Critics were language models judging text about language-model critics; the probes were written by the same lead who wrote the candidate.
- The paired-study runner's execute mode is untested. The first pair is the test.

## Next steps, in order

1. Run the first pair (task t001, flag F1: light versus compact) as the harness test; read both transcripts; record the measured per-arm cost. Backlog B-016.
2. Build the mutation-minting script for low-difficulty deterministic tasks. Backlog B-014.
3. Process the next batch of papers through `docs/RESEARCH-INTAKE.md` into backlog rows; batch adopted rows into a 5.1 upgrade run. Standing.
4. Decide the open skill items: template length (B-012), small-cap budget edge cases (B-013), two v4 inheritances in the route verbs and the `winner: bar` reading for repairs (B-009).

The full backlog with gates and states is [research/program/backlog.md](research/program/backlog.md).

## How to resume

Before dispatching any work, write a resume validation record as the execution contract prescribes: checkpoint identity, artifact identity match, versions match, authorization still valid, external effects reconciled, decision. The v5 run's own resume after an interruption is recorded in its events and is the worked example.
