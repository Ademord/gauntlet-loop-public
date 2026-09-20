# Review calibration 2026-09-20

Status: frozen before model execution. Exploratory apparatus calibration, not a powered performance study or a skill-version comparison.

## Question and contrast

Does a fresh review followed by one correction rescue defects beyond a capable builder's own additional check? Six original, constructed stress fixtures cover two contexts. They diagnose the apparatus; they do not estimate usefulness on representative development work.

For each task, run one ordinary builder with the public requirements, source, visible tests, normal local coding tools, and no instruction to delegate. Freeze its candidate. Three branches start from that identical candidate:

- **baseline:** deliver that candidate.
- **self_check:** resume a fork of the builder's context for one additional check and correction.
- **review:** give a fresh reviewer only the public task and candidate; return its findings to another fork of the builder's original context for one correction.

The runner owns these stages. Delegation is unavailable inside a stage. The reviewer cannot edit. No arm escalates into another arm. The order of self-check versus external review is counterbalanced by task ID; all branches are evaluated after generation so hidden outcomes cannot guide revisions. This estimates an added review-stage effect conditional on these built candidates, not three independent end-to-end systems.

## Budget and identities

Use the previous study's recorded model `claude-sonnet-5`; do not silently substitute. CLI version, observed model IDs, prompts, fixtures, source hashes, session IDs and candidate hashes are recorded. CLI spend limits after the recorded pre-comparison amendment below: build $0.55, self-check $0.85, reviewer $0.45, repair $0.40. The two extra-work branches have equal $0.85 ceilings. Six tasks reserve $13.50 including their shared builds. A $15 session ceiling includes diagnostic calls and the stopped first attempt; no dispatch starts without reserving its ceiling. CLI limits may stop only at request boundaries, so observed cost is also checked after every call. Unknown cost, authentication failure, or a failed stage stops execution for diagnosis; no automatic paid retry.

Original observations are append-only. A run directory cannot be reused. This protocol's hashes are frozen in a manifest before execution. Historical paired-study records are not pooled with this calibration.

## Grading and decision

The fixture author freezes requirements, visible tests, hidden tests and a known-good reference before execution. Each broken base must pass its visible tests and fail hidden checks; the reference must pass both. The builder receives requirements, never hidden tests or reference solutions. Hidden test outputs are withheld until every branch of the task is saved. Each evaluator uses a separate scratch copy with authoritative frozen tests, not candidate-edited tests. Test-file modifications, out-of-scope changes, stage failures and observed forbidden delegation are recorded separately from functional success.

Primary descriptive outcome: all visible and hidden behavioral tests pass within the allocated calls. Also report regressions, rescues/spoils relative to the shared candidate, actual total cost and latency. Count review stages from the controller, not Agent/Task dispatch labels or self-reports. Report edit and verdict events separately. Dollar cost is primary for resource comparisons; token categories and provenance remain separate.

The pilot has no significance threshold and cannot establish equivalence. At a ceiling, report no observed incremental benefit on these fixtures and stop this pilot; do not mint harder fixtures until something wins. If the grader or treatment is invalid, fix the apparatus and preserve the invalid run. A promising result motivates a separately specified representative task sample with untouched confirmation tasks and a sample-size calculation matched to the intended effect. It does not change the production skill automatically.

## Local execution limits

The CLI is the execution backend; its own permission controls apply. Worker copies contain no study files, hidden tests or oracle. This is workspace separation, not a claim of an operating-system isolation boundary. Public requirements may be inspected by the grader author; the final hidden outcomes must not be fed back into a running branch.

## Pre-comparison amendment, 2026-09-20

Pilot 01 stopped on its first reviewer call: build cost $0.3019644; reviewer cost $0.261862 with `error_max_budget_usd` against a $0.25 call limit. The raw stream contains a no-violations review summary, but the CLI did not return a successful stage result. No arm comparison or hidden candidate grading had completed. Including backend diagnostics, known usage cost was $0.577671. The failed run, its original manifest, and raw trace remain preserved and are not pooled into the comparison.

One deliberate allocation correction is made before a new comparison: redistribute the same $13.50 planned stage reservations to $0.55 build, $0.85 self-check, $0.45 reviewer, $0.40 repair. The two extra-work branches retain equal ceilings. The new manifest charges the entire $0.577671 prior cost against the existing $15 overall limit. This changes an operational allocation, not the task set, grader, model, or desired quality outcome. The reviewer prompt now contains only its review role and the public task, removing contradictory inherited builder instructions. There will be no further budget escalation within this calibration if the revised limits fail.
