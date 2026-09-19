# Source 3: Reach or Solve? Attributing Agentic RL Gains with Checkpoint Handoffs

| Field | Value |
| --- | --- |
| arXiv | [2609.19636](https://arxiv.org/abs/2609.19636) |
| Title | Reach or Solve? Attributing Agentic RL Gains with Checkpoint Handoffs |
| Authors | Xuan Liu, Jingbin Qian |
| Submitted | September 17, 2026 |
| Retrieved | 2026-09-19 via arxiv.org/abs (abstract only; full text not read) |

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
