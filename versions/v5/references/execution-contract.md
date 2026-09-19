# Execution contract, verdicts, budgets, and recovery

Read for execution or resumption. Keep the record proportional: reuse equivalent project files instead of creating a second system. This contract describes agent behavior; use real permission, test-protection, and budget controls where the harness provides them, and disclose when enforcement is manual.

## Durable records

A useful layout is `gauntlet/<run-id>/contract.yaml`, `events.jsonl`, `state.yaml`, and `evidence/`, with a human-readable `progress.md` and a milestone summary in `gauntlet/runs.jsonl`. Equivalent Markdown tables or existing project records are fine. Do not create empty record collections or tooling solely to imitate this layout.

The contract records:

- Run ID, skill version, outcome, audience, scope/non-goals, and stopping milestone.
- Reference snapshot ID, source and retrieval time, comparison dimension, and relevant conditions.
- Required check IDs, expected outcomes, requirement sources, applicability, and criteria version/hash.
- Selected delivery targets, approved audience, existing authorization, and genuine missing capabilities.
- Harness and actual model/effort per role when observable; ownership and dependency edges.
- User limits and explicit overrides, per-piece and shared allowances, integration reserve, accounting method, and enforceable versus estimated limits.
- Selected lesson IDs/versions when enabled, mutable-state locations, and current artifact identity.
- Difficulty estimate with its observable proxies, the verifiability class of the required checks, and the topology decision with its reason and any later change.

Capture a starting artifact before editing. Use a commit plus dirty-diff/untracked-input identity, or an immutable copy/content manifest for non-Git work. HEAD alone cannot identify a dirty checkout. For external state include the resource/revision and observed time. Never hash or copy secrets into evidence; scope manifests to relevant authorized inputs.

## Acceptance checks and changing expectations

Each check has an ID, requirement source, expected observation, scope, and status. Available statuses are `passed`, `failed`, `blocked`, `not selected`, and `not applicable`. A selected check with no evidence is `blocked` with the missing verification stated. Lack of tools is not `not applicable`.

Builders can create implementation tests and propose acceptance-test corrections. They cannot silently remove required cases, relax assertions, mark failures skipped, or edit evidence to obtain approval. Review a claimed oracle bug against the requirement and a discriminating example, preserve the old check/result, and version a legitimate correction independently of the builder's desired verdict. Ask for the user's decision when ambiguity materially changes scope or acceptance; otherwise use a stated reversible assumption where appropriate. Repairing a proven fixture typo within the same expectation needs no new product decision.

Where possible, give builders read access to acceptance expectations and keep acceptance artifacts separately owned or technically protected. A read-only convention is not access enforcement. Do not hide product requirements under the label of independence. A frozen check set can gain a newly discovered requirement-derived test through a recorded version change; it cannot silently gain unrelated scope.

## Verdict record

The following is a schema illustration; fill it with actual IDs and evidence. Nulls are allowed only where the explanation says the value is unavailable, not as a substitute for required verification.

```yaml
run_id: run-identifier
piece_id: piece-identifier
review_id: unique-review-identifier
artifact:
  identity: commit-plus-content-manifest-or-artifact-hash
  location: candidate-path-or-resource
reference:
  identity: captured-reference-version
  location: reference-evidence-path
criteria_version: checks-version-or-hash
reviewer:
  id: independent-reviewer-identifier
  model: unknown
  independence: separate-context
comparison:
  mode: blind-preference # or nonblind-preference or behavioral
  order: recorded-presentation-order-or-not-applicable
winner: none # ours | bar | none
reason: evidence-based-comparison-reason
biggest_gap: most-important-next-gap-or-no-remaining-gap
biggest_gap_class: judgment # deterministic | external | judgment; unknown only in records made before 5.0.0
blocking_findings: [] # each entry names its finding, its evidence class, and its evidence; include all unresolved required failures
advisory_findings: [] # uncorroborated judgment findings recorded from the third review round on
checks:
  - id: requirement-check-id
    status: blocked # passed | failed | blocked | not selected | not applicable
    evidence_class: deterministic # deterministic | external | judgment; unknown only in records made before 5.0.0
    expected: observable-requirement
    observed: actual-result-or-what-is-missing
    evidence: [] # specific files, commands/results, source locations, or URLs
hold:
  active: false
  finding_ids: []
drift_vs_best: none # or the named hedging, clarity, or scope regression against the retained best candidate
ladder:
  piece_review_index: 1
  judgment_may_force_revision: true # false from the third review round on unless corroborated
evidence: [] # must identify actual inspection; empty evidence cannot support acceptance
budget:
  piece_reviews_used: 1
  run_reviews_used: 1
  model_requests_used: null # null means unobservable
  accounting: review-counted-requests-unobservable
next_action: concrete-action-or-deliver
```

The lead validates artifact/reference/criteria identities, independence, evidence coverage, HOLD disposition, and check statuses before acceptance. `winner: ours` with a failed required check is still incomplete. `winner: none` preserves uncertainty and is not accepted. A behavioral comparison can favor a repaired candidate over the failing baseline when independent checks demonstrate the agreed correction without required regressions; no stylistic superiority claim is needed.

The critic independently inspects or reproduces the relevant checks on the reviewed artifact; it does not copy builder status labels. Record the command or interaction, environment/fixture, expected and actual result, time, and artifact identity. Relevant independently produced CI can be inspected as evidence when its jobs and identity are verified. Reuse a prior check only when its inputs and dependency scope are demonstrably unchanged, and record why. Integration still needs the affected full journey checked.

## Evidence classes and the revision ladder

Every finding, check result, and biggest gap carries an evidence class. `deterministic` comes from a compiler, test, calculation, rendering, or other reproducible procedure. `external` comes from a reference document, primary source, captured reference behavior, or live system observation. `judgment` is a critic's preference or reading, however expert. Class by the observation that produced the finding, not by its importance.

A review round is one or more critics reviewing the same candidate identity; parallel critics in one round share one index, and the piece's review index counts rounds. In a piece's first two rounds any class may be the biggest gap and may drive a revision. From the third round on, a `judgment` finding is advisory unless corroborated: it is recorded in `advisory_findings`, it cannot be the biggest gap, it cannot force a revision, and it cannot block acceptance, including when raised as a HOLD. Corroboration means a discriminating observation that changes the class, or a second independent critic preferring the change in an order-swapped comparison; that corroborating comparison counts against the budget but does not advance the index. Required checks keep their own status regardless of class; the ladder limits what opinion can compel, not what evidence can reject. A `winner: bar` or `none` verdict still withholds acceptance; from the third round on, the lead's exits from such a verdict are a corroborating observation, a required-check fix, a stall-diagnosis step (a different bounded approach, a smaller slice, or an authorized fallback), or parking the piece.

Each review also compares the candidate against the retained best candidate on the comparison dimension and records `drift_vs_best`: added hedging or qualifiers, lost clarity, lost scope, or regressions the bar comparison would not show. Drift is a `judgment` finding unless a check demonstrates it. The lead keeps the best candidate; a revision that only reshuffles prose ends the loop for that gap. The ladder is an engineering rule motivated by the research basis, not a measured optimum. The index follows the candidate's lineage: revisions of the same artifact advance it, resumption does not reset it, and a genuinely new slice starts at one; re-slicing the same artifact to reset the ladder is a budget-continuity violation.

## HOLD and uncertainty

Any critic can flag a specific acceptance claim with its artifact, evidence, suspected mismatch, and the next observation that would resolve it. Label unconfirmed uncertainty as provisional. The lead prevents acceptance of the affected claim while keeping unrelated work moving. From the third review round on, a HOLD grounded only in uncorroborated judgment is instead recorded as advisory and does not block (see the ladder above); every HOLD still names its discriminating next observation.

Resolve each HOLD explicitly as upheld/fixed, dismissed with reproducible counterevidence, recorded as advisory under the ladder, or superseded by an authorized scope change. Keep the finding and disposition. A new agent, a newer artifact, or many agreeing messages does not erase it. If the lead's own claim is disputed, obtain a fresh review. Do not repeat judging until a favorable answer appears.

## Budget semantics

These defaults are adjustable engineering guardrails:

| Scope | Soft reviews | Hard reviews | Soft observable requests | Hard observable requests |
| --- | ---: | ---: | ---: | ---: |
| Each piece | 6 | 9 | 120 | 180 |
| Whole run, including integration | 24 | 30 | 480 | 600 |

The last 6 shared reviews and 120 observable requests are reserved inside the hard run ceiling for integration, required verification, and handoff. They are not extra budget. A user's tighter cap wins. For a smaller positive integer review cap H, reserve ceil(0.2 * H) reviews within H and set the run soft point to H minus that reserve, unless the user set a different allocation. Thus an 8-review cap has a soft point of 6 and a reserve of 2. A per-piece limit never exceeds the run's remaining hard allowance: under a run cap H below the per-piece defaults, the per-piece hard limit is min(9, H minus the reserve) and the soft limit is min(6, that hard limit), so no single piece can spend the reserve; under small caps the two may coincide, and at H = 1 the only review is the reserved final review. A cap stated only in reviews leaves the request allowance at its default; state both when both matter. A single-review allowance supports one bounded build and final review; a zero-review allowance cannot establish independent acceptance. Scale a smaller observable request allowance in the same way. Explicitly larger or unlimited user allowances override these defaults and are recorded. Do not infer a spend authorization from the default ceiling.

A review is one dispatched critic attempt, including an inconclusive or failed attempt. Additional critics and order-swapped reviews each count. Builder self-checks do not count as critic reviews, but their model requests count when visible. Shared request usage includes lead, builders, critics, reconnaissance, curation, failed calls, and retries visible to the harness. Count reservations before dispatch so concurrent agents cannot each spend the same remainder. Return unused reservations only when the worker is confirmed stopped. Record uncertainty when telemetry is incomplete.

At a piece soft limit, finish the current bounded attempt within the hard allowance and judge whether another attempt has a concrete path to closing the gap. Continue only within the existing run and piece caps. Otherwise park that piece and use remaining capacity on independent obligations. At the run soft limit, stop starting optional work or fresh search rounds: converge on the best candidates, integration, required corrections that fit the reserve, and handoff. At a hard limit, dispatch no further work against that allowance. Preserve state and report incomplete work. Never spend an unobservable request allowance as though it were known; keep the observable review cap and disclose missing request telemetry.

If no reliable token/cost/request counter exists, state that review counts are manually bounded and cost is unknown. Limit each dispatched assignment to a concrete artifact and handoff; do not give workers unbounded exploration. A review cap cannot promise a dollar or token cap. Honor user stops and account controls immediately. If the host has a separate goal/status tool, follow its own transition rules; these record labels do not grant tool authority.

Split children share their parent's unspent allowance; renamed pieces, resumed sessions, model changes, and restarts retain ledger ancestry. Neither decomposition nor a new run ID may bypass a still-active user ceiling. An authorized new allowance needs a recorded change with old/spent/new/remaining values.

## Stall diagnosis and candidate retention

After two successive verdicts repeat the same unresolved gap without supporting evidence of progress, pause edits to identify the bottleneck. Check for a bad oracle, missing inputs, dependency failure, unsuitable approach, insufficient model capability, or unreachable bar. Choose one evidence-producing next step, a different bounded approach, a smaller slice sharing its parent's budget, or an authorized model fallback. Do not lower the bar or spin up a larger team to avoid diagnosis. Escalating topology needs this diagnosis, recorded with its reason and the remaining allowance, with two exceptions: a user request, and a `light` piece whose single review does not accept (winner `bar` or `none`, or a failed required check), which escalates to `compact` on that verdict alone. De-escalation is a recorded event with its reason. Delegation and decomposition do not refill the piece's budget.

Retain the strongest independently reviewed candidate and viable alternatives when they represent meaningful tradeoffs. Record wins, failed checks, and provenance; "best" does not mean accepted. Restore a saved candidate only into the owned workspace or by a reviewed patch. Never overwrite user changes or silently undo selected newer requirements. An older candidate must still meet the current contract and receive affected integration checks.

## Checkpoint and resume

The lead owns checkpoint writes; workers return structured handoffs. Append factual events with IDs and evidence pointers, then update a derived current-state record. Prefer write-to-temp and replace for the state snapshot where supported. Preserve prior valid state if interrupted. Append-only here is a recordkeeping convention, not a claim of tamper-proof storage.

Checkpoint after every verdict, before integration or ownership transfer, and at pause/stop. Include:

- Latest event, run/piece IDs and parent budgets; skill, contract, reference, criteria, and lesson versions.
- Current and best candidate paths/identities; branches, patches, dirty work, and relevant executable state.
- All required obligations, selected deliveries, latest verdict/evidence, pending or invalidated checks.
- HOLDs, unresolved commitments, dependencies, parked work, and external blockers.
- Spent/reserved/remaining allowances, accounting limits, active owners/workers, and next concrete action.
- Dispatched external actions and whether their effects are confirmed, failed, or unknown.
- Run start time, per-piece completion times, and each piece's review index, or `unknown`.

On resume, write a resume validation record before any dispatch. Verify relevant files/revisions, read unresolved evidence, reconcile changed external state, confirm ownership, and re-read the authorization the checkpoint relied on. Keep existing budget charges and holds. If checkpoint and artifact disagree, record the discrepancy and reverify the affected scope; do not adopt the more flattering status. Recover a partial snapshot from valid events and actual artifacts. Investigate unknown external effects before a retry; cancellation is not proof of rollback.

```yaml
resume_validation:
  checkpoint_id: latest-checkpoint-event-id
  artifact_identity: match # match | mismatch
  versions: { contract: match, criteria: match, skill: mismatch, lessons: match } # match | mismatch | unknown
  authorization: valid # valid | changed | unknown; user limits, delivery audience, access
  external_effects: confirmed # confirmed | failed | unknown
  holds_carried: []
  decision: repair-then-resume # resume | repair-then-resume | restart-from-evidence | withhold
  permitted_actions: [reverify-affected-checks, amend-contract-for-skill-version]
  reason: evidence-based-reason
```

`resume` continues from the checkpoint. `repair-then-resume` first performs the listed permitted actions, such as reverifying claims whose inputs changed. `restart-from-evidence` discards the checkpoint's derived state and rebuilds it from events and actual artifacts. `withhold` parks the run as `withheld_resume` with the missing evidence named, or as `blocked_external` or `paused_user` when that is the actual cause. A skill, harness, or model change since the checkpoint is a recorded contract amendment: affected accepted claims are marked for revalidation, and any comparison that spans the change says so. A later successful acceptance never validates a resume recorded as invalid; the resume decision is evaluated on its own evidence.

## Milestone summary

Use states `accepted`, `in_progress`, `parked_budget`, `blocked_external`, `withheld_resume`, `paused_user`, and `stopped_user` for pieces/run records as appropriate. A dependency on a parked piece stays incomplete with that dependency named. These states are distinct from verdict/check status and from any platform's goal status enum.

Record run/skill/contract identity, current delivered identity, accepted and incomplete pieces, review counts, user limits, observable time/usage, unknown telemetry, verdict/evidence links, blockers, and next action. Also record the difficulty estimate and its proxies, the verifiability class, the topology and any change with its reason, reviews used per piece and how many were advisory-only, wall-clock from run start to stop, and, when learning is enabled, the lessons retrieved with their ledger outcomes. These fields are observational; they exist so that later analysis across runs can ask which topology and how much review a task of this kind actually needed. Later defects are `not assessed` unless actually inspected; do not schedule a seven-day follow-up by default. Save pending work, stop workers, release ownership, and schedule nothing unless requested. Local preparation, integrated acceptance, and remote delivery remain separate claims.
