# Using the research program

Start with the [index](README.md). Pick one unanswered decision; the fifty milestones are a conditional queue, not fifty experiments to fund.

| Record | Authority |
| --- | --- |
| [MILESTONES-50.json](MILESTONES-50.json) | Stable `M-…` IDs, six investor questions, dependencies, research/native support and workflow state |
| [evidence.json](evidence.json) | Observations, exact scopes established, source IDs, artifact hashes and limitations |
| `experiments/EXP-…/plan.json` | One comparison, prerequisites, metrics, inputs and budget |
| `experiments/EXP-…/frozen.json` | Immutable plan, relevant claim/evidence/source snapshots, driver and input hashes |
| `experiments/EXP-…/result.json` | Immutable outcomes, losses, exclusions, full cost categories and scoped decision |
| [materials/native-overlap.json](materials/native-overlap.json) | Twelve anchored clauses, native overlap judgments and proposed behavioral probes |
| [materials/OVL-001/change.json](materials/OVL-001/change.json) | One concrete sentence-removal proposal and both candidate texts |
| [README.md](README.md), [MILESTONES-50.md](MILESTONES-50.md) | Generated views; edit their JSON records, then render |

Existing version archives, calibration runs, paper notes and the [backlog](backlog.md) remain evidence/provenance. A `related_backlog_ids` link connects an older proposal to a current milestone.

Choose ordinary tasks with the [task-selection policy](materials/task-selection.json): fresh user work first, frozen starting state and independent acceptance, a recorded eligibility queue, and explicit separation of development tasks from untouched confirmation. Its examples are task types, not admitted fresh tasks.

For ordinary work in a separate task, use the [passive observer](../../ledger/OBSERVER.md) outside the worker's context. Its records are observational and stay separate from frozen performance experiments. The [native smoke test](materials/observer-native-validation.json) verified Codex request/tool/completion capture and Claude request/failure capture; Claude's successful tool cycle remains blocked by usage credits. Enroll each selected task explicitly and preserve unknown coverage and costs. Human corrections and user-reported resolution are classified outside the worker context. Reviewed [checkpoint manifests](../../ledger/OBSERVER.md#git-checkpoints-and-agent-memory) preserve selected summaries while raw snapshots stay private.

## Inspect and prepare

Run from the repository root, using Python 3.10 or later. No additional packages are needed.

```text
python tools/program.py validate
python tools/program.py next
python tools/program.py list --state open
python tools/program.py show M-031
python tools/program.py readiness EXP-031-033-002
```

`next` lists research work whose declared dependencies and evidence permit consideration. It does not authorize or dispatch experiments. `readiness` checks a concrete experiment separately.

To open a new experiment, choose an unused ID:

```text
python tools/program.py prepare EXP-031-033-003 M-031 M-033
```

Fill its six questions: exact claim, competent comparator, stop/advance rule, losses to check, complete cost accounting, and the decision enabled by the next expenditure. Specify actual inputs and metrics. A generated draft cannot be frozen as-is.

Each prerequisite names a `required_scope`; at least one cited evidence record must explicitly `establishes` that scope. `satisfied: true` alone is insufficient. Documentation of native availability cannot establish tested runtime behavior.

## Freeze, execute, record

The only executable driver is `inventory_audit`: it checks clause/source identities and probe-record structure locally. It makes no model calls and performs no native behavioral probes.

```text
python tools/program.py readiness EXP-031-033-001
python tools/program.py freeze EXP-031-033-001
python tools/program.py run EXP-031-033-001
```

Those last two commands refuse overwrites once the seeded audit is frozen/recorded. Use a new experiment ID for an amended plan or repeat. The freeze stores fingerprints, not a complete copy of every input; retain source artifacts in version control. Changed treatment, evidence, sources or driver prevent execution under the old freeze.

`record EXP-ID path/to/result.json` validates and stores a result against its frozen plan. It never changes milestone status. The inventory driver enforces its fixed metric set, zero model/native-probe execution and inventory-only decision scope. Schema validation checks consistency; it cannot certify that a manually supplied observation is truthful.

The [removal comparison](experiments/EXP-031-033-002/plan.json) remains a draft. It needs a frozen native configuration, qualified controls, representative tasks/acceptance checks, and an accounting/price quote. Its external driver is intentionally unimplemented. The existing six-fixture Claude calibration is not a compatible runner for this comparison. Adding a driver requires its own implementation and verification before a paid experiment can be frozen.

## Change the plan when evidence changes

| State | Meaning |
| --- | --- |
| `reuse` | Prior work closes only the stated question |
| `verified_scope` | Linked engineering evidence checks the stated behavior |
| `partial` / `open` | Residual uncertainty remains |
| `deferred` | Do not investigate yet |
| `rejected` / `superseded` | Preserve the old decision and its evidence |

`queue` separately records `ready`, `blocked`, `deferred` or `closed`. Native availability and `performance_evidence` are separate fields. A successful pointer audit earns no performance promotion.

When a paper or product changes, update its source assessment and affected milestones. Set `review_status` to `contested` or `superseded` when appropriate; record a new evidence ID for a new observation. Preserve frozen/result records and negative outcomes. Change `checked_date` only after actually reviewing the source. Native-product sources have a thirty-day review reminder, a maintenance policy rather than a guarantee that their contents remain current.

Artifact drift and overdue/contested sources appear as validation warnings so historical records remain readable; reuse and execution are blocked where that evidence is required. Do not silence drift by blindly replacing hashes: inspect the change and record its new scope first.

After edits:

```text
python tools/program.py validate
python tools/program.py render
python tools/program.py render --check
python -m unittest discover -s tests -v
python tools/verify_release.py
```

Changing the shipped skill follows [CONTRIBUTING.md](../../CONTRIBUTING.md). A research plan or proposal does not adopt that change.

## Reading proposed allowances

Acceptance means independently accepted tasks divided by all started eligible tasks; failures/timeouts remain unaccepted. Report exclusions and unstarted tasks. Cost per acceptance includes every attributable attempt, agent, tool, retry and escalation; it is undefined when no task is accepted. Report end-to-end delivery time and observed human effort separately.

**G** is a proposed exploratory funding gate: preselect either one net additional acceptance among four paired tasks without higher cost per acceptance, or at least 25% lower cost per acceptance with no fewer acceptances. Both require no new critical regression or concealed human repair. This is a practical screening choice, not statistical proof or a literature-derived effect.

| Code | Proposed allowance; never a current price quote |
| --- | --- |
| L | No new solver benchmark; initially up to thirty minutes additional analysis |
| S | Conditional $24 execution screen: four pairs at provisional $3/run, plus one investigator hour |
| B | Prior conditional $46 ceiling: $10 readiness plus up to four tasks × three distinct arms × $3; three investigator hours |
| Q | Obtain a separate scope and quote; prior $36 confirmation reservation remains deferred |

Collapse equivalent arms. Quote realistic tasks before execution. Record unsuccessful runs, preparation, evaluation, research and human time; unknown actual costs are JSON `null`, never zero. Earlier calibration usage of about $5.77 was execution usage, not the full research cost. Budget fields record allocations; they do not enforce external billing limits or dispatch work.
