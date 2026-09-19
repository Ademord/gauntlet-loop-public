# Optional grounded lessons and bounded method changes

Read only when cross-run learning or workflow improvement is selected. Ordinary delivery needs checkpoints and evidence, not a permanent memory service. Enabling project-local learning authorizes the procedures below within existing access; it does not authorize global skill edits, paid studies, background agents, or wider data collection.

## Keep three layers distinct

1. **Source record:** versioned artifacts, observed failures, commands/results, external observations, decisions, and concise factual events. Preserve the evidence needed to audit a conclusion, subject to the user's retention and privacy requirements. Never store credentials, hidden reasoning, or unrelated conversation history merely to make memory richer.
2. **Current state:** a derived view of commitments, constraints, accepted plans, unresolved findings, artifact identities, owners, and budgets. Prefer executable state such as repository files, validated configuration, schema, or constraint models when these are the thing being operated on. Do not build a solver or database just to replace a small status file.
3. **Working context:** the small subset of current state and lessons relevant to the present goal, environment version, dependency, and authority. Stored history is not automatically active guidance.

Keep source pointers in summaries. A new summary does not supersede a fact by itself. Superseded information can still answer a historical question, but it cannot silently direct present work. If retention rules require removal, honor them; "append-only" is not permission to retain sensitive data forever.

## Conditional lesson record

Use project methodology or a small collection of records. A graph is justified only after flat records demonstrably fail to express recurring dependencies; a graph database is never the default.

```yaml
id: stable-lesson-id
version: 1
kind: procedure # fact | procedure | coordination
scope: project-and-supported-environment
applies_when: observable-trigger
observation: what-actually-happened
cause_hypothesis: explanation-not-yet-established-or-null
procedure: bounded-action-to-take-when-applicable
verification: observable-check-that-could-disconfirm-the-claim
source_evidence: [run-and-artifact-evidence-pointer]
environment_probe:
  command_or_observation: read-only-check
  environment_identity: revision-or-resource-version
  result: observed-result
  checked_at: timestamp
reviewer: independent-reviewer-or-pending
status: candidate # candidate | experimental | active | disputed | superseded | invalidated | rejected | retired
valid_from: date-or-environment-version
recheck_when: dependency-change-or-expiry-trigger
supersedes: []
depends_on: []
contrary_evidence: []
admission_basis: none-until-reviewed
retrieval_priority: normal # normal | lowered
utility_ledger: [] # entries: {run, piece, retrieved_at, applied, outcome, evidence}; outcome is prevented_defect | reduced_rounds | neutral | irrelevant | harmful | unknown
```

The utility ledger records what happened after each retrieval, in the lead's attribution, with evidence. A `candidate` becomes `experimental` once its environment probe has run and a reviewer other than its author has checked its scope. Promotion from `experimental` to `active` needs the probe and review below plus at least one `prevented_defect` or `reduced_rounds` entry from a run other than the lesson's source run. Two consecutive `irrelevant` entries set `retrieval_priority: lowered` without changing status. One evidenced `harmful` entry moves the lesson to `disputed` and removes it from retrieval until reviewed. `lowered` priority sorts after every normal-priority lesson in retrieval ranking. Lessons already `active` before this version keep their status; their empty ledger reads as `unknown` until the next retrieval. Ledger outcomes are confounded by everything else in a run; they prioritize retrieval and gate promotion, they do not prove causal value.

Use an event or environment trigger for expiry when that is more meaningful than a calendar date. `active` always means active within the recorded scope, not a universal truth. Distinguish a failed attempted improvement (`rejected`) from a previously accepted claim shown wrong (`invalidated`) and a correct old version replaced by a new one (`superseded`). Keep their reasons so later agents do not rediscover the same rejected proposal without new evidence.

## Nominate, probe, review, admit

At a milestone, nominate a lesson only when a recurring failure or clearly reusable discovery warrants it. Separate observed facts from causal guesses. Narrow generic advice to a trigger, action, and falsifiable check; do not promote "be careful" or a model's confident explanation.

Probe the claim using available read-only environment access. Check that referenced paths exist in the named revision, commands are actually defined, interfaces behave as claimed, prerequisites hold, and older guidance has not become stale. Do not run a command as a "read-only probe" if it changes accounts, databases, deployments, or user state. A local isolated check can be run under normal task authorization, but record its side effects and evidence honestly.

If a required probe is unavailable, keep the lesson `candidate` or `experimental`, with the missing evidence. Absence of a contradiction is not verification. An independent reviewer checks the evidence and scope before activation; the lead can reuse an existing qualified critic instead of creating a curator department. Multiple agents copying one source remain one evidence source.

When project-local learning is enabled, verified factual/procedural discoveries can be admitted within that project under this recorded review process without asking permission for every entry. Admission confirms the scoped claim, not a general productivity gain. Claims that a procedure improves future performance remain hypotheses until supported by separate relevant use recorded in the utility ledger. Generalized workflow changes follow the separate process below.

## Retrieve narrowly and handle conflicts

Select active and experimental lessons by applicability, environment compatibility, validity, dependency status, and evidence freshness before semantic similarity. Read only the relevant subset; record selected IDs/versions in the run contract. Keep that selection frozen during the run.

Retrieval is budgeted. The frozen selection is the run's pool. By default at most three lessons from that pool enter a piece's working context, `active` before `experimental`, then ranked by applicability, validity, and evidence freshness, with `lowered` priority last; more needs a recorded reason. An `experimental` lesson is labeled as such in working context and can inform a hypothesis or diagnosis, not a required rule. Each retrieval is an event with the lesson ID/version, the selection reason, and its cost in observable tokens or `unknown`, charged against the piece's observable allowance where telemetry exists. A `light` topology piece retrieves nothing unless an observed condition matches the `applies_when` of a lesson in the pool; similarity alone does not qualify. Write each retrieval's outcome to the lesson's utility ledger at the piece verdict or the milestone. The allowance of three is an editable default, not a measurement; memory competes with reasoning, tests, and reference comparison for the same context. A newly proposed lesson can inform an explicitly labeled hypothesis or diagnosis, but cannot silently become a required rule or acceptance fact.

When a selected lesson conflicts with current observation, quarantine its affected use immediately, record the contradiction, notify dependent owners, and reverify affected claims. Do not keep applying stale guidance merely because the snapshot was frozen. This suspension is an evidence correction, not unreviewed promotion of a replacement. The underlying user requirement remains in force.

Neither recency nor popularity resolves a factual conflict by itself. Inspect scope, source identity, validity, and a discriminating observation. Mark downstream lessons disputed when a dependency is invalidated. Corrections propagate to the derived state and current consumers while the original evidence remains auditable. Summaries and project memories cannot override the live user's instructions or confer external authority.

## Bounded workflow-improvement proposals

Delivery changes the artifact. Method improvement changes how later deliveries run. Keep them separate, including separate candidate identity and evidence. A delivery run may nominate a proposal, but cannot install it into the workflow that is judging that same run.

For each proposal record the source failure, hypothesis, intended effect, permitted files/components, invariants, patch, parent version, prior snapshot, verification needed, contrary evidence, and rollback trigger. Start with the smallest meaningful edit: context packaging, a handoff field, retrieval filtering, or a task ordering rule. A broader redesign needs a concrete reason and authorized scope, not automatic escalation after a failed patch.

Exclude user goals, permissions, acceptance authority, grading criteria, protected checks, and budget controls from autonomous mutation. A request to update those things must come from the actual user or applicable higher-level instructions. Retain the incumbent and useful earlier snapshots; a candidate patch may be rejected or rolled back without losing the evidence that motivated it.

Check structural correctness and compatibility before proposing promotion. Claims of improved performance require separately authorized validation beyond the source example, including regressions and failed attempts; shared agreement is not measurement. Benchmark campaigns are deferred here: do not create arms, synthetic task suites, paid model calls, calibration runs, or statistical reports unless separately requested. A deferred candidate remains proposed while ordinary delivery continues.

Adopt global/installed skill changes only under a request to update that skill or an already configured, explicit authorization covering the exact mutation scope. Prepare a concrete reviewed patch before asking for genuinely missing authorization. Reuse that authorization when it exists. Version the adopted package, preserve rollback, and apply it to a new or explicitly amended run contract. Cosmetic coordination choices within an existing contract do not need a skill promotion ceremony.
