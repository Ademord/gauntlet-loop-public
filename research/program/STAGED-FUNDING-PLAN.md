# A staged funding case for Gauntlet

Superseded by the [50-milestone matrix](MILESTONES-50.md), following the [twenty-milestone roadmap](MILESTONES-20.md). The [current research/native-capability register](RESEARCH-NATIVE-50.md) distinguishes existing evidence, native host overlap, residual local uncertainty, reduced proposed allocation and deferred spending. Retained below as the original proposal; its $100 is not an approved or spent budget.

Proposal, 20 September 2026. This document authorizes no experiment, external outreach, or production release. Dollar allocations below are proposed metered experiment budgets, not quotes for the entire research effort.

The initial claim to investigate is narrow: **Can a small team get independently acceptable fixes to real Python tools with less total effort by adding Gauntlet?** Start with existing bug reports in document/workflow tools, across two repositories. Do not start with a claim about all agents, all software, or every artifact type.

The deliverable for an investor is a repeatable decision: what improved, compared with what, at what cost, for which work, and what the next tranche would resolve. A higher version number does not earn funding. The strongest tested configuration remains the incumbent, even if that is a normal coding agent.

## What the first tranche buys

Proposed envelope: one investigator workday and up to $100 in metered execution calls. Keep preparation and evaluation inside that time allowance. Record planning, solver, critic, judge, failed-run and infrastructure usage separately; mark unpriced categories unknown. Human time is a separate resource, not free. The previous calibration's $5.77 covered execution calls and diagnostics; it was not the full cost of conducting the study.

| Allocation | Work | Result required before proceeding |
| --- | --- | --- |
| Up to $10 | Compatibility checks and one excluded smoke task; validate that worker/subagent usage is fully counted | Actual V1 behavior can run under the shared external ceiling; graders reject plausible wrong fixes; a credible per-run quote exists |
| Up to $54 | Six real tasks, three end-to-end approaches, up to $3 reserved per run | Task-level quality, actual usage, time, regression and intervention records; one candidate may earn confirmation |
| Up to $36 | Six fresh tasks, the selected candidate versus its strongest simple control, up to $3 reserved per run | An untouched replication of the selected comparison, including losses and incomplete runs |

These are allocations, not a forecast that every task will fit. If meaningful tasks cannot run within the quote, stop and re-scope before the paid screen. Do not shorten tasks into artificial mutations, quietly raise caps, spend reserves on repeated failures, or weaken the baseline to make the plan fit. Backend limits can stop at request boundaries; account for observed overshoot and never describe an approximate CLI limit as an exact billing guarantee.

This is a screening and replication tranche, not a statistically powered demonstration. A successful tranche earns another bounded investigation. A wider performance claim needs a separately sized study on untouched tasks.

## First comparison: earn V1

Compare three independent end-to-end runs from identical starting source:

1. A capable coding agent using its normal workflow, including local tests and revisions.
2. The same agent explicitly asked to perform an additional self-check before delivery, inside the same total ceiling.
3. The actual V1-generated execution prompt, with its concrete reference, fresh critic and revision loop, inside that same ceiling.

Give every approach the same task requirements, reference access, tools, model/effort, environment, and external cost/time ceilings. Freeze the model identity and record actual usage: equal ceilings do not imply equal spending. Include V1 prompt-generation and subagent costs. Use a minimal documented adapter for host-specific commands; do not silently replace V1 with the recent one-review calibration, which tested a different intervention.

Choose tasks using eligibility rules and a fixed queue/order before inspecting model outcomes. Requirements must be clear enough to grade, dependencies available, and the work relevant to the selected users. Keep six confirmation tasks unseen by the implementation and prompt-tuning process. If eligible tasks are unavailable, report that supply constraint instead of inventing representative data.

Acceptance checks must be derived independently of solver output, cover the requested behavior and plausible regressions, and be exercised against both correct and broken examples. The solver gets its normal development tests; final checks stay outside the solver's context. Blind artifact labels for human judgment where practical. Critic approval is a recorded process event, not the primary outcome.

The primary outcome is an independently accepted task within the resource envelope. Also report actual cost per accepted task, including failed attempts, elapsed time, and human interventions/active review minutes when observed. If there are zero accepted tasks, cost per acceptance is undefined, not zero. Show paired task results so averages cannot hide regressions.

Proposed commercial screening bar, fixed before execution: either at least two net additional accepted tasks in the six-task screen without higher cost per accepted task, or at least 25% lower cost per accepted task with no fewer accepted tasks. Both routes require no new critical regression and no concealed increase in human repair work. These are discretionary investment hurdles, not statistical significance thresholds or universal standards. Confirmation must support the same selected benefit; switching to a different success metric after seeing confirmation fails that gate.

If results are equal and V1 costs more, keep the simpler approach for this workload and stop funding its default use here. If results are too uncertain, say so and explain what a further test would cost. Neither outcome proves V1 useless everywhere. If all tests pass, inspect grader adequacy before interpreting the ceiling; do not shop for harder tasks until V1 wins.

## How later versions compete for funding

Read the historical versions in order, but fund one relevant mechanism at a time. First use cheap targeted checks to establish that it behaves as intended. Only then spend on real tasks from the workload where the triggering condition occurs. A deliberately injected failure can test recovery behavior; it cannot establish how often that failure occurs in ordinary use.

| Source version | Candidate to test first, when relevant | Comparison and outcome that could earn adoption |
| --- | --- | --- |
| [V1](../../versions/v1/SKILL.md) | Fresh critique and revision against a real reference | Outperform capable normal work and extra self-checking on the measures above |
| [V2](../../versions/v2/references/team-method.md) | Evidence-backed shared findings and dissent/HOLD during interacting handoffs | Hold worker count/budget fixed; fewer incorrect final approvals without needless blocking of correct work. Fund a larger team separately only if parallel work is actually the bottleneck |
| [V3](../../versions/v3/SKILL.md) | Soft limits and parking when work stalls | Same overall budget; more verified completed obligations, accounting for valuable tasks abandoned too early. If stalls are absent, defer this test |
| [V4](../../versions/v4/SKILL.md) | Acceptance tied to the current artifact and evidence | Correctly reject stale passing evidence while accepting valid current evidence; confirm on actual delivery work. Test checkpoint recovery separately when interruptions are an observed problem |
| [V5](../../versions/v5/SKILL.md) | Selective effort: lightweight routing on easy, verifiable work | Reduce actual cost while preserving acceptance across a preselected mixed workload. Count escalation into the heavier route; this is a policy comparison, not review versus no review. Test the judgment-only revision limit separately only when third-review checkpoints naturally occur |
| [V5.1](../../skill/SKILL.md) | Restored examples and clarified instructions | A small task-setup/usability comparison only if users have trouble forming correct requests; no automatic full performance campaign |

Each feature competes against the earned incumbent, which includes the normal-agent control. Keep winning features only when their combined configuration also survives a bounded integration check. One-at-a-time wins do not prove that a bundle of them works well together. Discard or defer weak features; chronological completeness is not an investment objective.

The [archive](../../versions/README.md) documents material fidelity limits: V3 is missing four referenced files, forbids builder checks, and includes unmeasured model/vendor recommendations. Do not silently repair those facts and label the result historical V3. A test of an extracted V3 budget rule is an **incumbent-plus-feature test**, not proof that V3 beats V2. Complete package comparisons answer a separate product question and become worth funding after feature selection. Modern-model results are not evidence about how the packages performed when originally written.

## How the investor should judge the work

| Investor question | Evidence to demand from us |
| --- | --- |
| Whose recurring problem is this? | A specific user/task class, examples from actual work, and the existing alternative's cost |
| Did the method add value? | Strong controls, equal access and ceilings, externally checked artifacts, task-level wins and losses, and actual spending |
| Can the result survive scrutiny? | Frozen inputs, untouched confirmation work, usable logs, missing-data labels, and explanations of counterexamples |
| Was the investigation economical? | Total expenditure and time, including evaluation and unsuccessful work; one decision per tranche; a stated stopping condition |
| Will someone use or pay for it? | After technical screening, three prospective users trying their own tasks and evidence of voluntary reuse or a paid pilot. Interviews and praise alone do not establish demand |
| Could this become durable? | Evidence of an advantage that persists across tasks/model changes and a plausible distribution/business model. A copyable prompt or growing rulebook does not establish defensibility |
| What exactly does more funding buy? | One unresolved question, a bounded experiment, its cost, and the decision possible afterward |

Useful questions to ask the agent directly: **What would have made you stop? What did your approach lose? What costs are missing? Did you change the test after seeing the result? Why is this next experiment more valuable than the cheaper alternative?**

A research contribution and a startup are different funding cases. Reproducible evidence about when orchestration helps could be a worthwhile research result even if a simple agent wins much of the time. A venture case additionally needs demand, distribution, economics and a credible durable advantage. None of those commercial facts is established by our current repository.

This framing follows primary investor guidance on funding the next meaningful milestone and presenting customer pain, alternatives, business model and market opportunity: [Y Combinator's seed fundraising guide](https://www.ycombinator.com/blog/how-to-raise-a-seed-round/) and [Sequoia's business-plan guide](https://sequoiacap.com/article/writing-a-business-plan). The proposed experimental budgets and hurdles above are our planning choices, not recommendations or guarantees from those sources.

## Current investment decision

The [completed calibration](calibration/DECISION.md) funds confidence in the measurement infrastructure and exposes important grading weaknesses. It does not yet fund a claim that Gauntlet outperforms a capable agent. The next proposed purchase is the bounded V1 comparison above. Later-version experiments remain conditional on observed problems and earned evidence.
