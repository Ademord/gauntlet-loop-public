# R2 verdict: scenario probes, consistency, backward compatibility (round 1)

Critic: Agent tool subagent `critic-r2-probes`, fresh context, model self-reported `claude-fable-5-1`. Inputs: versions/v4/ (8 files), skill/ (8 files), probes.md, plus the six arXiv abstracts fetched by the critic. Returned 2026-09-17, about 7 minutes, 175k subagent tokens (harness-reported).

```yaml
run_id: v5-upgrade-2026-09-17
piece_id: A
review_id: R2-probes
comparison: { mode: nonblind-preference, order: "bar read first, then ours" }
winner: ours
reason: v5 gives a concrete, source-aligned instruction on all six probes where v4 is silent or ambiguous, but reading its eight files as one rule set exposes one mechanical deadlock and five underspecified rule conflicts, so the win is incomplete under its own acceptance rule.
biggest_gap: Only `active` lessons are ever retrieved while `active` status requires a utility-ledger benefit earned by being retrieved in another run, so no lesson can ever activate.
biggest_gap_class: deterministic
blocking_findings:
  - "C5-1 [deterministic] lesson activation deadlock (learning L61/L63, SKILL L71 vs learning L45, SKILL L71)"
  - "C5-2 [deterministic] 'change it only at stall diagnosis or user request; de-escalate ...' names a third trigger the 'only' excludes; de-escalation has no recording location"
  - "C5-3 [judgment] ladder 'cannot block acceptance' vs HOLD 'lead prevents acceptance'; judgment-only HOLD at review 3+ unstated"
  - "C5-4 [judgment] review index under parallel critics: three concurrent critics put the third on advisory before any revision; corroborating order-swapped review consumes an index"
  - "C5-5 [judgment] retrieval allowance per piece vs run-level frozen selection; observation-triggered retrieval mid-run unstated"
  - "C5-6 [judgment] withhold parks as blocked_external or paused_user, but an invalid-checkpoint withhold is neither"
advisory_findings:
  - "[judgment] at review 3+ on a judgment-only piece, winner bar/none still blocks; the only exit (corroborate or park) is unstated"
  - "[judgment] SKILL L73 exceptions omit the resume amendment introduced at execution-contract L153"
  - "[judgment] critic inputs at SKILL L50 omit the retained best candidate that drift_vs_best requires"
  - "[judgment] retrieval_priority lowered has no stated effect in the ranking"
  - "[judgment] split children after review 2 start advisory"
  - "[deterministic] blocking_findings entries carry no class field"
  - "[deterministic] evidence-class enum lacks unknown, so v4 records cannot be classed honestly"
  - "[judgment] v4 active lessons with empty ledgers are not grandfathered"
  - "[external] ICML abstract supports delayed reward but not penalizing unhelpful retrievals; demotion is v5's inference"
  - "[deterministic] length: +18% words excluding research-basis (which doubled); template 311 to 398 words"
  - "[judgment] PipeSwift-derived sentences add words for a thin transfer"
checks:
  - { id: C4-scenario-probes, status: passed, evidence_class: judgment, observed: "6 of 6 pass; P6 passes on the accounting half only; P4 concrete but promotion unreachable under C5-1" }
  - { id: C5-consistency, status: failed, evidence_class: judgment, observed: "6 contradictions (2 deterministic, 4 judgment) plus 5 underspecifications" }
  - { id: C6-backward-compatibility, status: passed, evidence_class: deterministic, observed: "diff additive in every schema; budget section byte-identical; 8-review cap still soft 6 reserve 2; two default gaps advisory" }
hold: { active: false, finding_ids: [] }
drift_vs_best: "No v4 rule removed; cost is +18% length ex research and the six rule conflicts."
next_action: "Fix C5-1 (retrieve experimental lessons under the same allowance), then one sentence each for C5-2..C5-6; rejudge C5 only."
```

Per-probe table (critic's own words, condensed): P1 pass (v4 ambiguous on whether an opinion-only gap is "evidenced"; v5 SKILL L53, contract L89/L91 concrete). P2 pass (v4 same answer for both requests; v5 records estimate, class, topology, reason; (a) light, (b) compact). P3 pass (v4 no count or cost; v5 three-lesson allowance with events). P4 pass on C4, blocked by C5-1. P5 pass (v4 concrete on hash, silent on skill change and retroactive validation; v5 schema and rule). P6 pass on accounting only; dispatch half already in v4.

Lead disposition (round 2): C5-1 fixed by retrieving `active` and `experimental` lessons from the frozen pool under the same allowance, experimental labeled and non-binding. C5-2 fixed: "Choose the lightest topology whose gate is met"; three triggers listed with "only" applied to escalation; light exit on `bar`/`none`/failed check; de-escalation is a recorded event. C5-3 fixed: judgment-only HOLD from round 3 is advisory, must still name a discriminating observation. C5-4 fixed: index counts review rounds; parallel critics share one index; corroborating comparison does not advance it; lineage rule for slices. C5-5 fixed: frozen selection is the run pool, per-piece takes at most three from it, light trigger test draws from the pool. C5-6 fixed: new state `withheld_resume`. Advisories: exit from bar/none at round 3+ stated; SKILL L73 exceptions extended; critic inputs include retained best; `lowered` sorts last; class comment on blocking_findings; `unknown` class for pre-5.0.0 records; v4 active lessons grandfathered; split-children rule replaced by lineage rule. Not acted on: PipeSwift sentence in SKILL.md removed (kept in team-method); the ICML inference is already framed as "motivates".
