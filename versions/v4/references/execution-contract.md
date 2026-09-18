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
blocking_findings: [] # include all unresolved required failures
checks:
  - id: requirement-check-id
    status: blocked # passed | failed | blocked | not selected | not applicable
    expected: observable-requirement
    observed: actual-result-or-what-is-missing
    evidence: [] # specific files, commands/results, source locations, or URLs
hold:
  active: false
  finding_ids: []
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

## HOLD and uncertainty

Any critic can flag a specific acceptance claim with its artifact, evidence, suspected mismatch, and the next observation that would resolve it. Label unconfirmed uncertainty as provisional. The lead prevents acceptance of the affected claim while keeping unrelated work moving.

Resolve each HOLD explicitly as upheld/fixed, dismissed with reproducible counterevidence, or superseded by an authorized scope change. Keep the finding and disposition. A new agent, a newer artifact, or many agreeing messages does not erase it. If the lead's own claim is disputed, obtain a fresh review. Do not repeat judging until a favorable answer appears.

## Budget semantics

These defaults are adjustable engineering guardrails:

| Scope | Soft reviews | Hard reviews | Soft observable requests | Hard observable requests |
| --- | ---: | ---: | ---: | ---: |
| Each piece | 6 | 9 | 120 | 180 |
| Whole run, including integration | 24 | 30 | 480 | 600 |

The last 6 shared reviews and 120 observable requests are reserved inside the hard run ceiling for integration, required verification, and handoff. They are not extra budget. A user's tighter cap wins. For a smaller positive integer review cap H, reserve ceil(0.2 * H) reviews within H and set the run soft point to H minus that reserve, unless the user set a different allocation. Thus an 8-review cap has a soft point of 6 and a reserve of 2. A single-review allowance supports one bounded build and final review; a zero-review allowance cannot establish independent acceptance. Scale a smaller observable request allowance in the same way. Explicitly larger or unlimited user allowances override these defaults and are recorded. Do not infer a spend authorization from the default ceiling.

A review is one dispatched critic attempt, including an inconclusive or failed attempt. Additional critics and order-swapped reviews each count. Builder self-checks do not count as critic reviews, but their model requests count when visible. Shared request usage includes lead, builders, critics, reconnaissance, curation, failed calls, and retries visible to the harness. Count reservations before dispatch so concurrent agents cannot each spend the same remainder. Return unused reservations only when the worker is confirmed stopped. Record uncertainty when telemetry is incomplete.

At a piece soft limit, finish the current bounded attempt within the hard allowance and judge whether another attempt has a concrete path to closing the gap. Continue only within the existing run and piece caps. Otherwise park that piece and use remaining capacity on independent obligations. At the run soft limit, stop starting optional work or fresh search rounds: converge on the best candidates, integration, required corrections that fit the reserve, and handoff. At a hard limit, dispatch no further work against that allowance. Preserve state and report incomplete work. Never spend an unobservable request allowance as though it were known; keep the observable review cap and disclose missing request telemetry.

If no reliable token/cost/request counter exists, state that review counts are manually bounded and cost is unknown. Limit each dispatched assignment to a concrete artifact and handoff; do not give workers unbounded exploration. A review cap cannot promise a dollar or token cap. Honor user stops and account controls immediately. If the host has a separate goal/status tool, follow its own transition rules; these record labels do not grant tool authority.

Split children share their parent's unspent allowance; renamed pieces, resumed sessions, model changes, and restarts retain ledger ancestry. Neither decomposition nor a new run ID may bypass a still-active user ceiling. An authorized new allowance needs a recorded change with old/spent/new/remaining values.

## Stall diagnosis and candidate retention

After two successive verdicts repeat the same unresolved gap without supporting evidence of progress, pause edits to identify the bottleneck. Check for a bad oracle, missing inputs, dependency failure, unsuitable approach, insufficient model capability, or unreachable bar. Choose one evidence-producing next step, a different bounded approach, a smaller slice sharing its parent's budget, or an authorized model fallback. Do not lower the bar or spin up a larger team to avoid diagnosis.

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

On resume, verify relevant files/revisions, read unresolved evidence, reconcile changed external state, and confirm ownership before dispatch. Keep existing budget charges and holds. If checkpoint and artifact disagree, record the discrepancy and reverify the affected scope; do not adopt the more flattering status. Recover a partial snapshot from valid events and actual artifacts. Investigate unknown external effects before a retry; cancellation is not proof of rollback.

## Milestone summary

Use states `accepted`, `in_progress`, `parked_budget`, `blocked_external`, `paused_user`, and `stopped_user` for pieces/run records as appropriate. A dependency on a parked piece stays incomplete with that dependency named. These states are distinct from verdict/check status and from any platform's goal status enum.

Record run/skill/contract identity, current delivered identity, accepted and incomplete pieces, review counts, user limits, observable time/usage, unknown telemetry, verdict/evidence links, blockers, and next action. Later defects are `not assessed` unless actually inspected; do not schedule a seven-day follow-up by default. Save pending work, stop workers, release ownership, and schedule nothing unless requested. Local preparation, integrated acceptance, and remote delivery remain separate claims.
