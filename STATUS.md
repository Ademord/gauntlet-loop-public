# Status

Work in progress, updated 19 September 2026. This is the canonical working repository.

## Where things stand

| Area | State | Where |
| --- | --- | --- |
| Skill 5.0.0 | Accepted by a gauntlet run on itself: nine frozen checks, six independent critic reviews. Not benchmarked. Installing it is up to each user | [skill/](skill/SKILL.md), [dist/](dist/README.md), [gauntlet/v5-upgrade-2026-09-17/](gauntlet/v5-upgrade-2026-09-17/progress.md) |
| Version history | Complete from v1 to v5; every stored file checksummed | [versions/](versions/README.md) |
| Research | Six papers noted with verbatim abstracts; the v5 thesis; a research program with a pre-registered paired-study protocol, amended 19 September for harness isolation and measurement | [research/](research/README.md) |
| Run ledger | Scripts ready. The first ingest over the author's projects found three recorded runs and five run folders without a machine-readable record; every cell is below threshold. Outputs stay local | [tools/ledger/](tools/README.md), [ledger/SCHEMA.md](ledger/SCHEMA.md) |
| Paired study | Flag F1 is done on mutation tasks: thirty pairs, no difference detected, contrast-fired rate zero. An eight-pair pilot on a harder class, whole functions removed, also produced no first-review rejection, so the revision loop still has nothing to measure. The next class varies specification rather than volume, pre-registered before it is built | [look-F1.md](research/program/paired-study/look-F1.md), [task-classes.md](research/program/paired-study/task-classes.md) |
| Guards | Pre-commit leak guard, audit with zero hits on tree and history, and a commit-msg guard that refuses skill changes not tied to an upgrade run. Both scanners were blind to a Windows path inside a JSON string until 19 September, when one slipped into a tracked manifest; both now scan the de-escaped form, and a spec may name a private repository only through a gitignored alias | [tools/README.md](tools/README.md) |

## Known limitations

- Only the abstracts of the six v5 papers were read.
- The difficulty estimate every run records is the lead's self-report.
- The v5 critics were language models judging text about language-model critics, and the scenario probes were written by the same lead who wrote the candidate.
- The last consistency fix of the v5 run was verified deterministically after the last critic read it; see [dist/RELEASE-REVIEW.md](dist/RELEASE-REVIEW.md).
- v4 and v5 dropped the worked examples and the bar table that v1 to v3 carried; the effect was never measured.
- The twelve mutation tasks all come from one repository and are one-token defects; results on them generalize only to that class.
- No first critic review has returned a negative verdict in any of the 76 recorded arms, so nothing here measures the revision loop; one arm dispatched no critic at all, and one under-reported its review count.
- The thirty F1 pairs are one-token defects and small repairs in one public Python repository on one model; nothing here speaks to harder work, and the flag's own mechanism never fired on them.
- Cost is measured: $53.65 for thirty pairs, about six minutes a pair, dominated by cache reads.

## Next steps, in order

1. Build and pilot the specification-varying task class (B-033) with the corrected mechanism-fired metric (B-034). Two classes have now failed to make a first review reject, and a third failure would itself be the result: that a deterministic oracle over a repository cannot produce work the loop is needed for.
2. Cut medium tasks by hand from release-sized commits (B-025). The flag's contrast never fired on one-token defects, and both the evidence ladder (F2) and the checkpoint handoff need work long enough to reach a third review round.
3. Run the 5.1 upgrade, whose contract and probes are already frozen in `gauntlet/v51-upgrade-2026-09-19/`: restore the bar table and worked examples (B-020), task class and features in the milestone (B-002), route and repair-verdict wording (B-009), template length (B-012), budgets under small caps (B-013).
4. Open the checkpoint-handoff gate (B-023) once medium tasks exist: clone each arm's first-verdict state and cross the solvers, so an arm's advantage separates into arriving well and finishing well.
5. Take new papers through [research/INTAKE.md](research/INTAKE.md) as they arrive; B-021, B-022, B-024 and B-026 are queued from the 19 September scan.

The full list with gates and states is the [backlog](research/program/backlog.md).

## How to resume

Before dispatching work, write a resume validation record as the [execution contract](skill/references/execution-contract.md) prescribes; the paired-study log has a worked example. Then run `python tools/verify_release.py`, the validator, and `python tools/ledger/run_all.py` with your local configuration to confirm the state matches this file.
