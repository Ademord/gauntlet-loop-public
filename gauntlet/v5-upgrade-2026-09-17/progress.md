# Progress: v5 upgrade run (2026-09-17)

Run `v5-upgrade-2026-09-17`, governed by skill 4.0.0, on branch `codex/v5-adaptive-evidence-2026-09-17` from `ce76d1b`. Contract: [contract.yaml](contract.yaml). Probes: [probes.md](probes.md). Events: [events.jsonl](events.jsonl). State: [state.yaml](state.yaml). Evidence: [evidence/](evidence/). Milestone line: [../runs.jsonl](../runs.jsonl).

## Outcome

Piece A (the v5 package) accepted after six independent critic reviews in three rounds plus deterministic checks. Piece B (research notes, thesis, program) accepted by the lead; the notes were checked within R1, the thesis was not independently reviewed. Piece C (tooling, release, provenance, docs) accepted on deterministic checks. Install and merge were not selected. No benchmark ran; no performance claim is made.

## Timeline

- 11:08Z Branch created; v4 package snapshotted to `versions/v4/` (diff identical).
- 11:05Z Six arXiv abstracts fetched and recorded verbatim in `research/scan-2026-09-17/`.
- 11:20Z Contract frozen (criteria v1, checks C1-C9, probes P1-P6). Difficulty: high. Topology: compact with parallel critics of distinct lenses.
- 11:40Z Candidate r1 built. 11:58Z self-checks: validator failed only C2 (size); round 1 dispatched on r1 in parallel with the known size failure.
- 12:03Z to 12:06Z Round 1 verdicts R1, R2, R3.
- 12:20Z Candidate r2: six C5 conflicts fixed, advisories acted on, template rewritten, reserve rule fixed, light exit defined; size trimmed to 15,974 bytes.
- 12:35Z Round 2 dispatched (R4, R5). Background pitch team started on the owner's self-improving SDLC sketch (scratchpad only).
- 12:45Z to 12:50Z Round 2 verdicts. 12:58Z candidate r3: N1/N2 clause repairs, per-piece reserve rule, Route sentence restored, round vocabulary. 13:05Z r3b: two-word byte trim.
- 13:12Z Round 3 targeted verdict R6. 13:20Z final: "blocking HOLD" in software-quality and template; advisory HOLD disposition; H = 1 budget clause. Deterministic checks re-run and passed.
- 13:25Z Acceptance recorded. Pitches filed with lead assessment and backlog. Docs, provenance, release artifacts written.

## Review ledger (run cap 24/30, per piece 6/9, reserve 6)

| Review | Piece | Round | Critic lens | Model (self-reported) | Winner | Biggest gap | Class | Run reviews used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A | 1 | research fidelity (C3) | claude-fable-5-1 | ours | authors absent from research-basis entries | deterministic | 1 |
| R2 | A | 1 | probes, consistency, compatibility (C4, C5, C6) | claude-fable-5-1 | ours, C5 failed | lesson activation deadlock | deterministic | 2 |
| R3 | A | 1 | prompt-mode forward check (C7) | claude-opus-5 | ours | template too long before expansion | deterministic | 3 |
| R4 | A | 2 | consistency rejudge (C4, C5, C6) | claude-fable-5-1 | ours, C5 failed | "only exits" vs stall options; "one exception" omits user request | judgment | 4 |
| R5 | A | 2 | prompt-mode redraft (C7) | claude-opus-5 | ours | per-piece hard limit could consume the reserve | deterministic | 5 |
| R6 | A | 3 | targeted consistency (C5) | claude-fable-5-1 | ours, C5 failed | "unresolved HOLD" wording in two files | judgment, corroborated | 6 |

Evidence ladder for this run: rounds 1 and 2 unrestricted; round 3 acted only on deterministic findings and on judgment findings corroborated by a second quoted location. After R6 the lead applied the prescribed fix and verified it deterministically; no critic re-read the package after that, which is disclosed in the release review.

## Check status (final candidate)

| Check | Status | Evidence |
| --- | --- | --- |
| C1 structure | passed | evidence/quick_validate-final.txt, evidence/validate_package-final.json |
| C2 size | passed | 15,989 <= 16,000; export 89,747 <= 90,000 |
| C3 research fidelity | passed (R1) | evidence/R1-fidelity-verdict.md |
| C4 scenario probes | passed (R2, R4) | evidence/R2-probes-verdict.md, evidence/R4-consistency-verdict.md |
| C5 consistency | passed (R6 + lead verification) | evidence/R6-consistency-verdict.md, grep none |
| C6 backward compatibility | passed (R2, R4) | as above |
| C7 prompt-mode | passed (R3, R5) | evidence/R3-prompt-mode-verdict.md, evidence/R5-prompt-mode-verdict.md |
| C8 tooling | passed | evidence/build_release-final.json, evidence/verify_archive-final.json |
| C9 export boundary | passed | validate_package forbidden-pattern scan |

## Open holds

None.

## Parked or blocked

Nothing parked. Install (backlog B-010) and merge are owner decisions. Push status is recorded in the events log once performed.
