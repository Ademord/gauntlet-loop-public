# R6 verdict: targeted consistency confirmation (round 3)

Critic: `critic-r2-probes` resumed for a targeted rejudge of the clauses changed since R4; model self-reported `claude-fable-5-1`. Candidate read: r3 (the two byte trims of r3b landed while the critic was reading; only SKILL.md changed by two words, see event E013). Returned 2026-09-17, about 2 minutes, 231k cumulative subagent tokens (harness-reported).

```yaml
run_id: v5-upgrade-2026-09-17
piece_id: A
review_id: R6-consistency
comparison: { mode: nonblind-preference, order: "R4 candidate held as retained best, then R6 regions" }
winner: ours
reason: N1 and N2 are fixed as claimed and the light trigger, HOLD order, schema comments, and per-piece reserve rule all read consistently, but the SKILL change to "no blocking HOLD" left two unchanged locations still requiring "no unresolved HOLD".
biggest_gap: software-quality.md SHIP rule and prompt-drafting.md template still withhold acceptance on any unresolved HOLD, while the contract says a round-3+ judgment HOLD cannot block and the HOLD disposition list gives it no dismissal path without counterevidence.
biggest_gap_class: judgment
blocking_findings:
  - "R1 [judgment, corroborated by two locations] 'no unresolved HOLD remains' (software-quality) and 'no unresolved HOLD' (prompt template) vs 'cannot block acceptance, including when raised as a HOLD' and 'no blocking HOLD remains'; fix: 'blocking' in both places; software-quality.md then stops being byte-identical to v4"
advisory_findings:
  - "[deterministic] budget formula degenerate cases: H=8 gives per-piece hard 6 and soft 6; H=1 gives per-piece hard 0 while the text says a single-review allowance supports one build and a final review"
  - "[judgment] template omits user request and de-escalation as topology-change triggers; the new 'semantic checklist, compress' sentence makes this an accepted simplification"
  - "[judgment] 'A self-report, recorded.' is a fragment; clear enough"
checks:
  - { id: C5-consistency, status: failed, evidence_class: judgment, observed: "N1 fixed; N2 fixed; light trigger identical in four places; HOLD order fixed; schema comments say 'third review round'; per-piece rule keeps the reserve; candidate-to-experimental defined; one residual HOLD-wording conflict" }
hold: { active: false, finding_ids: [] }
drift_vs_best: "+62 words vs R4; every addition traces to a requested fix; nothing vaguer; Route bullet and description net clearer"
next_action: "Replace 'unresolved HOLD' with 'blocking HOLD' in software-quality.md and prompt-drafting.md, then deliver; no further consistency round needed."
```

Lead disposition (round 3, after R6): the prescribed two-word fix applied in both files; the HOLD disposition list gained "recorded as advisory under the ladder" so an advisory HOLD has an explicit resolution; the budget sentence gained the H = 1 clause and a note that soft and hard may coincide under small caps. Lead verification: `grep -rn "unresolved HOLD" skill/` returns nothing; `validate_package.py` and `verify_archive.py` re-run on the final candidate. C5 is recorded as passed on the basis of R6 plus the lead's deterministic verification that the critic's prescribed fix is present; no critic re-read the package after these edits, and that is disclosed here and in the release review.
