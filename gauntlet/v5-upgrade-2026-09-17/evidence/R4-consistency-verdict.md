# R4 verdict: consistency rejudge (round 2)

Critic: `critic-r2-probes` resumed with instructions to re-read the six changed files from disk; model self-reported `claude-fable-5-1`. Candidate identity: r2 (evidence/candidate-r2b-sha256.txt). Returned 2026-09-17, about 3 minutes, 215k cumulative subagent tokens (harness-reported).

```yaml
run_id: v5-upgrade-2026-09-17
piece_id: A
review_id: R4-consistency
comparison: { mode: nonblind-preference, order: "bar read first, then ours; round-1 candidate held as retained best" }
winner: ours
reason: All six round-1 contradictions are resolved in the text as claimed, C4 and C6 are unaffected or improved, but the exclusive wording of two fixes ("one exception", "only exits") introduces two small new conflicts with the stall-diagnosis section.
biggest_gap: execution-contract lists the lead's "only exits" from a judgment-only bar/none verdict at round 3+ while stall diagnosis offers a different bounded approach, a smaller slice, or a model fallback at the stall that such verdicts trigger.
biggest_gap_class: judgment
blocking_findings:
  - "N1 [judgment] 'with one exception: a light piece ...' vs SKILL and team-method listing user request as an escalation trigger"
  - "N2 [judgment] 'only exits' at round 3+ vs stall diagnosis's different bounded approach / smaller slice / model fallback"
advisory_findings:
  - "[judgment] SKILL 'no HOLD remains' vs contract's advisory HOLD; 'no blocking HOLD remains' would close it"
  - "[judgment] HOLD paragraph sentence order reads as if 'the lead prevents acceptance' applies to the advisory HOLD"
  - "[judgment] light escalation trigger: SKILL and template say 'returns bar or none'; contract and team-method add 'or fails a required check'"
  - "[deterministic] schema comments say 'third review' where the ladder defines the unit as a round"
  - "[judgment] candidate to experimental transition stated nowhere (pre-existing in v4)"
  - "[deterministic] unrequested ~60-word per-piece min() derivation; correct, changes no v4 behavior"
  - "[judgment] Route bullet lost the resume sentence; rule survives elsewhere; prominence loss"
checks:
  - { id: C4-scenario-probes, status: passed, evidence_class: judgment, observed: "unaffected, 6 of 6; P4 strengthened because promotion is now reachable" }
  - { id: C5-consistency, status: failed, evidence_class: judgment, observed: "6 of 6 round-1 contradictions resolved as claimed; 2 new minor conflicts N1, N2; 4 wording residues advisory" }
  - { id: C6-backward-compatibility, status: passed, evidence_class: deterministic, observed: "unchanged or improved: withheld_resume additive; unknown class for pre-5.0.0 records; v4 active lessons grandfathered; 8-review cap still soft 6 reserve 2" }
hold: { active: false, finding_ids: [] }
drift_vs_best: "+367 words vs round-1 candidate, all traceable to requested fixes except the ~60-word budget derivation; nothing vaguer; one prominence loss at the Route bullet"
next_action: "Two clause edits in execution-contract, then deliver without another full rejudge"
```

Lead disposition (round 3): N1 fixed ("with two exceptions: a user request, and a light piece whose single review does not accept ..."); N2 fixed (stall-diagnosis step listed among the exits). All seven advisories acted on: "no blocking HOLD remains"; HOLD sentence order; light trigger unified as "does not accept" with the contract and team method spelling out the cases; schema comments say "third review round"; candidate-to-experimental sentence added; per-piece derivation kept (R5 found it necessary and asked for a reserve fix); Route bullet restored with byte trims elsewhere. Targeted confirmation R6 requested on C5 only.
