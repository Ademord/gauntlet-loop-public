# First graph-pattern implementation

**P002, 21 September 2026.** [Indexed result](P002-implementation.json), following [GRAPH-001](GRAPH-001.json) and [SVQ-001](../readiness/SVQ-001.json).

The existing private application controller is repaired and its package is now 1.1.4. A new pure planner returns one next action from a supplied snapshot. Opus 5/xhigh implemented it with the qualified static-validation tool. Independent code review and all **15 frozen test methods** passed before integration; the full canonical package hash check passed afterward.

The implemented patterns are a fixed dependency graph, a join requiring both current parents, explicit unknown/error routes, and deterministic next-action selection. The controller rejects unknown stages even with a force override. The planner checks artifact bindings transitively, routes uncertain submission records to reconciliation, and keeps the existing combined letter/form review after prefilling. It proposes actions only: it does not fetch live state, execute a stage, control a browser, submit an application or update the tracker.

| Investor question | This increment's answer |
| --- | --- |
| Exact claim? | The named parser works through the worker interface, and the planner meets the frozen routing contract on synthetic fixtures. |
| Compared with what? | The inspected original controller could not parse. No equally equipped native-agent comparison was run; no orchestration advantage is inferred. |
| Stop rule? | One build plus at most one bounded repair; reject a failing candidate. Build cap $4/900 seconds, optional repair $2/600 seconds; dollar caps are soft. |
| Where did it lose? | General execution remains unqualified. No live snapshot adapter or effect executor exists. Recording needed an explicit raw-byte versus normalized-text hash reconciliation. |
| What did it cost? | **$2.693950 CLI-reported API-equivalent execution usage**, 621,882 native tokens including smoke and all attempts; 0 controller-to-worker repairs. Preparation, evaluation, cash billing and human time remain unpriced. |
| What next decision does it enable? | Whether a read-only adapter can supply current, attributable job evidence without converting missing data into readiness. |

The evaluator was frozen before the worker began. Tests include valid advancement, stale joins, transitive invalidation, unknown external status, missing facts/login, prior and uncertain submissions, malformed inputs, replay identity and no observed fixture-file effects. Narrow controller tests use synthetic config and a no-op checks dependency. These results do not certify the complete live pipeline or semantic truth of supplied evidence. One explicit contract boundary remains: an H7 failed/unknown marker alone does not trigger reconciliation. Define that recovery rule before connecting an executor.

The controller performed preplanned manifest packaging from reviewed worker bytes. That is separate from worker repairs. Native transcripts, enrollment, artifact hashes, independent outcomes and contact classifications remain private. User-confirmed resolution stays unknown. Successful delivery on this task does not establish that validation caused fewer corrections than P001; the tasks differ.

Gauntlet's **147-test** suite passed with one native symlink fixture skipped. The static tool is documented in [STATIC-VALIDATION.md](../../../ledger/STATIC-VALIDATION.md). MAQ-001 stays blocked; the general sandbox and P001 discovery/skill-validation gaps are not silently marked complete. No research milestone was promoted and no graph framework was installed.
