# Source 2: Difficulty-Aware Topology Selection (DATS)

| Field | Value |
| --- | --- |
| arXiv | [2609.13890](https://arxiv.org/abs/2609.13890) |
| Title | Learning How Much to Collaborate: Difficulty-Aware Topology Selection for Multi-Agent Code Generation |
| Author | Yunsong Hong |
| Submitted | September 12, 2026 |
| Retrieved | 2026-09-17 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> Multi-agent systems for code generation are deployed with a single communication topology, chosen once for every problem. This is the wrong granularity. Evaluating five topologies on 614 problems from APPS, HumanEval+ and LiveCodeBench, we find that the advantage of hierarchical collaboration over a single agent grows from 2.4 points of pass@1 on the easiest third of problems to 21.1 points on the hardest third, while its token cost stays about ten times higher. We propose the Difficulty-Aware Topology Selector (DATS), which predicts each topology's probability of solving a problem and selects the one maximising predicted success minus cost. Its predictor is a graph network that treats the five topologies as nodes of a connectivity order rather than independent labels, worth 1.7 points over a flat multi-label head. Because the cost penalty is a single scalar recalibrable without retraining, routers compare at equal spend: under this budget-matched protocol six cost-aware methods span 21.6 percentage points, and two baselines leading DATS fall behind once calibrated to it. Fixed at 40% of the always-hierarchical cost, DATS reaches 77.7% pass@1 against 73.6% (always-hierarchical) and 74.3% (strongest learned competitor), all eleven pairwise McNemar comparisons surviving Holm-Bonferroni correction. The 4.1-point gain holds across four backbones spanning fourteen points of capability, and replacing the 39 interpretable features with a graph network or a pretrained encoder shifts accuracy by at most 1.3 points, never significantly. A cross-domain study on 400 mathematical reasoning problems reproduces the effect, the gap widening from 2.5 to 20.9 points.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| five topologies, 614 coding problems | "five topologies on 614 problems from APPS, HumanEval+ and LiveCodeBench" | matches |
| 2.4 points easiest third, 21.1 hardest third, ~10x tokens | same figures | matches |
| DATS estimates success and cost, selects per task | "predicts each topology's probability of solving a problem and selects the one maximising predicted success minus cost" | matches |
| at 40% of always-hierarchical cost: 77.7% vs 73.6% vs 74.3% | same figures | matches |
| replicated on 400 math problems | "400 mathematical reasoning problems ... 2.5 to 20.9 points" | matches |

## What the abstract does not establish

- The domain is competitive-programming style problems scored by pass@1 (ASSUMPTION: against unit tests, as is standard for these three benchmarks): every outcome is deterministically verifiable. The finding that hierarchy pays on hard problems is therefore a finding about hard *verifiable* problems, which is consistent with source 1's closing sentence rather than in tension with it.
- The router is trained on labeled outcomes from 39 interpretable problem features (ASSUMPTION: trained before deployment; the abstract says only that the cost penalty is "recalibrable without retraining"). Gauntlet has no labeled dataset and no ground-truth difficulty for real project tasks; a difficulty estimate made by the lead is a self-report that can be biased toward whatever saves budget.
- "Hierarchical collaboration" here is a multi-agent code-generation topology; it is not the same object as source 1's manager-with-revise-authority.
- Single author; only the abstract was read. ASSUMPTION: the paper defines the five topologies and the difficulty tiers in a way that would transfer to piece-level decomposition in Gauntlet.

## Where v4 already stands

v4: "Compact is the default ... Full team is optional: use it when the user requests team/full setup"; "A larger topology must solve a coordination need; role count is not agent count"; "Do not manufacture a testing campaign for low-impact edits"; stall diagnosis: "Do not lower the bar or spin up a larger team to avoid diagnosis." This is already a fixed-default, escalate-only-with-reason policy, which is the cheap end of what DATS shows.

## The gap

v4 never asks the lead to estimate difficulty or verifiability, never records why a topology was chosen, has no lighter shape than "build, separate critic, comparison against a bar" even for a one-function fix with an existing failing test, and its run log (`gauntlet/runs.jsonl`) does not record the features that a later router would need. The result is that the repository's own runs cannot ever answer the question DATS answers.

## Proposed v5 change (adapted, not copied)

1. The contract gains a `difficulty` block: an estimate (`low | medium | high`) with named observable proxies (scope, interacting components, verifiability class, novelty, prior failures) and a `verifiability` value (`deterministic | external | judgment`).
2. The topology decision is recorded with its reason: `light | compact | compact+delegates | team`.
3. `light` is defined: one bounded build, one independent evidence-based review against the failing original or behavior contract, no preference comparison, permitted only when difficulty is `low` and verifiability is `deterministic` or `external`. Independent acceptance is still required; light removes the comparison loop, not the reviewer.
4. Topology changes mid-run only at a recorded stall diagnosis or on user request; de-escalation is allowed when the remaining work is low difficulty. The reason is recorded either way.
5. The milestone record gains the observational tuple: difficulty proxies, verifiability, topology, reviews used, outcome, wall-clock. No router is built; the data accumulates from ordinary runs.

## Judgment on adoption

Adopt. The recording part costs a few lines per run and is the only way the repository can ever test the routing hypothesis on its own tasks. The `light` topology is the riskier part: it removes the comparison, so it is gated on verifiability and still requires a separate reviewer. The lead's difficulty self-report is a known weakness and is disclosed as such; the record exists so it can be checked against outcomes later.
