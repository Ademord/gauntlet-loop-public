# Lineage

This repository is a derivative of prior work and says so.

## The technique

The gauntlet loop is **Matt Shumer's** idea. He wrote the original prompt and named the technique while building [Claude of Duty](https://github.com/mshumer/Claude-of-Duty). The harsh critic, the blind comparison and the refusal to stop before the work wins all come from that prompt.

## v1, the skill (August 2026)

**Jay E at RoboNuggets** packaged the technique as a reusable Claude Code skill: [robonuggets/gauntlet-loop](https://github.com/robonuggets/gauntlet-loop), CC BY 4.0, commit `9b1975a` (6 Aug 2026). v1 established the parts every later version keeps: the bar must be named, fetchable and comparable; builder and critic are separate agents with fresh context; the verdict is binary; the exit is winning, never a round count; minimal instructions win. `versions/v1/SKILL.md` is that file, unmodified.

## v2, team, governance, delivery gates (early September 2026)

Franco Ribera's rewrite. Added: a team tier (two solvers, four whistleblower responsibilities, reference researcher, final reviewer); knowledge-admission, challenge and correction rules for shared memory; a HOLD route any critic can trigger; selectable software delivery gates (CI green on the reviewed commit, hosted demo, README with a real screenshot, regressions on real user journeys) with the states passed / failed / blocked / not selected / not applicable; a stopping record for resumable runs; a Codex-first portability section; and an optional, auditable agent-language experiment.

## v3, controls and evidence (9 September 2026)

Produced after a side-by-side reading of v2 against oh-my-pi's orchestration logic (`orchestrate` contract, `task` tool, `workflowz`, advisor) and feedback from a practitioner who runs OMP for one-shot phased refactors. Nothing in the method changed; what changed is control and evidence, most of it borrowed from OMP's mechanics and re-expressed as rules a prompt can carry: solo tier by default, team tier opt-in; a default per-piece budget with a soft wrap-up and a hard stop that parks the piece, never passes it; a fixed verdict record; verify-once at the lead; isolation for parallel builders; no silent model substitution; a run log.

## v4, evidence-based acceptance and continuity (12 September 2026)

Calibrated acceptance with a consistent `winner: none`; builder-local tests with independent acceptance; artifact, reference, and criteria identity binding; shared run budgets with an integration reserve; best-candidate retention and verdict checkpoints; optional environment-probed lessons; removal of speculative model rankings.

## v5, verifiability-conditional mechanisms (17 September 2026)

Six September 2026 papers, each read at abstract level and judged for transfer, produced evidence classes and a revision ladder, a recorded difficulty and topology decision with a `light` topology, a retrieval allowance and utility ledger, a resume validation record, and completion-time accounting. Produced by a gauntlet run on the skill itself; see `docs/thesis/v5-thesis.md` and `gauntlet/v5-upgrade-2026-09-17/`.

## What OMP contributed and what it did not

oh-my-pi ([can1357/oh-my-pi](https://github.com/can1357/oh-my-pi), MIT) is a harness, not a method. It has no bar, no blind A/B and no delivery gates; its exit criterion is "gates green", not "beats the reference". It does have routing, isolation, structured outputs, a deterministic loop and live supervision that no prompt can provide. v3 borrowed the shape of its controls.

## Attribution requirements

v1 is CC BY 4.0: any redistribution of later versions keeps this file and the credit lines in the README and LICENSE. OMP is MIT; nothing of its code is included here, only descriptions of its behaviour taken from its documentation.
