# Status

Work in progress, updated 19 September 2026. This is the canonical working repository.

## Where things stand

| Area | State | Where |
| --- | --- | --- |
| Skill 5.0.0 | Accepted by a gauntlet run on itself: nine frozen checks, six independent critic reviews. Not benchmarked. Installing it is up to each user | [skill/](skill/SKILL.md), [dist/](dist/README.md), [gauntlet/v5-upgrade-2026-09-17/](gauntlet/v5-upgrade-2026-09-17/progress.md) |
| Version history | Complete from v1 to v5; every stored file checksummed | [versions/](versions/README.md) |
| Research | Six papers noted with verbatim abstracts; the v5 thesis; a research program with a pre-registered paired-study protocol, amended 19 September for harness isolation and measurement | [research/](research/README.md) |
| Run ledger | Scripts ready. The first ingest over the author's projects found three recorded runs and five run folders without a machine-readable record; every cell is below threshold. Outputs stay local | [tools/ledger/](tools/README.md), [ledger/SCHEMA.md](ledger/SCHEMA.md) |
| Paired study | First look at flag F1 taken on 14 pairs: both topologies solved every task, no difference detected under the pre-registered tests, and the light arm used about a third fewer tokens. Every arm used exactly one review, so the compact arm never revised and the contrast measured exploration rather than the loop. Minting more tasks toward the planned 30 pairs | [look-F1.md](research/program/paired-study/look-F1.md), [LOG.md](research/program/paired-study/LOG.md) |
| Guards | Pre-commit leak guard, audit with zero hits on tree and history, and a commit-msg guard that refuses skill changes not tied to an upgrade run | [tools/README.md](tools/README.md) |

## Known limitations

- Only the abstracts of the six v5 papers were read.
- The difficulty estimate every run records is the lead's self-report.
- The v5 critics were language models judging text about language-model critics, and the scenario probes were written by the same lead who wrote the candidate.
- The last consistency fix of the v5 run was verified deterministically after the last critic read it; see [dist/RELEASE-REVIEW.md](dist/RELEASE-REVIEW.md).
- v4 and v5 dropped the worked examples and the bar table that v1 to v3 carried; the effect was never measured.
- The twelve mutation tasks all come from one repository and are one-token defects; results on them generalize only to that class.
- Fourteen pairs are one-token defects and small repairs in one public Python repository on one model; nothing here speaks to harder work.
- Cost is measured now: about two dollars and seven minutes per pair, dominated by cache reads.

## Next steps, in order

1. Finish the F1 series to thirty pairs and take the second look; the protocol's stopping rules decide whether a third is needed.
2. Cut medium tasks by hand from release-sized commits (B-025). The flag's contrast never fired on one-token defects, and both the evidence ladder (F2) and the checkpoint handoff need work long enough to reach a third review round.
3. Run the 5.1 upgrade, whose contract and probes are already frozen in `gauntlet/v51-upgrade-2026-09-19/`: restore the bar table and worked examples (B-020), task class and features in the milestone (B-002), route and repair-verdict wording (B-009), template length (B-012), budgets under small caps (B-013).
4. Open the checkpoint-handoff gate (B-023) once medium tasks exist: clone each arm's first-verdict state and cross the solvers, so an arm's advantage separates into arriving well and finishing well.
5. Take new papers through [research/INTAKE.md](research/INTAKE.md) as they arrive; B-021, B-022, B-024 and B-026 are queued from the 19 September scan.

The full list with gates and states is the [backlog](research/program/backlog.md).

## How to resume

Before dispatching work, write a resume validation record as the [execution contract](skill/references/execution-contract.md) prescribes; the paired-study log has a worked example. Then run `python tools/verify_release.py`, the validator, and `python tools/ledger/run_all.py` with your local configuration to confirm the state matches this file.
