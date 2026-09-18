# Source 1: Loop-Back Authority in LLM Agent Teams

| Field | Value |
| --- | --- |
| arXiv | [2609.14767](https://arxiv.org/abs/2609.14767) |
| Title | Loop-Back Authority in LLM Agent Teams: A Paired Experiment on Flat and Hierarchical Coordination |
| Authors | Burak Agachan, Max van Duijn, Amirhossein Zohrehvand |
| Submitted | September 13, 2026 |
| Retrieved | 2026-09-17 via arxiv.org/abs (abstract only; full text not read) |

## Abstract, verbatim

> Hierarchical orchestration, in which a Manager agent reviews worker output and can send it back for revision, is the default coordination pattern in production multi-agent LLM frameworks. Classical organizational theory predicts that the authority link speeds convergence on decisive output; work on sycophancy and Degeneration-of-Thought predicts that authoritative critique makes LLM output worse. Prior comparisons vary whole frameworks on tasks with checkable answers, leaving the authority link untested on open-ended work. We present a paired experiment that holds five LLM agents, their roles, prompts, tools, models, and data fixed and varies one link: whether the Manager may reject a worker's output and oblige a revision. Across 43 paired products and 86 runs of a business-intelligence reporting task, a five-model judge panel and a deterministic specification check score every report. The flat organization scores higher on Utility (d = 0.42, p = 0.009) and on Writing Clarity (d = 0.34, p = 0.030); the classical prediction fails. The reports are the same length, but hierarchical reports hedge 53% more, each revision loop is associated with a 0.14-point drop in Writing Clarity, and the hierarchical Writer's first draft is indistinguishable from the flat report: the gap opens inside the revision loop. Specification accuracy is at ceiling in both organizations, and the supervisory tier costs 51.5% more tokens for no quality gain. A supervisor pays for itself when it can verify and becomes a liability when it can only opine.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| five agents, prompts, models, tools, roles, task held constant; only revise authority varied | "holds five LLM agents, their roles, prompts, tools, models, and data fixed and varies one link" | matches |
| 43 paired outputs / 86 runs | "43 paired products and 86 runs" | matches |
| flat scored significantly higher on usefulness and writing clarity | Utility d = 0.42, p = 0.009; Writing Clarity d = 0.34, p = 0.030 | matches; effect sizes are small-to-medium |
| hierarchical hedged 53% more | "hedge 53% more" | matches |
| each revision loop correlated with another 0.14-point clarity loss | "each revision loop is associated with a 0.14-point drop in Writing Clarity" | matches; associational, not causal |
| supervisory tier consumed 51.5% more tokens | "costs 51.5% more tokens for no quality gain" | matches |
| both at ceiling on objectively checkable specification accuracy | "Specification accuracy is at ceiling in both organizations" | matches |

## What the abstract does not establish

- The task is one business-intelligence reporting task, an open-ended writing product. Nothing here is about code, and the authors say prior work with checkable answers is exactly what they are not testing.
- Utility and Writing Clarity are scored by a five-model judge panel. LLM judges can prefer confident prose; "hedging" may partly measure calibrated uncertainty that a human reader would want. The deterministic check is the only oracle-based measure, and it is at ceiling for both arms, so the experiment cannot show what a verifying supervisor does.
- "Each revision loop is associated with" is an association across runs, not a per-loop causal estimate.
- Only the abstract was read for this note. The counts are known (43 paired products, 86 runs); judge agreement, the distribution of revision-loop counts, and the hedging measure's definition are not. ASSUMPTION: the full paper reports them.

## Where v4 already stands

v4 already refuses to treat a critic's opinion as quality: "A critic's confidence, a longer process, or repeated agreement does not establish quality" (SKILL.md, opening); "Prefer observations that can reject a wrong answer" (delivery loop step 3); "Do not repeatedly sample critics until one approves" (step 5); "Retain the strongest verified candidate ... the newest version may regress" and the two-repeated-gap diagnosis heuristic (step 6).

## The gap

v4 gives the critic revision-forcing authority on any `biggest_gap` for up to 6/9 reviews per piece, with no distinction between a gap grounded in a discriminating observation and a gap that is the critic's taste. The paper's mechanism is exactly that link: the first draft was fine; the loop made it worse. v4 also has no instruction to look for the specific degradation the paper measured (qualifier creep, lost clarity) when comparing a revision against the best candidate, and does not raise the evidence requirement as rounds accumulate.

## Proposed v5 change (adapted, not copied)

1. Every finding carries an evidence class: `deterministic` (compiler, test, calculation, rendering), `external` (reference document, live behavior, source), or `judgment` (critic preference).
2. Evidence ladder per piece: in reviews 1 and 2 any class can be the biggest gap. From review 3 onward an uncorroborated `judgment` finding is advisory: it is recorded, it cannot force a revision, and it cannot block acceptance. Corroboration means a discriminating observation, or a second independent critic in an order-swapped comparison preferring the change.
3. Revision-drift check: the critic compares the revision against the retained best candidate on the comparison dimension and names drift (added hedging, lost clarity, scope creep) as a finding of class `judgment`. The lead keeps the best candidate; a loop that only reshuffles prose ends.
4. Cost disclosure: reviews are the price of supervision; the run record keeps the count so a later analysis can ask whether the later reviews changed anything.

## Judgment on adoption

Adopt as a rule change. The rule is cheap, reversible, and aligned with v4's existing stance. The paper does not prove it helps in Gauntlet's setting; the change is justified on the mechanism (opinion-driven loops have no stopping signal) more than on the effect size. Recorded as a hypothesis in the research basis.
