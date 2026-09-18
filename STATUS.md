# Status

Work in progress, updated 19 September 2026. This is the canonical working repository.

## Where things stand

| Area | State | Where |
| --- | --- | --- |
| Skill 5.0.0 | Accepted by a gauntlet run on itself: nine frozen checks, six independent critic reviews. Not benchmarked. Installing it is up to each user | [skill/](skill/SKILL.md), [dist/](dist/README.md), [gauntlet/v5-upgrade-2026-09-17/](gauntlet/v5-upgrade-2026-09-17/progress.md) |
| Version history | Complete from v1 to v5; every stored file checksummed | [versions/](versions/README.md) |
| Research | Six papers noted with verbatim abstracts; the v5 thesis; a research program with a pre-registered paired-study protocol, amended 19 September for harness isolation and measurement | [research/](research/README.md) |
| Run ledger | Scripts ready. The first ingest over the author's projects found three recorded runs and five run folders without a machine-readable record; every cell is below threshold. Outputs stay local | [tools/ledger/](tools/README.md), [ledger/SCHEMA.md](ledger/SCHEMA.md) |
| Paired study | Fourteen pairs ready for flag F1 (light versus compact): two tasks from real commits and twelve mutation-minted tasks, each rebuilt and confirmed. The first attempt stopped at the CLI login; no task work and no spend. Execute mode is hardened with a login preflight and arm isolation | [research/program/paired-study/LOG.md](research/program/paired-study/LOG.md), [tools/paired_study/](tools/paired_study/README.md) |
| Guards | Pre-commit leak guard, audit with zero hits on tree and history, and a commit-msg guard that refuses skill changes not tied to an upgrade run | [tools/README.md](tools/README.md) |

## Known limitations

- Only the abstracts of the six v5 papers were read.
- The difficulty estimate every run records is the lead's self-report.
- The v5 critics were language models judging text about language-model critics, and the scenario probes were written by the same lead who wrote the candidate.
- The last consistency fix of the v5 run was verified deterministically after the last critic read it; see [dist/RELEASE-REVIEW.md](dist/RELEASE-REVIEW.md).
- v4 and v5 dropped the worked examples and the bar table that v1 to v3 carried; the effect was never measured.
- The twelve mutation tasks all come from one repository and are one-token defects; results on them generalize only to that class.
- No pair has produced a valid result yet, so the per-arm cost is still an estimate.

## Next steps, in order

1. **Owner:** log the standalone CLI in once. In a terminal, run `claude` and then `/login`. Nothing else is blocked on you.
2. Run the harness test, t001 on its own, and read both transcripts (B-016):

   ```bash
   PYTHONPATH=.validation-deps python tools/paired_study/run_pair.py --pair research/program/paired-study/pairs/t001-ip-sum-check-gates-confidence/F1 --execute
   ```

3. If the transcripts show a sound harness, run the other thirteen pairs and analyze them with `tools/paired_study/analyze_pairs.py --flag F1`. Thirty pairs are the planned first look; mint more with `tools/paired_study/mint_mutations.py`.
4. Run the 5.1 upgrade on the queued candidates: restore the examples and bar table v4 dropped (B-020), task class and features in the milestone record (B-002), the route wording and `winner: bar` for repairs (B-009), the prompt template's length (B-012), budgets under small caps (B-013).
5. Take new papers through [research/INTAKE.md](research/INTAKE.md) as they arrive.
6. Design the per-chat record behind the every-interaction-as-experiment direction (B-019).

The full list with gates and states is the [backlog](research/program/backlog.md).

## How to resume

Before dispatching work, write a resume validation record as the [execution contract](skill/references/execution-contract.md) prescribes; the paired-study log has a worked example. Then run `python tools/verify_release.py`, the validator, and `python tools/ledger/run_all.py` with your local configuration to confirm the state matches this file.
