# R5 verdict: prompt-mode redraft (round 2)

Critic: `critic-r3-prompt` resumed with instructions to re-read the three changed files from disk; model self-reported `claude-opus-5[1m]`. Candidate identity: r2 (SKILL.md 15,974 bytes, execution-contract.md 19,024 bytes, prompt-drafting.md 6,262 bytes as reported by the critic). Returned 2026-09-17, about 4 minutes, 141k cumulative subagent tokens (harness-reported).

Produced prompt (round 2): 449 words, no placeholders. It names the audience, states difficulty low with three proxies and deterministic verifiability, chooses light with the gate reason and the escalation rule, computes reserve ceil(20% of 8) = 2 with run soft point 6 and per-piece min(9, 8) = 8 hard and min(6, 6) = 6 soft, states that a review-only cap leaves request allowances at default, carries the third-review-round ladder, drift against the retained best, a resume validation decision with four outcomes, and excludes benchmark, model sweep, learning, and scheduled follow-up. The full prompt text is retained in the session transcript.

```yaml
run_id: v5-upgrade-2026-09-17
piece_id: A
review_id: R5-prompt-mode
winner: ours
reason: The revised skill yields a 449-word placeholder-free prompt carrying the ladder, the low/deterministic estimate, the light topology with its gate reason and the new escalation rule, the contract's 8-cap math, the review-only request default, and a resume validation decision, with no benchmark or learning.
biggest_gap: The per-piece hard limit min(9, H) does not subtract the integration reserve, so under an 8-review cap a single piece may consume all 8 reviews and starve the 2 reserved for integration and handoff.
biggest_gap_class: deterministic
blocking_findings: []
advisory_findings:
  - "RESOLVED (7): flat reserve sentence; compact-vs-light gate; light exit; per-piece limit above run cap; request scaling; two missing template slots; no listed include dropped this round"
  - "REMAINS: per-piece hard min(9, H) does not subtract the reserve"
  - "REMAINS [deterministic]: template 386 words with 11 brackets; faithful adaptation measured 518, reached 449 by a compression pass"
  - "REMAINS: route verbs both match 'make a prompt for: repair ...' (v4 inheritance)"
  - "REMAINS: winner: bar reads oddly for a repair (v4 inheritance)"
  - "NEW REGRESSION: Route bullet lost 'Record a resume validation decision before dispatch.'"
  - "NEW: vocabulary drift, schema comments and the include bullet still say 'third review' where the ladder counts rounds"
checks:
  - { id: C7-prompt-mode-forward-check, status: passed, evidence_class: deterministic, observed: "449 words; zero placeholders; ladder; estimate and topology with reason; reserve 2, soft 6, per-piece 8/6 per the revised contract; resume decision; no benchmark or learning; 1 word of headroom" }
hold: { active: false, finding_ids: [] }
next_action: "per-piece hard limit min(9, H minus the reserve); restore the Route bullet sentence; align 'review round' vocabulary; cut roughly 70 words from the template"
```

Lead disposition (round 3): per-piece hard limit changed to min(9, H minus the reserve) with soft min(6, that hard limit); Route bullet sentence restored (byte budget recovered from the description and item 6); schema comments and the include bullet now say "review round"; template trimmed by about 20 words and a sentence added that the template is a semantic checklist to compress, not prose to preserve. The template-length residual and the two v4 inheritances are recorded in the program backlog (B-009, B-012) rather than forced into this release; C7 passed on both rounds.
