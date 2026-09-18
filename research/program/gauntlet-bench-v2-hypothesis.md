# Gauntlet Bench v2: topology as a runtime decision

A research-program proposal, 17 September 2026. Status: proposed. Nothing in this file authorizes a benchmark, a paid model sweep, or a scheduled run. It states what question is worth asking, what the v5 skill already records toward answering it, how much data is needed before any inference is credible, and what a designed study would look like when separately authorized.

## 1. From "which arm wins" to "which arm is the cheapest that reliably solves this task"

The three archived research kits in the study archives kept in the private canonical repository framed Gauntlet Bench as a comparison of fixed arms (skill versions and harnesses) on a task ladder. That framing assumes one architecture is best across tasks. Two September 2026 results argue against the assumption from opposite sides:

- DATS (arXiv 2609.13890): on verifiable coding problems the advantage of hierarchical collaboration over a single agent grows from 2.4 to 21.1 pass@1 points from the easiest to the hardest third, at about ten times the cost; a per-problem selector at 40% of the always-hierarchical cost beats it.
- Loop-Back Authority (arXiv 2609.14767): on an open-ended writing task, giving a supervisor the power to force revisions lowered utility and clarity and cost 51.5% more tokens, with specification accuracy at ceiling either way.

If both hold, the useful object is not a winner but a frontier: for each task, the cheapest topology whose probability of accepted delivery within budget is high enough. The research question becomes whether that topology can be predicted from features known before the run starts.

## 2. Hypotheses

- H1 (verifiable difficulty gradient). For pieces whose required checks are `deterministic` or `external`, the difference in acceptance rate between heavier and lighter topologies increases with recorded difficulty.
- H2 (judgment saturation). For pieces whose comparison dimension is `judgment`, reviews beyond the second round do not raise acceptance or later-defect outcomes, and revisions after round two show more `drift_vs_best` findings than earlier ones.
- H3 (delayed memory utility). A lesson's utility ledger predicts whether its next retrieval is `prevented_defect` or `reduced_rounds` better than its admission-time review does.
- H4 (self-report drift). Leads' recorded difficulty estimates shift toward `low` over time when the `light` gate saves budget; the shift is detectable by comparing estimates against reviews actually used.

H4 is a threat to H1 and must be tested first.

## 3. Phase 0: observational record, zero extra cost

v5 already records, per run and piece: difficulty estimate and proxies; verifiability class; topology chosen and any change with reason; reviews used per piece and how many were advisory-only; outcome state; wall-clock; lessons retrieved with ledger outcomes (execution contract, milestone summary). Phase 0 is nothing more than keeping those records in each project's `gauntlet/runs.jsonl` and not editing them after the fact.

A deterministic script (no model calls) can aggregate across projects: counts per (difficulty, verifiability, topology) cell, reviews used, acceptance rate, advisory ratio, wall-clock. Its output is a table a person reads monthly. No inference is drawn from it until the volume in section 5 is reached.

## 4. Confounders and guards

- Self-selection: only runs that use the skill are recorded, and heavier topologies are chosen for tasks that look harder. Guard: record the estimate before the topology decision and never revise it; analyze within difficulty cells, not across.
- Self-report: the lead estimates difficulty. Guard: record proxies, not only the label; a later reviewer can re-estimate from proxies without seeing the label.
- Lead identity: the same agent builds and estimates. Guard: the estimate is part of the contract, which the independent critic sees and may dispute as a finding.
- Evaluator drift: critics may class findings inconsistently. Guard: sample verdict records and re-class blind; report agreement.
- Small numbers: see section 5.

## 5. Minimum volume before inference

With three difficulty levels, three verifiability classes, and four topologies there are 36 cells; most will be empty. A credible descriptive comparison needs on the order of 20 pieces per compared pair of cells, and acceptance is a coarse binary outcome. At the repository owner's current rate (ASSUMPTION: a few gauntlet runs per week across projects, each with one to four pieces) that is months of records for the two or three most common cells and never for the rest. Anything reported earlier is a table, not a finding.

## 6. Phase 1: proposals, human-gated

Once the table exists, an agent may read it and nominate workflow-improvement proposals under the existing process in the learning reference (source failure, hypothesis, intended effect, permitted files, patch, rollback). The table is evidence for the hypothesis field; it is not acceptance. A person approves each proposal. Model tokens: bounded, one reading per proposal cycle.

## 7. Phase 2: designed paired study, separately authorized

When a cell pair has enough volume to suggest a difference, the designed study is: a fixed task set drawn from real project tasks with known deterministic checks, each task run under two topologies (`light` or `compact` against `compact+delegates` or `team`) by the same builder model, with an independent critic per run and a held-out later-defect check. Outcomes: accepted within budget, reviews used, cost, later defects. Analysis: paired comparison per task within difficulty tier. This is the experiment the archived kits designed and never ran; it costs paid model calls and needs explicit authorization and a budget.

## 8. Phase 3: routing, only if phase 2 shows a gradient

Only after phase 2 shows H1 with a usable effect does a router make sense, and even then the first router is a lookup table over difficulty and verifiability, not a learned model. The skill's stance stays: no learned router is implied by v5.

## 9. Every task is an experiment (added 17 September 2026 after the owner's answer)

The owner answered the phase-2 gate question: willing to pay for paired runs where there is value. That changes the shape of phase 2 from a campaign into a standing budget. The large version of the idea:

- Exploration fraction. A fixed share of ordinary low-difficulty deterministic tasks (for example one in five, capped by a monthly token allowance) is run twice, once under the current default and once under the alternate arm of the flag currently under study. The second run costs money; the first run was going to happen anyway. Over months this yields the paired data phase 2 needs without a synthetic task suite, on tasks that matter to the owner.
- The flag under study rotates through the pre-registered list in `phase2-paired-study.md` (F1 light versus compact first, then F2 the ladder, then F3 critic shape), one at a time, until each reaches its planned 30 pairs or is stopped at a look.
- What the data buys: a default per task class chosen from measured pairs rather than from the skill author's judgment; later, a lookup-table router keyed on difficulty and verifiability (phase 3); later still, if there are enough cells, a contextual bandit that allocates the exploration fraction itself, which is the honest form of the "RL agent" in the owner's sketch.
- What stays fixed: the owner decides which flag is under study and approves every change to the skill; the critic never knows an arm is an experiment; the analysis is committed before the first pair; nothing in this loop can change the checks it is judged by.

Costs and the first concrete step are in `phase2-paired-study.md` and the harness under `tools/paired_study/`. The observational ledger under `ledger/` (phase 0) stays the denominator and the place where unrecorded runs are counted.

## 10. Relationship to the "self-improving SDLC" sketch

The repository owner's 17 September sketch (a tree of runs with per-feature usefulness deltas, an explorer that evaluates each enabled feature after each cycle, and an RL-style prioritizer) is phase 0 through phase 2 of this program with different words. The per-feature deltas are the aggregation table; the explorer is the phase-1 proposer; the RL prioritizer is phase 3 and premature until phase 2 exists. Two pitches on that sketch were commissioned from separate agents during the v5 run and are filed alongside this proposal when they arrive.
