# R3 verdict: prompt-mode forward check (round 1)

Critic: Agent tool subagent `critic-r3-prompt`, fresh context, model requested `opus`, self-reported `claude-opus-5[1m]`. Inputs: skill/ only (SKILL.md, prompt-drafting.md, execution-contract.md read in full; software-quality.md consulted). Forbidden from reading versions/, research/, gauntlet/. Task: draft the prompt for "repair the CSV import ... failing test exists ... local-only ... max 8 critic reviews ... learning off", then judge it against C7. Returned 2026-09-17, about 5 minutes, 109k subagent tokens (harness-reported).

Produced prompt: 449 words, no placeholders, difficulty low / deterministic, topology light with the gate reason, reserve ceil(0.2 * 8) = 2 with soft point 6, third-review advisory ladder, resume validation decision, benchmark and learning excluded. (Full text retained in the session transcript; not reproduced here because it was regenerated in round 2 against the revised template.)

```yaml
run_id: v5-upgrade-2026-09-17
piece_id: A
review_id: R3-prompt-mode
winner: ours
reason: The skill's draft route produced a 449-word, placeholder-free prompt carrying the ladder, the low/deterministic estimate with a reasoned light topology, the ceil(0.2*8)=2 reserve with a soft point of 6, a resume validation decision, and no benchmark or learning.
biggest_gap: The prompt-drafting template is 398 words before bracket expansion, so adapting it with the additions the same file mandates overshoots the 250-450 ceiling and forces the drafter to drop listed includes.
biggest_gap_class: deterministic
blocking_findings: []
advisory_findings:
  - "SKILL.md flat 'Reserve the final 6 run reviews' vs execution-contract ceil(0.2 * H): against an 8-cap SKILL.md alone yields reserve 6, contract yields 2"
  - "'Compact is the default' vs light gate 'only for'; nothing in SKILL.md says to prefer light when the gate passes"
  - "light has no exit: escalation needs a stall diagnosis defined as two repeated verdicts, unreachable with one review"
  - "per-piece 6/9 exceeds a run cap of 8; no rescaling rule"
  - "unclear whether a review-only cap scales the request allowance"
  - "template budget paragraph has no bracketed field yet must be rewritten for a user cap"
  - "Draft vs Execute route verbs both match 'make a gauntlet prompt for: repair ...'"
  - "winner: bar is awkward for a repair against a failing original"
  - "self-reported: audience implicit; 'inherit configured defaults' clause dropped to fit the ceiling"
checks:
  - { id: C7-prompt-mode-forward-check, status: passed, evidence_class: deterministic, observed: "449 words; zero placeholders; ladder, estimate/topology, 8-cap reserve 2 / soft 6, resume decision, no benchmark or learning; 1 word of headroom" }
hold: { active: false, finding_ids: [] }
next_action: "Point SKILL.md's reserve sentence at the H-scaled rule; define how light exits on none; cut the template to roughly 300 words with explicit slots for estimate, checks, and cap."
```

Lead disposition (round 2): reserve sentence in SKILL.md now says "or ceil(20%) of a smaller user cap"; light exit defined in SKILL.md, team-method, and execution-contract; per-piece limits capped at the run's remaining allowance with min() rule; review-only cap leaves request allowance at default, stated; template rewritten with explicit slots for difficulty/proxies/verifiability and for the budget cap (bracketed), shortened; "inherit configured models" kept in the template. Not acted on: Draft-vs-Execute route wording and `bar` semantics for repairs are v4 inheritances the critic resolved correctly; recorded in the thesis as deferred. Rejudge C7 on the revised template.
