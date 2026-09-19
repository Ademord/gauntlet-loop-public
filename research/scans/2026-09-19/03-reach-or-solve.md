# Source 3: Reach or Solve? Attributing Agentic RL Gains with Checkpoint Handoffs

| Field | Value |
| --- | --- |
| arXiv | [2609.19636](https://arxiv.org/abs/2609.19636) |
| Title | Reach or Solve? Attributing Agentic RL Gains with Checkpoint Handoffs |
| Authors | Xuan Liu, Jingbin Qian |
| Submitted | September 17, 2026 |
| Retrieved | 2026-09-19 via arxiv.org/abs; full text (v1 HTML) read the same day |

## Abstract, verbatim

> Reinforcement learning now trains language-model agents that act over dozens of steps in live environments. The gains are large, and they are read as better decision-making. An agent in a closed loop writes its own inputs. Each observation follows from its own earlier actions, so the states it meets late in an episode are partly of its own making. An SFT checkpoint and an RL checkpoint are then scored from different states, even on identical tasks. Endpoint success mixes two changes: where the agent arrives, and what it does once it is there. Restricting the comparison to states both policies reach does not separate them. That restriction selects on an outcome, and in our data it flips the sign of the effect. We introduce checkpoint handoff, an evaluation protocol that clones a state one released checkpoint reached and hands it to another, with no retraining. Crossing a reacher role and a solver role over SFT and RL splits an endpoint gain into REACH and SOLVE. REACH is how often a policy arrives at a state the environment confirms is a fixed number of actions from success. SOLVE is how often it finishes from an identical cloned state. Across two benchmarks and two independently released pipelines, the reacher by solver interaction is positive in all five conditions. An RL history is worth more to an RL solver than the same history is to an SFT solver. On ALFWorld, RL improves both terms, and the SFT solver never succeeds where the RL solver fails. Independent REACH and SOLVE gaps predict the aggregate interaction. Handoff asks only that one checkpoint's history can be replayed under another, so long-horizon evaluation can report arrival and completion beside endpoint success.

## Scan claims checked against the abstract

| Scan claim | Abstract | Status |
| --- | --- | --- |
| an agent's late observations are partly produced by its own earlier actions | "Each observation follows from its own earlier actions, so the states it meets late in an episode are partly of its own making" | matches |
| submitted September 17, announced September 18 | arXiv submission date is September 17, 2026 | matches on submission |
| the protocol clones an intermediate state reached by one policy and lets another continue from that exact state | "clones a state one released checkpoint reached and hands it to another, with no retraining" | matches |
| across two benchmarks and two independently released pipelines, positive interactions between who created the history and who consumes it | "the reacher by solver interaction is positive in all five conditions" | matches |
| on ALFWorld, RL improved both reaching useful states and solving from them | "On ALFWorld, RL improves both terms" | matches |
| decomposes long-horizon capability into state construction and state exploitation without retraining | "splits an endpoint gain into REACH and SOLVE", "with no retraining" | matches |
| (not in the scan) | "Restricting the comparison to states both policies reach ... selects on an outcome, and in our data it flips the sign of the effect" | the strongest methodological warning in the abstract; the scan omits it |

## What the abstract does not establish

- The setting is reinforcement learning against supervised fine-tuning on agent benchmarks with clonable environment state. A software task in a repository has clonable state too, but the task distribution and the notion of "a fixed number of actions from success" do not transfer directly.
- No effect sizes appear in the abstract: "positive in all five conditions" gives a direction, not a magnitude.
- "The SFT solver never succeeds where the RL solver fails" is a statement about one benchmark.
- REACH depends on the environment confirming a state is a fixed number of actions from success. Most real repositories have no such oracle; a surrogate would have to be defined and is a judgment.
- ASSUMPTION: the five conditions are the crossings of two reachers with two solvers across the benchmarks; the abstract does not enumerate them.

## Full text, read 19 September 2026 (closes B-026 for this paper)

Read from the v1 HTML on arxiv.org. Quotations below are short and verbatim; everything else is paraphrase, and
anything inferred is labelled.

### What the abstract hid, and what it changes here

**1. There are two handoff variants, and the second one is the one this repository can use.** The frontier variant
needs an environment oracle: the solvable frontier is the set of states exactly D valid actions from success with
budget enough to reach it, "verified by enumeration" in ALFWorld's symbolic engine, with D = 2. The other variant,
used for TravelPlanner, has no such oracle. There the cut is taken from the recorded trajectory, "immediately
before its final model call", both solvers receive the same record and at most four model decisions, and the prefix
is replayed and checked for an identical reconstructed history. The previous note treated a surrogate for REACH as
a departure from the paper. It is not: where no oracle exists the paper itself cuts on a recorded-trajectory event
and bounds the continuation budget. That is precisely the shape available in a repository.

**2. The sign flip is quantified, and the authors limit their own claim.** On the 480-row ALFWorld matrix the
endpoint interaction is 24.2 points, 95% CI [13.3, 35.0]. The survivor-only estimand, which drops non-arrivals, is
-12.6 points, CI [-45.8, 22.7], and its paired difference from the endpoint interaction is -36.8 points, CI
[-68.6, -7.3]. The support loss behind the wide interval is stated: SFT reaches the frontier in 16 trajectories
from six tasks, RL in 99 from 28. The authors then say the diagnostic "was specified after its point estimates were
observed", so it "establishes neither a confirmatory effect nor a negative conditional interaction". The warning to
copy is the estimand rule, not the number: keep non-arrivals as failures.

**3. The estimand is a product, not a rate.** With the non-arrival state scored zero, the endpoint equals arrival
rate times conversion rate, J(W,R) = A_W x C_{W,R}. The reacher moves the first factor and the solver the second.
The interaction is then the difference of two products of an arrival rate and a same-state solve gap. This is worth
copying exactly, because it forces a report to say which factor moved.

**4. Identical inputs are verified, not assumed.** In the worked example the two handoff prompts "hash to the same
value". The prefix is replayed and the reconstructed history checked. This is a deterministic guard, cheap to
implement, and the local design did not have it.

**5. Solve decomposes further, and the decomposition is informative.** Every frontier state admits bridge actions,
first actions from which one more action wins. The SFT solver picks a bridge action on 72.2% of states and finishes
from one on 78.3% of those; the RL solver, 97.4% and 98.2%. Both stages contribute to the deficit, 25.2 and 19.9
points. A single conversion rate would have hidden that the weakness is split between choosing the right first move
and completing after it.

**6. The prediction test mostly fails at the level that matters.** Forecasting the interaction from independently
measured arrival and solve gaps lands 3.5 points from the observed 24.2 in aggregate, but the per-type residuals
run from +25.0 to -12.0 points and take both signs. The authors locate the error in the transport of the
within-type solve profile. Aggregate agreement with type-level disagreement is a familiar pattern and a reason not
to adopt the component model here.

**7. Non-arrival has failure modes, and they are dull.** An automatic audit labels every trajectory that never
arrived: for SFT, 102 of 104 are loops that repeat actions without changing the state. The RL-minus-SFT difference
in loop share is -12.4 points, CI [-28.6, 1.0], and the audit is called descriptive with no mechanism claim.

**8. Seeds are paired deliberately**, because seed choice alone is cited as moving reported agent performance by a
wide margin. A headless CLI run of a hosted model exposes no seed, so this repository cannot pair on it; that is a
limit of the local adaptation, recorded rather than papered over.

### Corrections to the earlier section "What the abstract does not establish"

| Earlier statement | After reading the full text |
| --- | --- |
| "No effect sizes appear in the abstract" | Effect sizes exist and are large: endpoint interaction 24.2 pp CI [13.3, 35.0] on ALFWorld unseen; seen-split replication 17.5 pp CI [6.7, 27.5]; frontier arrival +65.8 pp on the seen split |
| "a surrogate would have to be defined and is a judgment" | Still a judgment, but the paper supplies the precedent: its TravelPlanner arm cuts on a recorded-trajectory event with a fixed continuation budget and no oracle |
| ASSUMPTION: the five conditions are the crossings of two reachers with two solvers | Confirmed as three TravelPlanner scales (1.5B, 3B, 7B) plus two ALFWorld splits, each a full two-by-two crossing |

### What still does not transfer

- The population is language-model checkpoints from two training pipelines on two agent benchmarks. Nothing here is
  evidence about software-repair workflows, and no claim in this repository may cite it as such.
- ALFWorld's oracle comes from a symbolic engine that can enumerate admissible actions. A git repository cannot
  answer "how many actions from success is this state", so the frontier variant is unavailable, not merely harder.
- The component prediction test needs an independent sample of frontier states. This repository has no such sample
  and no cheap way to build one.

## Where the skill already stands

v5 checkpoints after every verdict with "Current and best candidate paths/identities; branches, patches, dirty work, and relevant executable state", and resumption validates that state before dispatch. The milestone record keeps reviews used, advisory counts, topology, difficulty, and outcome. The research program compares architectures by whether a task is accepted within budget.

## The gap

Every comparison the program can currently make is an endpoint comparison: did this arm get accepted, at what cost. When two arms differ, nothing says whether one was better at getting the work into a good state or better at finishing from one. The paired study inherits the exact confound the paper names, because each arm writes the state it later works from. The harness already snapshots state per arm, so the missing piece is the crossing, not the plumbing.

## Proposed change (adapted, not copied)

1. Add a milestone snapshot to the paired-study harness: after an arm's first accepted-or-rejected review round, commit the arm's worktree as a snapshot with its identity recorded.
2. Add a crossing run: hand arm A's snapshot to arm B's configuration and the reverse, with a continuation prompt that states the state is inherited and the contract unchanged.
3. Report two numbers beside acceptance: how often an arm's snapshot is one that any configuration can finish from, and how often a configuration finishes from a snapshot it did not create.
4. Keep it gated: the crossing doubles the runs per task, so it starts only after the first look at the plain comparison, on the tasks where the arms disagreed.

## Judgment on adoption

Adopt as a program design, not a skill change, and run it only after the first F1 look. This is the cleanest new experiment available to this repository, and it needs no new tasks: the same minted tasks work. The design is written up separately in [checkpoint-handoff.md](../../program/checkpoint-handoff.md). Falsifier for the design: if arms almost never produce different snapshots on low-difficulty deterministic tasks, the crossing measures nothing and belongs only on medium tasks. Backlog row: B-023.
