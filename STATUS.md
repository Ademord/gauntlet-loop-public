# Status

Work in progress, updated 21 September 2026. This is the canonical working repository.

Current research decisions are indexed in the [program](research/program/README.md): fifty milestones with linked evidence, dependency checks, concrete experiment plans and frozen result records. Start with `python tools/program.py next`; use the [workflow](research/program/WORKFLOW.md) to update the plan when research or native capabilities change. The available execution driver checks inventory pointers and probe-record structure locally; the native performance comparison still requires a qualified runner and controls.

The [passive observer](ledger/OBSERVER.md) now has installed, explicitly enrolled Codex/Claude adapters, external contact classifications and private snapshot manifests. Codex and a Read-only Claude Opus/high invocation passed native request/tool/completion checks. Claude's earlier credit-limit failure and soft-budget overshoot are preserved. These are compatibility diagnostics, not evidence of orchestration gains. Raw recordings stay private; public checkpoints contain selected summaries and hashes. No daily commit automation is enabled.

## Measurement correction and completed calibration

The independent September 20 audit found incomplete token accounting, a missed critic-driven revision, and unsupported statistical conclusions. The [derived measurement replay](research/program/paired-study/measurement-replay.md) reconciles all 76 counted transcripts: 217,433,726 tokens across complete modelUsage categories, compared with 150,771,035 recorded previously. Original rows remain unchanged. Dollar figures are CLI-reported API-equivalent usage cost; subscription billing was not observed.

The historical F1 arms both allow revision after rejection and use generated prompts, not the full installed skill. They therefore do not establish a benefit of the revision loop or a version-to-version gain. Of 76 counted arms, 76 passed their exposed suites and 74 met scope acceptance; only two arms, on one task, had held-out tests.

The [six-task review calibration](research/program/calibration/DECISION.md) is complete: baseline, builder self-check, and fresh review plus one correction all passed 6/6 frozen suites, at $0.98, $2.82 and $3.35 respectively across six tasks including each branch's shared builds. Total physical usage was $5.77 including the stopped first attempt and diagnostics. Supplementary probes found real repairs in both extra-work paths and a self-check regression that the frozen tests missed. These selected boundary cases cannot estimate general comparative performance. Production skill 5.1.0 remains unchanged. The next performance study requires real tasks sampled independently of reviewer usefulness and independently authored acceptance checks; no further paid run is active.

## Where things stand

| Area | State | Where |
| --- | --- | --- |
| Skill 5.1.0 | Accepted by a gauntlet run under 5.0.0: nine frozen checks, eight scenario probes frozen before building, four independent critics over four review rounds. It restores what v4 dropped and fixes wording the v5 run left ambiguous; no new mechanism, and nothing benchmarked. 5.0.0 is preserved byte for byte in versions/v5/ | [skill/](skill/SKILL.md), [dist/](dist/README.md), [gauntlet/v51-upgrade-2026-09-19/](gauntlet/v51-upgrade-2026-09-19/progress.md) |
| Version history | Complete from v1 to v5.1; every stored file checksummed | [versions/](versions/README.md) |
| Research | Six papers noted with verbatim abstracts; the v5 thesis; a research program with a pre-registered paired-study protocol, amended 19 September for harness isolation and measurement | [research/](research/README.md) |
| Run ledger | Scripts ready. The first ingest over the author's projects found three recorded runs and five run folders without a machine-readable record; every cell is below threshold. Outputs stay local | [tools/ledger/](tools/README.md), [ledger/SCHEMA.md](ledger/SCHEMA.md) |
| Passive observer | Codex and Claude Opus/high request/tool/completion capture verified on bounded fixtures. Failures preserved; human contacts classified separately from explicit resolution. Claude success used only Read and no MCP servers | [observer](ledger/OBSERVER.md), [Opus validation](research/program/materials/observer-native-validation-002.json) |
| Paired study | Historical F1 data corrected and preserved. Both policies permit revision, and x008 contains a nonblocking critic-driven edit. The separate six-task calibration is complete; frozen grades were at a ceiling while supplementary probes found repairs and a regression. No demonstrated general orchestration advantage | [measurement-replay.md](research/program/paired-study/measurement-replay.md), [calibration decision](research/program/calibration/DECISION.md) |
| Guards | Pre-commit leak guard, audit with zero hits on tree and history, and a commit-msg guard that refuses skill changes not tied to an upgrade run. Both scanners were blind to a Windows path inside a JSON string until 19 September, when one slipped into a tracked manifest; both now scan the de-escaped form, and a spec may name a private repository only through a gitignored alias | [tools/README.md](tools/README.md) The validator also compares all three copies of the record vocabularies and checks that both worked examples carry every drafting include, after prose pacts failed at both jobs during the 5.1 run |

## Known limitations

- Only the abstracts of the six v5 papers were read.
- The difficulty estimate every run records is the lead's self-report.
- The v5 critics were language models judging text about language-model critics, and the scenario probes were written by the same lead who wrote the candidate.
- The last consistency fix of the v5 run was verified deterministically after the last critic read it; see [dist/RELEASE-REVIEW.md](dist/RELEASE-REVIEW.md).
- v4 and v5.0 dropped the worked examples and the bar table that v1 to v3 carried; 5.1 restored them, and the effect of neither the dropping nor the restoring was measured.
- The twelve mutation tasks all come from one repository and are one-token defects; results on them generalize only to that class.
- No first critic review was recorded as negative across the 76 counted arms. That does not imply no review-driven edit: x008 changed exception handling after a nonblocking finding. Agent/Task dispatch counts are not verified reviewer counts; see the dated study erratum.
- The thirty F1 pairs are one-token defects and small repairs in one public Python repository on one model; nothing here speaks to harder work, and the flag's own mechanism never fired on them.
- Cost is measured: $53.65 for thirty pairs, about six minutes a pair, dominated by cache reads.
- Calibration reference implementations and their hidden tests shared an author. Supplementary checks found uncovered defects in three references; suite-passing does not mean full contract correctness. The selected supplementary cases are kept outside frozen scores.

## Superseded September 19 plan

The following ordering is retained as history. It is superseded by the September 20 measurement repair and bounded calibration above. A representative confirmation study requires its own task sample and effect-size plan after the apparatus is validated.

1. Build and pilot the specification-varying task class (B-033) with the corrected mechanism-fired metric (B-034). Two classes have now failed to make a first review reject, and a third failure would itself be the result: that a deterministic oracle over a repository cannot produce work the loop is needed for.
2. Cut medium tasks by hand from release-sized commits (B-025). The flag's contrast never fired on one-token defects, and both the evidence ladder (F2) and the checkpoint handoff need work long enough to reach a third review round.
3. Run the 5.1 upgrade, whose contract and probes are already frozen in `gauntlet/v51-upgrade-2026-09-19/`: restore the bar table and worked examples (B-020), task class and features in the milestone (B-002), route and repair-verdict wording (B-009), template length (B-012), budgets under small caps (B-013).
4. Open the checkpoint-handoff gate (B-023) once medium tasks exist: clone each arm's first-verdict state and cross the solvers, so an arm's advantage separates into arriving well and finishing well.
5. Take new papers through [research/INTAKE.md](research/INTAKE.md) as they arrive; B-021, B-022, B-024 and B-026 are queued from the 19 September scan.

The full list with gates and states is the [backlog](research/program/backlog.md).

## How to resume

Before dispatching work, write a resume validation record as the [execution contract](skill/references/execution-contract.md) prescribes; the paired-study log has a worked example. Then run `python tools/verify_release.py`, the validator, and `python tools/ledger/run_all.py` with your local configuration to confirm the state matches this file.
