# P011 — recorder coverage and accounting

**The selected recent tasks were not recorded by this observer.** All six selected other Codex tasks and the current controller were unenrolled, with no stored events. This is a bounded sample checked against an independent task inventory, not a census or evidence that no work occurred elsewhere.

A consistent private snapshot contained 15 enrolled sessions (14 Claude, one Codex), 417 events, 45 null measurement values, 14 contact-label rows, no resolution rows and 12 outcome rows. Two known enrolled positive controls returned 10 and 26 events, while the selected tasks and controller remained absent; the snapshot stayed unchanged. Label rows can include revisions; outcome rows are supplied assessments. These counts do not establish human corrections, unresolved work or complete acceptance.

The three frozen collector modules matched the repository. Nine Codex and ten Claude hook definitions were configured. Installed hooks do not enroll every task: the existing adapter registers a known session or consumes one expiring enrollment for the next matching host/directory start. Unregistered sessions are ignored. Eight generic errors were present in the shared bounded diagnostic log; their session attribution and relation to missing tasks are unknown. Configuration presence is not current invocation or trust proof.

| Accounting component | Existing source | What remains unknown |
| --- | --- | --- |
| Selected tasks and controller | Task inventory versus recorder snapshot | All seven selected identities are unenrolled; earlier work cannot be recovered from this recorder. |
| Historical P008 worker | [Saved P008 accounting](../architecture/P008-validated-drafting.json): $1.2040785, 271,938 tokens, 229.016 seconds | Worker execution only, not full cost or subscription billing; not a new P011 charge. |
| Controller, review, preparation and retries | Existing checkpoint descriptions | Complete attributable cost and labor; activity descriptions are not metering. |
| Descendants | Lifecycle metadata when supplied | Complete coverage and inclusive/exclusive usage attribution; do not add overlapping totals. |
| Human corrections and minutes | Captured labels and reported measurements | Classifier identity is not prompt authorship. Controller repairs are not established human corrections; active time is not elapsed message time. |
| User resolution and acceptance | Zero resolution rows; 12 outcome rows | Explicit user resolution and complete independent acceptance coverage; neither follows from Stop events. |

The new [read-only coverage command](../../../tools/observer_coverage.py) queries the existing observer and exports aliases and aggregates. It does not enroll tasks or initialize contact tables. Its corrected independent probe passed **8/8 fixture groups**, and independent code/privacy review accepted the scoped audit. The initial run had zero assertion failures but seven Windows cleanup errors because fixture SQLite connections remained open. The evaluator correction closes those connections; assertions, criteria and candidate bytes are unchanged, and the original failure remains recorded. These offline checks do not qualify current native capture.

| Investor question | This increment |
| --- | --- |
| Exact claim | Establish enrollment and accounting coverage for a specified task sample using existing evidence. |
| Compared with what? | Independent task identities versus a consistent database snapshot and exact installed collector code; no agent-performance comparison. |
| Stop condition | Preserve missing coverage and cost as unknown. No backdated enrollment, invented history, automatic follow-up-to-correction conversion or paid comparison. |
| Where did it lose? | The six sampled other tasks and controller were missed. Stored usage is entirely null; human origin, resolution and descendant attribution remain incomplete. Fixture cleanup failed before the corrected rerun. |
| Real cost | No new benchmark worker run. Controller, review, preparation and human cost remain unknown, not zero. Prior worker usage is not counted twice. |
| Next expenditure | Once future recording scope is chosen, use the existing enrollment interface and verify actual capture before a benchmark. |

The choice between all future local tasks and selected tasks remains pending; current explicit enrollment is unchanged. No broad collection, retrospective reconstruction, installed-runtime change or public push occurred. This is a local checkpoint, not a performance result or milestone promotion. It follows [P010's accounting requirement](P010-CHECKED-EXPORT.md); the [machine-readable report](P011-recorder-coverage.json) keeps source hashes, unknowns and qualification status explicit.

Evidence: [coverage output](P011-coverage.json), [actual snapshot replay](P011-actual-replay.json), [independent snapshot review](P011-actual-review.json), [audit contract](P011-contract.json), [frozen criteria](P011-probe-criteria.json), [independent code review](P011-review.json), [corrected qualification](P011-qualification.json), and [preserved fixture correction](P011-probe-amendment.json). Original and corrected result identities remain distinct.

The public [portable probe](../../../tools/probes/observer_coverage_probe.py) exercises synthetic databases against the public audit command. Run it with `--candidate tools/observer_coverage.py --result NEW-RESULT.json --private-log PRIVATE-LOG.json`; keep its diagnostic output private. The real task identity mapping and database stay in the private checkpoint.
