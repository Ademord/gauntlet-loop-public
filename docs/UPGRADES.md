# Upgrade history

## v5.0.0, September 17, 2026 (candidate; not installed by this repository)

Requested: study six September 2026 papers (Loop-Back Authority, DATS, LIMBO, Interactive Memory Learning, Recoverability, PipeSwift), reason through each like a thesis, and use the gauntlet skill itself to produce v5. Benchmarking stayed deferred; installation was not requested.

Method: a gauntlet run (`gauntlet/v5-upgrade-2026-09-17/`) governed by v4 with v4 as the bar, nine checks frozen before building, six scenario probes derived from the papers, a lead that built, and three independent critics with fresh context (research fidelity, scenario probes plus consistency plus compatibility, prompt-mode forward check). Six critic reviews in three rounds; the run's own difficulty, topology, and evidence ladder were recorded in its contract.

Adopted changes, all additive:

- Evidence classes (`deterministic | external | judgment`) on every finding, check, and biggest gap; a revision ladder under which, from a piece's third review round on, an uncorroborated judgment finding is advisory and cannot force a revision or block acceptance; a revision-drift check against the retained best candidate.
- A recorded difficulty and verifiability estimate in the contract, a recorded topology decision (`light | compact | compact+delegates | team`) with the rule to choose the lightest whose gate is met, a `light` topology gated on low difficulty and deterministic or external checks, defined exits and escalation triggers, and critical-path dispatch.
- A retrieval allowance (three lessons per piece from the run's frozen pool, `active` before `experimental`), retrieval as a recorded event with cost, and a per-lesson utility ledger with promotion on downstream benefit in another run, demotion on repeated irrelevance, quarantine on evidenced harm, and grandfathering of pre-v5 lessons.
- A resume validation record and decision (`resume | repair-then-resume | restart-from-evidence | withhold`) before any dispatch, contract amendment on skill, harness, or model change, the rule that later success never validates an invalid resume, and a `withheld_resume` state.
- Completion-time recording and an observational tuple in the milestone summary (difficulty, verifiability, topology, reviews, advisory counts, wall-clock, lessons and outcomes) so later analysis can ask what a task of a given kind needed.
- Corrections found by review: the entrypoint's reserve sentence now scales with small user caps (ceil(20%)); per-piece limits are capped at the run's remaining allowance minus the reserve; the HOLD wording is "blocking HOLD" throughout; the prompt template gained explicit slots for the estimate and the budget cap.

Review found and corrected: a lesson-activation deadlock (only `active` lessons retrieved while `active` required a benefit earned by retrieval), five underspecified ladder and topology rules under parallel critics, two conflicts introduced by the first round of fixes, and one HOLD-wording residual. Research fidelity was verified by a critic that re-fetched every abstract; every figure, title, identifier, and date matched. A prompt-mode critic on a different model drafted a compliant prompt from v5 alone in both rounds. Findings, dispositions, and candidate hashes are under `gauntlet/v5-upgrade-2026-09-17/evidence/`. This was release QA by independent critics, not a performance benchmark; no claim is made that v5 accepts better work or costs less than v4.

Package limits used as acceptance checks: entrypoint at most 16,000 bytes (final 15,989), single-file export at most 90,000 bytes. The thesis is `docs/thesis/v5-thesis.md`; the research notes with verbatim abstracts are `research/scan-2026-09-17/`; the research program and backlog are under `research/program/`.

## v4.0.0, September 12, 2026

Requested: integrate practical improvements from supplied v3 and accumulated study notes; defer benchmarking. Installed under the existing `gauntlet-loop` identifier and verified byte-for-byte against the release.

Adopted changes: calibrated evidence-based acceptance and consistent `winner: none`, replacing harshness as the quality mechanism; builder-local tests and scoped formatters while retaining independent acceptance and protected expectations; artifact, reference, and criteria identity binding, integrated verification, and explicit HOLD disposition; shared run budgets, per-piece limits, integration reserves, budget continuity, and a repeated-gap diagnosis heuristic; best-candidate retention, verdict checkpoints, ownership, commitments, and executable state as continuity anchors; dependency-based organization with a compact default and optional full-team responsibilities; optional environment-probed conditional lessons, lifecycle metadata, scoped retrieval, and separate bounded method-change proposals; current primary-source notes and limitations; removal of speculative model rankings and benchmark claims.

Review found and corrected material-ambiguity handling, preservation of explicitly selected hosted demonstrations, budget/pause/stop consistency, and rounding of small review reserves. The standard skill validator and reference, YAML, and archive checks passed. Independent prompt-mode QA preserved an 8-review user budget and local-only scope. This was release QA, not a performance benchmark.

## Earlier versions

v3 added explicit piece budgets, verdict records, isolation, role and model controls, and a run log. v2 added team and shared-knowledge governance, delivery gates, and optional auditable language procedures. See [lineage](LINEAGE.md) and [research/historical-lineage.md](../research/historical-lineage.md). Historical descriptions are retained as provenance; they are not proof that their proposed experiments ran.
