# Status

Work in progress, updated 18 September 2026. This is the canonical working repository.

## Where things stand

| Area | State | Where |
| --- | --- | --- |
| Skill 5.0.0 | Accepted by a gauntlet run on itself: nine frozen checks, six independent critic reviews. Not benchmarked. Installing it is up to each user | [skill/](skill/SKILL.md), [dist/](dist/README.md), [gauntlet/v5-upgrade-2026-09-17/](gauntlet/v5-upgrade-2026-09-17/progress.md) |
| Version history | Complete from v1 to v5; every stored file checksummed | [versions/](versions/README.md) |
| Research | Six papers noted with verbatim abstracts; the v5 thesis; a research program with a pre-registered paired-study protocol and a backlog | [research/](research/README.md) |
| Run ledger | Scripts ready. The first ingest over the author's projects found three recorded runs and five run folders without a machine-readable record; every cell is below threshold. Outputs stay local | [tools/ledger/](tools/README.md), [ledger/SCHEMA.md](ledger/SCHEMA.md) |
| Paired-study harness | Analysis self-test passes; arms generated for two tasks minted from public repositories; execute mode never run | [tools/paired_study/](tools/paired_study/README.md), [research/program/paired-study/](research/program/paired-study/tasks/001-intelligence-pipeline-sum-check.yaml) |
| Leak guard | Pre-commit guard and audit; zero hits on the tree and the history | [tools/README.md](tools/README.md) |

## Known limitations

- Only the abstracts of the six v5 papers were read.
- The difficulty estimate every run records is the lead's self-report.
- The v5 critics were language models judging text about language-model critics, and the scenario probes were written by the same lead who wrote the candidate.
- The last consistency fix of the v5 run was verified deterministically after the last critic read it; see [dist/RELEASE-REVIEW.md](dist/RELEASE-REVIEW.md).
- v4 and v5 dropped the worked examples and the bar table that v1 to v3 carried; the effect was never measured.
- The paired-study runner's execute mode is untested; the first pair is its test.

## Next steps, in order

1. Run the first paired run, task t001 with flag F1 (light versus compact), as the harness test; read both transcripts; record the measured cost per arm (B-016).
2. Build the mutation-minting script that supplies low-difficulty tasks for thirty pairs (B-014).
3. Process the next batch of papers through [research/INTAKE.md](research/INTAKE.md) into backlog rows, then batch the rows into a 5.1 upgrade run. Already queued for 5.1: task class and features in the milestone record (B-002), the route wording and `winner: bar` for repairs (B-009), the prompt template's length (B-012), budgets under small caps (B-013), and restoring the examples and bar table v4 dropped (B-020).
4. Design the per-chat record behind the every-interaction-as-experiment direction (B-019).

The full list with gates and states is the [backlog](research/program/backlog.md).

## How to resume

Before dispatching work, write a resume validation record as the [execution contract](skill/references/execution-contract.md) prescribes. Then run `python tools/verify_release.py`, the validator, and `python tools/ledger/run_all.py` with your local configuration to confirm the state matches this file.
