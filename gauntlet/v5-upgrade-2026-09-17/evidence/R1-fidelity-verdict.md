# R1 verdict: research fidelity (round 1)

Critic: Agent tool subagent `critic-r1-fidelity`, fresh context, model self-reported `claude-fable-5-1`. Inputs: skill/ (research-basis.md read in full, other seven files regex-scanned), research/scan-2026-09-17/*.md, and the six arXiv abstract pages fetched by the critic itself. Candidate identity: research-basis.md SHA256 `88eda97c...1ad8` (see candidate-r1-sha256.txt). Returned 2026-09-17, about 4 minutes, 126k subagent tokens (harness-reported).

```yaml
run_id: v5-upgrade-2026-09-17
piece_id: A
review_id: R1-fidelity
winner: ours
reason: All six titles, arXiv IDs, submission dates, numeric figures and quoted phrases in research-basis.md and the six scan notes match the fetched abstracts; limits are stated per source; no file in skill/ claims v5 outperforms v4 or that any mechanism was measured.
biggest_gap: research-basis.md names no authors for any of the six v5 entries (file's existing convention); author lists appear only in the scan notes, where all six are correct and in order.
biggest_gap_class: deterministic
blocking_findings: []
advisory_findings:
  - "[deterministic] research-basis.md omits authors for all six v5 sources"
  - "[deterministic] scan 06 'verbatim' block substitutes 'PipeSwift' for the literal '\\name{}' on the arXiv page, unannotated"
  - "[judgment] 'a router trained offline on labeled outcomes' (research-basis, scan 02): 'offline' is an inference"
  - "[judgment] LIMBO limit 'needs a per-task reward': labeled ASSUMPTION in scan 03, unlabeled in research-basis"
  - "[judgment] scan 02 'with hidden unit tests' is an inference, unlabeled"
  - "[judgment] SKILL.md states the verifiability thesis as a flat principle; research-basis labels it the skill's inference"
  - "[judgment] scan 01 says sample size not known while its own table records 43/86"
checks:
  - { id: C3-research-fidelity, status: passed, evidence_class: external, observed: "6/6 titles, IDs, dates exact (PipeSwift v2 date also correct); all figures match; limits present for all six; superiority vocabulary only inside negations or disclaimers" }
hold: { active: false, finding_ids: [] }
next_action: "Deliverable as is; optional: add author lists to research-basis v5 entries; annotate the \\name{} expansion in scan 06."
```

Lead disposition (round 2): all seven advisories acted on. Authors added to the six v5 entries; `\name{}` expansion annotated in scan 06; "offline" removed from research-basis and labeled ASSUMPTION in scan 02; LIMBO limit rephrased as a statement about this skill; "hidden unit tests" labeled ASSUMPTION; scan 01 sentence corrected. The SKILL.md opening sentence stays as a design principle: it does not attribute the reading to any paper, and research-basis carries the hedge.
